# Importa as bibliotecas necessárias para o aplicativo Flask
from flask import Flask, render_template, redirect, url_for, flash, session, request, jsonify
from flask_mysqldb import MySQL  # Para conectar com o MySQL
from flask_wtf import FlaskForm  # Para formulários seguros com Flask-WTF
from wtforms import StringField, PasswordField, SubmitField  # Campos para o formulário
from wtforms.validators import DataRequired, Length  # Validações para os campos do formulário
import os  # Para manipulação do sistema operacional, como a geração de uma chave secreta
import bcrypt  # Para criptografar e verificar senhas
from functools import wraps  # Para criar decoradores personalizados
from cryptography.fernet import Fernet


b'0Ry0Np_T-51ZtqPtzyX0hcrpfcTCa-a15baaZjuiwEk=' 
# Inicializa o aplicativo Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Gera uma chave secreta aleatória para as sessões

fernet_key = b'0Ry0Np_T-51ZtqPtzyX0hcrpfcTCa-a15baaZjuiwEk='
cipher_suite = Fernet(fernet_key)


# Função para criptografar a senha do dispositivo
def encrypt_password(password):
    return cipher_suite.encrypt(password.encode())

# Função para descriptografar a senha do dispositivo
def decrypt_password(encrypted_password):
    return cipher_suite.decrypt(encrypted_password).decode()


# Configuração para conexão com o banco de dados MySQL
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "admin"
app.config['MYSQL_DB'] = "segura"

# Inicializa a conexão com o MySQL
mysql = MySQL(app)

# Classe de formulário para criar um novo usuário
class UserForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=4, max=25)])  # Campo de usuário com validações
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])  # Campo de senha com validações
    submit = SubmitField('Iniciar a Sessão')  # Botão de submissão do formulário

# Decorador para verificar se o usuário está logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:  # Verifica se o usuário está na sessão
            flash('Você precisa fazer login para acessar essa página.', 'danger')  # Mensagem se o usuário não estiver logado
            return redirect(url_for('login'))  # Redireciona para a página de login
        return f(*args, **kwargs)  # Executa a função se o usuário estiver logado
    return decorated_function

# Rota inicial que redireciona para o login
@app.route('/')
def home():
    return redirect(url_for('login'))

# Rota para login do usuário
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:  # Se o usuário já está logado, redireciona para o dashboard
        return redirect(url_for('dashboard'))
    
    form = UserForm()  # Cria o formulário
    if form.validate_on_submit():  # Se o formulário foi submetido e é válido
        username = form.username.data  # Captura o nome de usuário
        password = form.password.data  # Captura a senha
        
        # Executa a consulta para obter a senha armazenada no banco de dados
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT password FROM usuarios WHERE username = %s", (username,))
        bd_password = cursor.fetchone()  # Obtém o hash da senha do banco de dados
        cursor.close()
        
        if bd_password:  # Se o usuário foi encontrado
            senha_hashed = bd_password[0]  # Extrai o hash da senha
            print(f'Senha digitada: {password}')  # Exibe a senha para depuração (remover em produção)
            print(f'Senha hash armazenada: {senha_hashed}')  # Exibe o hash para depuração
            
            # Verifica se a senha fornecida corresponde ao hash
            if verificar_senha(password, senha_hashed):
                session['username'] = username  # Armazena o usuário na sessão
                return redirect(url_for('dashboard'))  # Redireciona para o dashboard
            else:
                flash('Senha incorreta!', 'danger')  # Exibe mensagem de erro para senha incorreta
        else:
            flash('Usuário não encontrado!', 'danger')  # Exibe mensagem de erro para usuário não encontrado
    
    return render_template('login.html', form=form)  # Renderiza a página de login com o formulário

# Rota para o dashboard, acessível apenas para usuários logados
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')  # Renderiza o dashboard


@app.route('/addmodel', methods=['GET', 'POST'])
@login_required
def add_model():
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        nome = data.get('nome')
        fabricante = data.get('fabricante')

        if not nome or not fabricante:
            return jsonify({"success": False, "message": "Todos os campos são obrigatórios."})

        try:
            # Verificação se o modelo já existe no banco de dados
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM modelo WHERE nome = %s", (nome,))
            existing_model = cursor.fetchone()
            
            if existing_model:
                cursor.close()
                return jsonify({"success": False, "message": "Esse modelo já existe."})

            # Inserção no banco de dados caso não exista
            cursor.execute("INSERT INTO modelo (nome, fabricante) VALUES (%s, %s)", (nome, fabricante))
            mysql.connection.commit()
            cursor.close()

            # Criar pasta com o nome do modelo
            base_dir = os.path.dirname(os.path.abspath(__file__))
            scripts_path = os.path.join(base_dir, 'scripts')
            modelo_path = os.path.join(scripts_path, nome)

            os.makedirs(modelo_path, exist_ok=True)

            return jsonify({"success": True, "message": "Modelo adicionado e pasta criada com sucesso!"})

        except Exception as e:
            return jsonify({"success": False, "message": f"Erro ao adicionar o modelo: {str(e)}"})

    # Renderiza o formulário HTML se o método for GET
    return render_template('addmodel.html')


# Rota para alterar modelos, acessível apenas para usuários logados


@app.route('/altermodel', methods=['GET', 'POST'])
@login_required
def alter_model():
    # Exibe a página de alteração de modelos
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id_modelo, nome, fabricante FROM modelo")
        modelos = cursor.fetchall()
        cursor.close()
        return render_template('altermodel.html', modelos=modelos)

    # Lida com a atualização do modelo via JSON
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        model_id = data.get('model_id')
        nome_modelo_novo = data.get('nome_modelo', '').strip()
        fabricante_modelo = data.get('fabricante_modelo', '').strip()

        # Verifica se os campos estão preenchidos
        if not nome_modelo_novo or not fabricante_modelo:
            return jsonify({"success": False, "message": "Todos os campos são obrigatórios."}), 400

        try:
            # Busca o nome antigo do modelo
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT nome FROM modelo WHERE id_modelo = %s", (model_id,))
            nome_modelo_antigo = cursor.fetchone()[0]
            cursor.close()

            # Atualiza o nome e o fabricante no banco de dados
            cursor = mysql.connection.cursor()
            cursor.execute("""
                UPDATE modelo 
                SET nome = %s, fabricante = %s 
                WHERE id_modelo = %s
            """, (nome_modelo_novo, fabricante_modelo, model_id))
            mysql.connection.commit()
            cursor.close()

            # Renomeia a pasta se o nome do modelo foi alterado
            base_dir = os.path.dirname(os.path.abspath(__file__))
            scripts_path = os.path.join(base_dir, 'scripts')
            pasta_antiga = os.path.join(scripts_path, nome_modelo_antigo)
            pasta_nova = os.path.join(scripts_path, nome_modelo_novo)

            # Verifica a existência da pasta e renomeia
            if nome_modelo_antigo != nome_modelo_novo and os.path.exists(pasta_antiga):
                os.rename(pasta_antiga, pasta_nova)

            return jsonify({"success": True, "message": "Modelo atualizado com sucesso!"})

        except Exception as e:
            return jsonify({"success": False, "message": f"Erro ao atualizar modelo: {str(e)}"}), 500

@app.route('/viewmodel')
@login_required
def view_model():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_modelo, nome, fabricante FROM modelo")  # Seleciona todos os modelos
    modelos = cursor.fetchall()
    cursor.close()
    return render_template('viewmodel.html', modelos=modelos)


@app.route('/adddevice', methods=['GET', 'POST'])
@login_required
def add_device():
    if request.method == 'POST' and request.is_json:
        # Recebe os dados do formulário em formato JSON
        data = request.get_json()
        nome = data.get('nome')
        id_modelo = data.get('modelo')
        mac_address = data.get('mac_address')
        id_grupo = data.get('grupo')
        ip = data.get('ip')
        access_type = data.get('access_type')
        username = data.get('username') if access_type == 'user_password' else None
        password = data.get('password')

        # Verifica se todos os campos obrigatórios estão preenchidos
        if not all([nome, mac_address, ip, password]) or (access_type == 'user_password' and not username):
            flash("Todos os campos obrigatórios devem ser preenchidos.", "danger")
            return redirect(url_for('add_device'))

        # Criptografa a senha com `Fernet` antes de armazená-la
        password_encrypted = encrypt_password(password)

        try:
            cursor = mysql.connection.cursor()

            # Insere o dispositivo com a senha criptografada
            if access_type == 'user_password':
                cursor.execute("""
                    INSERT INTO dispositivos (nome, id_modelo, mac_address, id_grupo, ip, access_type, username, password) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (nome, id_modelo, mac_address, id_grupo, ip, access_type, username, password_encrypted))
            else:
                cursor.execute("""
                    INSERT INTO dispositivos (nome, id_modelo, mac_address, id_grupo, ip, access_type, password) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (nome, id_modelo, mac_address, id_grupo, ip, access_type, password_encrypted))

            mysql.connection.commit()
            cursor.close()

            flash("Dispositivo adicionado com sucesso!", "success")
            return redirect(url_for('view_devices'))

        except Exception as e:
            flash(f"Erro ao adicionar o dispositivo: {str(e)}", "danger")
            return redirect(url_for('add_device'))

    # Método GET para exibir o formulário de cadastro de dispositivo
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_modelo, nome FROM modelo")
    modelos = cursor.fetchall()

    cursor.execute("SELECT id_grupo, nome FROM grupo")
    grupos = cursor.fetchall()
    cursor.close()

    return render_template('adddevice.html', modelos=modelos, grupos=grupos)

@app.route('/viewdevices')
@login_required
def view_devices():
    cursor = mysql.connection.cursor()
    
    # Seleciona todos os campos relevantes, incluindo `access_type` e `username`
    cursor.execute("""
        SELECT d.nome, m.nome AS modelo_nome, d.mac_address, g.nome AS grupo_nome, d.ip, 
               d.access_type, d.username
        FROM dispositivos d
        JOIN modelo m ON d.id_modelo = m.id_modelo
        JOIN grupo g ON d.id_grupo = g.id_grupo
    """)
    dispositivos = cursor.fetchall()
    cursor.close()
    
    # Cada dispositivo será um dicionário para fácil acesso aos dados no template
    dispositivos_data = [
        {
            "nome": dispositivo[0],
            "modelo_nome": dispositivo[1],
            "mac_address": dispositivo[2],
            "grupo_nome": dispositivo[3],
            "ip": dispositivo[4],
            "access_type": dispositivo[5],
            "username": dispositivo[6] if dispositivo[5] == "user_password" else None
        }
        for dispositivo in dispositivos
    ]
    
    return render_template('viewdevice.html', dispositivos=dispositivos_data)


@app.route('/alterdevices', methods=['GET', 'POST'])
def alter_devices():
    if request.method == 'POST':
        # Recebe os dados enviados via AJAX para atualizar um dispositivo
        data = request.get_json()
        id_dispositivo = data.get("id_dispositivo")
        nome = data.get("nome")
        id_modelo = data.get("id_modelo")
        mac_address = data.get("mac_address")
        id_grupo = data.get("id_grupo")
        ip = data.get("ip")
        access_type = data.get("access_type")
        username = data.get("username")
        password = data.get("password")  # Senha opcional para atualização

        try:
            cursor = mysql.connection.cursor()

            # Se a senha foi enviada, cria um hash e atualiza a senha
            if password:
                password_hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                cursor.execute(""" 
                    UPDATE dispositivos
                    SET nome = %s, id_modelo = %s, mac_address = %s, id_grupo = %s, ip = %s, 
                        access_type = %s, username = %s, password = %s
                    WHERE id_dispositivo = %s
                """, (nome, id_modelo, mac_address, id_grupo, ip, access_type, username, password_hashed, id_dispositivo))
            else:
                # Atualiza sem alterar a senha
                cursor.execute(""" 
                    UPDATE dispositivos
                    SET nome = %s, id_modelo = %s, mac_address = %s, id_grupo = %s, ip = %s, 
                        access_type = %s, username = %s
                    WHERE id_dispositivo = %s
                """, (nome, id_modelo, mac_address, id_grupo, ip, access_type, username, id_dispositivo))

            mysql.connection.commit()
            cursor.close()

            return jsonify({"success": True, "message": "Dispositivo atualizado com sucesso."}), 200
        
        except Exception as e:
            return jsonify({"success": False, "message": f"Erro ao atualizar dispositivo: {str(e)}"}), 500

    else:
        # Verifica se um ID específico foi solicitado para obter detalhes de um dispositivo
        device_id = request.args.get('id_dispositivo')
        
        if device_id:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT d.id_dispositivo, d.nome, m.id_modelo, m.nome AS modelo_nome, 
                       d.mac_address, g.id_grupo, g.nome AS grupo_nome, d.ip, d.access_type, d.username
                FROM dispositivos d
                JOIN modelo m ON d.id_modelo = m.id_modelo
                JOIN grupo g ON d.id_grupo = g.id_grupo
                WHERE d.id_dispositivo = %s
            """, (device_id,))
            device = cursor.fetchone()
            cursor.close()

            if device:
                device_data = {
                    "id_dispositivo": device[0],
                    "nome": device[1],
                    "id_modelo": device[2],
                    "modelo_nome": device[3],
                    "mac_address": device[4],
                    "id_grupo": device[5],
                    "grupo_nome": device[6],
                    "ip": device[7],
                    "access_type": device[8],
                    "username": device[9]
                }
                return jsonify(device_data)
            else:
                return jsonify({"message": "Dispositivo não encontrado"}), 404
        else:
            # Busca todos os dispositivos, modelos, e grupos para exibição na tabela
            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT d.id_dispositivo, d.nome, m.nome AS modelo_nome, d.mac_address, g.nome AS grupo_nome, 
                       d.ip, d.access_type, d.username
                FROM dispositivos d
                JOIN modelo m ON d.id_modelo = m.id_modelo
                JOIN grupo g ON d.id_grupo = g.id_grupo
            """)
            dispositivos = cursor.fetchall()

            cursor.execute("SELECT id_modelo AS id, nome FROM modelo")
            modelos = cursor.fetchall()
            
            cursor.execute("SELECT id_grupo AS id, nome FROM grupo")
            grupos = cursor.fetchall()

            cursor.close()

            dispositivos_data = [
                {
                    "id_dispositivo": dispositivo[0],
                    "nome": dispositivo[1],
                    "modelo_nome": dispositivo[2],
                    "mac_address": dispositivo[3],
                    "grupo_nome": dispositivo[4],
                    "ip": dispositivo[5],
                    "access_type": dispositivo[6],
                    "username": dispositivo[7]
                }
                for dispositivo in dispositivos
            ]

            modelos_data = [{"id": modelo[0], "nome": modelo[1]} for modelo in modelos]
            grupos_data = [{"id": grupo[0], "nome": grupo[1]} for grupo in grupos]

            return render_template('alterdevice.html', dispositivos=dispositivos_data, modelos=modelos_data, grupos=grupos_data)



@app.route('/deletedevice', methods=['GET', 'POST'])
@login_required
def delete_devices():
    # Se for uma requisição POST, o usuário deseja excluir um dispositivo
    if request.method == 'POST':
        id_dispositivo = request.json.get('id_dispositivo')  # Pegando o ID do dispositivo do JSON
        print("ID do dispositivo recebido para exclusão:", id_dispositivo)  # Log do ID recebido

        if not id_dispositivo:
            return jsonify({"success": False, "message": "ID do dispositivo não fornecido."}), 400

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM dispositivos WHERE id_dispositivo = %s", (id_dispositivo,))
            mysql.connection.commit()
            cursor.close()
            print("Dispositivo excluído com sucesso.")  # Log de sucesso
            return jsonify({"success": True, "message": "Dispositivo excluído com sucesso."})
        except Exception as e:
            cursor.close()
            print(f"Erro ao excluir dispositivo {id_dispositivo}: {str(e)}")  # Log de erro
            return jsonify({"success": False, "message": f"Erro ao excluir dispositivo: {str(e)}"}), 500

    # Se for uma requisição GET, o usuário deseja visualizar a lista de dispositivos
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT d.id_dispositivo, d.nome, m.nome AS modelo_nome, d.mac_address, g.nome AS grupo_nome, d.ip, 
               d.access_type, d.username, d.password
        FROM dispositivos d
        JOIN modelo m ON d.id_modelo = m.id_modelo
        JOIN grupo g ON d.id_grupo = g.id_grupo
    """)
    dispositivos = cursor.fetchall()
    cursor.close()

    # Formatando os dispositivos em uma estrutura de dicionário
    dispositivos = [
        {
            "id_dispositivo": dispositivo[0],
            "nome": dispositivo[1],
            "modelo_nome": dispositivo[2],
            "mac_address": dispositivo[3],
            "grupo_nome": dispositivo[4],
            "ip": dispositivo[5],
            "access_type": dispositivo[6],
            "username": dispositivo[7],
            "password": dispositivo[8]
        }
        for dispositivo in dispositivos
    ]

    return render_template('deletedevice.html', dispositivos=dispositivos)





@app.route('/createuser', methods=['GET', 'POST'])
@login_required
def create_user():
    form = UserForm()  # Cria o formulário de usuário
    if request.method == 'POST' and request.is_json:  # Se a requisição é POST e JSON
        data = request.get_json()
        username = data.get('username')  # Obtém o nome de usuário
        password = data.get('password')  # Obtém a senha

        if username and password:  # Verifica se ambos os campos foram preenchidos
            password_hashed = hash_senha(password)  # Gera o hash da senha
            
            try:
                # Insere o novo usuário no banco de dados
                cursor = mysql.connection.cursor()
                cursor.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", (username, password_hashed))
                mysql.connection.commit()
                cursor.close()
                
                # Retorna um JSON com sucesso
                return jsonify({"success": True, "message": "Usuário criado com sucesso!"})
            except Exception as e:
                return jsonify({"success": False, "message": f"Erro ao criar usuário: {str(e)}"})
        else:
            return jsonify({"success": False, "message": "Todos os campos são obrigatórios."})

    return render_template('createuser.html', form=form)  # Renderiza a página para criar usuários

# Função para gerar o hash de uma senha
def hash_senha(senha):
    salt = bcrypt.gensalt()  # Gera um "salt"
    senha_hashed = bcrypt.hashpw(senha.encode(), salt)  # Cria o hash da senha
    return senha_hashed.decode('utf-8')  # Retorna o hash como string

# Função para verificar se uma senha corresponde ao hash
def verificar_senha(senha, senha_hashed):
    return bcrypt.checkpw(senha.encode(), senha_hashed.encode())  # Compara a senha com o hash

# Rota para logout do usuário
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove o usuário da sessão
    flash('Você foi deslogado com sucesso!', 'success')  # Exibe mensagem de sucesso
    return redirect(url_for('login'))  # Redireciona para a página de login

# Rota para alterar usuários, acessível apenas para usuários logados
@app.route('/alterarusuarios', methods=['GET', 'POST'])
@login_required
def alterar_usuarios():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios")  # Seleciona todos os usuários
    usuarios = cursor.fetchall()  # Retorna todos os usuários
    cursor.close()

    if request.method == 'POST':  # Se a requisição é POST
        user_id = request.form.get('user_id')  # Obtém o ID do usuário
        nova_senha = request.form.get('nova_senha')  # Obtém a nova senha
        confirmar_senha = request.form.get('confirmar_senha')  # Obtém a confirmação da senha

        # Verifica se as senhas são iguais e possuem comprimento mínimo
        if nova_senha != confirmar_senha:
            flash("As senhas não coincidem. Por favor, tente novamente.", "danger")
        elif len(nova_senha) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.", "danger")
        else:
            try:
                nova_senha_hashed = hash_senha(nova_senha)  # Gera o hash da nova senha
                cursor = mysql.connection.cursor()
                cursor.execute("UPDATE usuarios SET password = %s WHERE id = %s", (nova_senha_hashed, user_id))
                mysql.connection.commit()
                cursor.close()
                
                flash("Senha do usuário alterada com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao alterar senha: {str(e)}", "danger")

    return render_template('alterarusuarios.html', usuarios=usuarios)  # Renderiza a página de alteração

# Rota para visualizar usuários
@app.route('/visualizarusuarios')
@login_required
def visualizar_usuarios():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios")  # Seleciona todos os usuários
    usuarios = cursor.fetchall()
    cursor.close()
    return render_template('visualizarusuarios.html', usuarios=usuarios)

# Rota para deletar usuários
@app.route('/deletarusuarios', methods=['GET', 'POST'])
@login_required
def deletar_usuarios():
    if request.method == 'POST':
        # Recebe o ID do usuário enviado por uma requisição AJAX para exclusão
        user_id = request.json.get('id')  # Assumindo que o ID do usuário vem no corpo JSON

        if user_id:
            try:
                cursor = mysql.connection.cursor()
                cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
                mysql.connection.commit()
                cursor.close()
                return jsonify({"success": True, "message": "Usuário excluído com sucesso."})
            except Exception as e:
                print(f"Erro ao excluir usuário {user_id}: {str(e)}")
                return jsonify({"success": False, "message": f"Erro ao excluir usuário: {str(e)}"}), 500
        else:
            return jsonify({"success": False, "message": "ID do usuário não fornecido."}), 400
    else:
        # Método GET para listar os usuários
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, username FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()

        # Converte os dados para uma estrutura de dicionário para facilitar o uso no template
        usuarios = [{"id": usuario[0], "username": usuario[1]} for usuario in usuarios]

        return render_template('deletarusuarios.html', usuarios=usuarios)


@app.route('/deletemodel', methods=['GET', 'POST'])
@login_required
def deletemodel():
    # Conectar ao banco de dados e obter todos os modelos
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_modelo, nome FROM modelo")  # Assumindo que 'nome' representa o nome da pasta
    modelos = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':  # Se a requisição é POST
        modelos_para_deletar = request.form.getlist('modelos_para_deletar')  # Obtém os IDs dos modelos selecionados

        if modelos_para_deletar:  # Se algum modelo foi selecionado
            try:
                cursor = mysql.connection.cursor()
                for modelo_id in modelos_para_deletar:
                    # Obter o nome do modelo (usado para o nome da pasta)
                    cursor.execute("SELECT nome FROM modelo WHERE id_modelo = %s", (modelo_id,))
                    modelo_nome = cursor.fetchone()

                    if modelo_nome:
                        modelo_folder = os.path.join('scripts', modelo_nome[0])  # Caminho da pasta do modelo

                        # Remover a pasta e seus arquivos
                        if os.path.exists(modelo_folder):
                            for root, dirs, files in os.walk(modelo_folder, topdown=False):
                                for file in files:
                                    os.remove(os.path.join(root, file))
                                for dir in dirs:
                                    os.rmdir(os.path.join(root, dir))
                            os.rmdir(modelo_folder)

                    # Deletar o registro do modelo no banco de dados
                    cursor.execute("DELETE FROM modelo WHERE id_modelo = %s", (modelo_id,))

                mysql.connection.commit()
                cursor.close()

                flash('Modelos excluídos com sucesso!', 'success')
                return redirect(url_for('deletemodel'))
            except Exception as e:
                flash(f'Erro ao excluir modelo: {str(e)}', 'danger')

    return render_template('deletemodel.html', modelos=modelos)

@app.route('/creategroup', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        nome_grupo = data.get('nome')

        # Verifica se o campo nome_grupo foi preenchido
        if not nome_grupo:
            return jsonify({"success": False, "message": "O nome do grupo é obrigatório."})

        try:
            # Conecta ao banco de dados e insere o novo grupo
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO grupo (nome) VALUES (%s)", (nome_grupo,))
            mysql.connection.commit()
            cursor.close()

            return jsonify({"success": True, "message": "Grupo criado com sucesso!"})
        except Exception as e:
            return jsonify({"success": False, "message": f"Erro ao criar o grupo: {str(e)}"})

    # Renderiza o formulário HTML se o método for GET
    return render_template('creategroup.html')

# Rota para deletar grupos
# Rota para carregar e deletar grupos
@app.route('/deletegroup', methods=['GET', 'POST'])
@login_required
def delete_group():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM grupo")
    grupos = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        grupos_para_deletar = request.json.get('grupos_para_deletar')

        if not grupos_para_deletar:
            return jsonify({"success": False, "message": "Nenhum grupo selecionado para exclusão."}), 400

        grupos_com_dispositivos = []
        dispositivos_por_grupo = {}

        cursor = mysql.connection.cursor()
        for grupo_id in grupos_para_deletar:
            cursor.execute("SELECT d.nome FROM dispositivos d WHERE d.id_grupo = %s", (grupo_id,))
            dispositivos = cursor.fetchall()

            if dispositivos:
                grupos_com_dispositivos.append(grupo_id)
                dispositivos_por_grupo[grupo_id] = [dispositivo[0] for dispositivo in dispositivos]

        if grupos_com_dispositivos:
            error_message = "Existem dispositivos associados aos grupos selecionados. Desassocie os dispositivos antes de continuar."
            for grupo_id in grupos_com_dispositivos:
                nome_grupo = next((grupo[1] for grupo in grupos if grupo[0] == grupo_id), "Dispositivos encontrados")
                dispositivos = ", ".join(dispositivos_por_grupo[grupo_id])
                error_message += f"<br><strong>{nome_grupo}:</strong> {dispositivos}"
            cursor.close()
            return jsonify({"success": False, "message": error_message}), 400

        # Deletar grupos sem dispositivos associados
        try:
            for grupo_id in grupos_para_deletar:
                cursor.execute("DELETE FROM grupo WHERE id_grupo = %s", (grupo_id,))
            mysql.connection.commit()
            cursor.close()
            return jsonify({"success": True, "message": "Grupos excluídos com sucesso!"})
        except Exception as e:
            print(f"Erro ao excluir grupos: {str(e)}")
            cursor.close()
            return jsonify({"success": False, "message": f"Erro ao excluir grupos: {str(e)}"}), 500

    return render_template('deletegroup.html', grupos=grupos)






# Rota para gerenciar dispositivos
@app.route('/managerdevices', methods=['GET', 'POST'])
def manager_devices():
    if request.method == 'POST':
        # Filtragem de dispositivos por grupo usando AJAX
        group_id = request.json.get('group_id')  # Recebe o `group_id` via JSON no corpo da requisição
        
        cursor = mysql.connection.cursor()
        # Filtra os dispositivos pelo grupo especificado, ou retorna todos se `group_id` estiver vazio
        if group_id:
            cursor.execute("""
                SELECT d.id_dispositivo, d.nome, m.nome AS modelo_nome, g.nome AS grupo_nome, d.mac_address, d.ip 
                FROM dispositivos d
                LEFT JOIN modelo m ON d.id_modelo = m.id_modelo
                LEFT JOIN grupo g ON d.id_grupo = g.id_grupo
                WHERE d.id_grupo = %s
            """, (group_id,))
        else:
            cursor.execute("""
                SELECT d.id_dispositivo, d.nome, m.nome AS modelo_nome, g.nome AS grupo_nome, d.mac_address, d.ip 
                FROM dispositivos d
                LEFT JOIN modelo m ON d.id_modelo = m.id_modelo
                LEFT JOIN grupo g ON d.id_grupo = g.id_grupo
            """)
        
        dispositivos = cursor.fetchall()
        cursor.close()
        
        # Formata os dispositivos para o formato JSON
        dispositivos_list = [
            {
                "id_dispositivo": dispositivo[0],
                "nome": dispositivo[1],
                "modelo_nome": dispositivo[2],
                "grupo_nome": dispositivo[3],
                "mac_address": dispositivo[4],
                "ip": dispositivo[5]
            }
            for dispositivo in dispositivos
        ]

        # Retorna a lista de dispositivos filtrados como JSON
        return jsonify({"devices": dispositivos_list})

    # Método GET para carregar a página de gerenciamento com todos os grupos e dispositivos
    cursor = mysql.connection.cursor()

    # Carregar todos os grupos
    cursor.execute("SELECT id_grupo, nome FROM grupo")
    grupos = cursor.fetchall()

    # Carregar todos os dispositivos
    cursor.execute("""
        SELECT d.id_dispositivo, d.nome, m.nome AS modelo_nome, g.nome AS grupo_nome, d.mac_address, d.ip 
        FROM dispositivos d
        LEFT JOIN modelo m ON d.id_modelo = m.id_modelo
        LEFT JOIN grupo g ON d.id_grupo = g.id_grupo
    """)
    dispositivos = cursor.fetchall()
    cursor.close()

    # Renderiza o template com todos os dispositivos e grupos para o carregamento inicial
    return render_template('managerdevices.html', dispositivos=dispositivos, grupos=grupos)

#Rota para upload de scripts
@app.route('/uploadscript', methods=['GET', 'POST'])
@login_required
def upload_script():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_path = os.path.join(base_dir, 'scripts')

    # Busca os modelos que têm pastas existentes
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_modelo, nome FROM modelo")
    modelos = cursor.fetchall()
    cursor.close()

    # Adiciona o caminho da pasta associada a cada modelo
    modelos_com_pasta = [
        {"id": modelo[0], "nome": modelo[1], "folder_path": os.path.join(scripts_path, modelo[1])}
        for modelo in modelos
        if os.path.exists(os.path.join(scripts_path, modelo[1]))
    ]

    if request.method == 'POST':
        router_model_id = request.form['router_model_id']
        script_files = request.files.getlist('script_file')  # Recebe múltiplos arquivos

        # Obter o nome do modelo e verificar a existência da pasta
        modelo_nome = next((modelo['nome'] for modelo in modelos_com_pasta if str(modelo['id']) == router_model_id), None)

        if not modelo_nome:
            flash("Erro: A pasta do modelo selecionado não existe.", "danger")
            return redirect(url_for('upload_script'))

        upload_folder = os.path.join(scripts_path, modelo_nome)

        # Salva cada arquivo se ele for .py e a pasta do modelo existir
        for script_file in script_files:
            if script_file.filename.endswith('.py'):  # Verifica se o arquivo é .py
                if os.path.isdir(upload_folder):
                    script_file.save(os.path.join(upload_folder, script_file.filename))
                else:
                    flash("Erro: A pasta para o modelo selecionado não está disponível.", "danger")
                    return redirect(url_for('upload_script'))
            else:
                flash(f"O arquivo {script_file.filename} não é um arquivo Python (.py).", "danger")
                return redirect(url_for('upload_script'))

        flash("Scripts carregados com sucesso!", "success")
        return redirect(url_for('upload_script'))

    return render_template('upload_script.html', router_models=modelos_com_pasta)




# Tratamento de erro 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Executa o servidor se o script for executado diretamente
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
