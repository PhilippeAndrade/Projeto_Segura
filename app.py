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
import logging, sys
from datetime import timedelta
import subprocess
from flask import Flask, Response, stream_with_context


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

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16 MB para upload de arquivos
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=2)  # Sessão de login válida por 2 horas
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30) 

# Configuração de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def create_admin_user():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", ("admin",))
        
        # Se o usuário "admin" não existe, crie-o
        if not cursor.fetchone():
            admin_password = hash_senha("admin")
            cursor.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", ("admin", admin_password))
            mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Erro ao tentar criar o usuário admin: {str(e)}")

# Classe de formulário para criar um novo usuário
class UserForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=4, max=25)])  # Campo de usuário com validações
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=5)])  # Campo de senha com validações
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


# Rota para adicionar um dispositivo
@app.route('/adddevice', methods=['GET', 'POST'])
@login_required
def add_device():
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        nome = data.get('nome')
        id_modelo = data.get('id_modelo')
        mac_address = data.get('mac_address')
        id_grupo = data.get('id_grupo')
        ip = data.get('ip')
        access_type = data.get('access_type')
        username = data.get('username') if access_type == 'user_password' else None
        password = data.get('password')

        # Verifica se campos obrigatórios estão preenchidos
        if not all([nome, id_modelo, mac_address, id_grupo, ip, password]):
            return jsonify({"success": False, "message": "Preencha todos os campos obrigatórios."}), 400

        # Criptografa a senha
        password_encrypted = encrypt_password(password)

        try:
            cursor = mysql.connection.cursor()

            # Insere o dispositivo com a senha criptografada
            query = """
                INSERT INTO dispositivos (nome, id_modelo, mac_address, id_grupo, ip, access_type, username, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (nome, id_modelo, mac_address, id_grupo, ip, access_type, username, password_encrypted))
            mysql.connection.commit()
            cursor.close()

            return jsonify({"success": True, "message": "Dispositivo adicionado com sucesso!"}), 200

        except Exception as e:
            return jsonify({"success": False, "message": f"Erro ao adicionar o dispositivo: {str(e)}"}), 500

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


# Rota para alterar dispositivos
@app.route('/alterdevices', methods=['GET', 'POST'])
@login_required
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

            # Se a senha foi enviada, criptografa a senha e atualiza o dispositivo
            if password:
                password_encrypted = encrypt_password(password)
                cursor.execute(""" 
                    UPDATE dispositivos
                    SET nome = %s, id_modelo = %s, mac_address = %s, id_grupo = %s, ip = %s, 
                        access_type = %s, username = %s, password = %s
                    WHERE id_dispositivo = %s
                """, (nome, id_modelo, mac_address, id_grupo, ip, access_type, username, password_encrypted, id_dispositivo))
            else:
                # Atualiza o dispositivo sem alterar a senha
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
                       d.mac_address, g.id_grupo, g.nome AS grupo_nome, d.ip, d.access_type, d.username, d.password
                FROM dispositivos d
                JOIN modelo m ON d.id_modelo = m.id_modelo
                JOIN grupo g ON d.id_grupo = g.id_grupo
                WHERE d.id_dispositivo = %s
            """, (device_id,))
            device = cursor.fetchone()
            cursor.close()

            if device:
                # Descriptografa a senha para enviar ao frontend
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
                    "username": device[9],
                    "password": decrypt_password(device[10]) if device[10] else None
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
    # Conectar ao banco de dados e obter todos os usuários
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios")  # Seleciona todos os usuários
    usuarios = cursor.fetchall()  # Retorna todos os usuários
    cursor.close()

    if request.method == 'POST':  # Verifica se a requisição é POST para alterar senha
        user_id = request.form.get('user_id')  # Obtém o ID do usuário do formulário
        nova_senha = request.form.get('nova_senha')  # Obtém a nova senha
        confirmar_senha = request.form.get('confirmar_senha')  # Obtém a confirmação da senha

        # Verifica se as senhas coincidem e têm pelo menos 6 caracteres
        if nova_senha != confirmar_senha:
            flash("As senhas não coincidem. Por favor, tente novamente.", "danger alterar_usuario")
        elif len(nova_senha) < 5:
            flash("A senha deve ter pelo menos 5 caracteres.", "danger alterar_usuario")
        else:
            try:
                # Gera o hash da nova senha com bcrypt para salvar no banco de dados
                nova_senha_hashed = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())
                cursor = mysql.connection.cursor()
                cursor.execute("UPDATE usuarios SET password = %s WHERE id = %s", (nova_senha_hashed, user_id))
                mysql.connection.commit()
                cursor.close()

                # Mensagem de sucesso
                flash("Senha alterada com sucesso!", "success alterar_usuario")
                return redirect(url_for('alterar_usuarios'))
            except Exception as e:
                flash(f"Erro ao alterar senha: {str(e)}", "danger alterar_usuario")

    return render_template('alterarusuarios.html', usuarios=usuarios)

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
def delete_model():
    # Carregar todos os modelos
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_modelo, nome FROM modelo")
    modelos = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        data = request.get_json()
        modelo_id = data.get('id_modelo')

        if not modelo_id:
            return jsonify({"success": False, "message": "ID do modelo não fornecido."}), 400

        try:
            cursor = mysql.connection.cursor()

            # Verificar se o modelo tem dispositivos associados
            cursor.execute("SELECT COUNT(*) FROM dispositivos WHERE id_modelo = %s", (modelo_id,))
            dispositivos_count = cursor.fetchone()[0]
            if dispositivos_count > 0:
                return jsonify({"success": False, "message": "Modelo possui dispositivos associados e não pode ser excluído."}), 400

            # Obter o nome do modelo para exclusão da pasta e os scripts associados
            cursor.execute("SELECT nome FROM modelo WHERE id_modelo = %s", (modelo_id,))
            modelo_nome = cursor.fetchone()

            if modelo_nome:
                modelo_folder = os.path.join('scripts', modelo_nome[0])

                # Obter os scripts associados ao modelo
                cursor.execute("SELECT id_script, nome FROM Scripts WHERE id_modelo = %s", (modelo_id,))
                scripts = cursor.fetchall()

                # Para cada script, deletar os parâmetros associados e o script
                for script_id, script_name in scripts:
                    # Excluir parâmetros associados ao script
                    cursor.execute("DELETE FROM Parametros_scripts WHERE id_script = %s", (script_id,))
                    
                    # Excluir o registro do script no banco de dados
                    cursor.execute("DELETE FROM Scripts WHERE id_script = %s", (script_id,))

                    # Deletar o arquivo de script do sistema de arquivos, se existir
                    script_file_path = os.path.join(modelo_folder, script_name)
                    if os.path.isfile(script_file_path):
                        os.remove(script_file_path)

                # Excluir a pasta do modelo se ainda existir após a exclusão dos arquivos
                if os.path.exists(modelo_folder):
                    os.rmdir(modelo_folder)

            # Deleta o registro do modelo no banco de dados
            cursor.execute("DELETE FROM modelo WHERE id_modelo = %s", (modelo_id,))
            mysql.connection.commit()
            cursor.close()

            return jsonify({"success": True, "message": "Modelo e scripts associados excluídos com sucesso!"}), 200
        except Exception as e:
            return jsonify({"success": False, "message": f"Erro ao excluir modelo: {str(e)}"}), 500

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


@app.route('/managergroups', methods=['GET', 'POST'])
@login_required
def manager_groups():
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        group_id = request.json.get('group_id')

        # Define a consulta base para dispositivos
        if group_id:  # Se um grupo foi selecionado, filtra por ele
            query = """
                SELECT d.id_dispositivo, d.nome, m.nome AS modelo_nome, g.nome AS grupo_nome, d.mac_address, d.ip 
                FROM dispositivos d
                LEFT JOIN modelo m ON d.id_modelo = m.id_modelo
                LEFT JOIN grupo g ON d.id_grupo = g.id_grupo
                WHERE d.id_grupo = %s
            """
            cursor.execute(query, (group_id,))
        else:  # Se nenhum grupo foi selecionado, traga todos os dispositivos
            query = """
                SELECT d.id_dispositivo, d.nome, m.nome AS modelo_nome, g.nome AS grupo_nome, d.mac_address, d.ip 
                FROM dispositivos d
                LEFT JOIN modelo m ON d.id_modelo = m.id_modelo
                LEFT JOIN grupo g ON d.id_grupo = g.id_grupo
            """
            cursor.execute(query)

        dispositivos = cursor.fetchall()
        cursor.close()

        # Formata os dispositivos para o formato JSON
        dispositivos_list = [
            {
                "id_dispositivo": dispositivo[0],
                "nome": dispositivo[1],
                "modelo_nome": dispositivo[2] if dispositivo[2] else "N/A",
                "grupo_nome": dispositivo[3] if dispositivo[3] else "N/A",
                "mac_address": dispositivo[4],
                "ip": dispositivo[5]
            }
            for dispositivo in dispositivos
        ]

        return jsonify({"devices": dispositivos_list})

    # Método GET para carregar a página de gerenciamento com todos os grupos e dispositivos
    cursor.execute("SELECT id_grupo, nome FROM grupo")
    grupos = cursor.fetchall()

    cursor.execute("""
        SELECT d.id_dispositivo, d.nome, m.nome AS modelo_nome, g.nome AS grupo_nome, d.mac_address, d.ip 
        FROM dispositivos d
        LEFT JOIN modelo m ON d.id_modelo = m.id_modelo
        LEFT JOIN grupo g ON d.id_grupo = g.id_grupo
    """)
    dispositivos = cursor.fetchall()
    cursor.close()

    # Renderiza o template com todos os dispositivos e grupos para o carregamento inicial
    return render_template('managergroups.html', dispositivos=dispositivos, grupos=grupos)






@app.route('/get-scripts/<string:model_name>/<int:device_id>', methods=['GET'])
def get_scripts(model_name, device_id):
    cursor = mysql.connection.cursor()

    try:
        # Carregar os scripts associados ao modelo, incluindo a descrição do script
        cursor.execute("""
            SELECT s.id_script, s.nome, s.descricao 
            FROM Scripts s
            JOIN modelo m ON s.id_modelo = m.id_modelo
            WHERE m.nome = %s
        """, (model_name,))
        scripts = cursor.fetchall()

        if not scripts:
            return jsonify({"message": "Nenhum script encontrado para o modelo."}), 404

        # Carregar informações do dispositivo
        cursor.execute("""
            SELECT ip, username, password, access_type 
            FROM dispositivos 
            WHERE id_dispositivo = %s
        """, (device_id,))
        device_data = cursor.fetchone()

        if not device_data:
            return jsonify({"message": "Dispositivo não encontrado."}), 404

        ip, username, password_criptografada, access_type = device_data

        # Descriptografar a senha
        senha = cipher_suite.decrypt(password_criptografada.encode()).decode()

        # Preparar lista de scripts com parâmetros e suas descrições
        scripts_list = []
        for script_id, script_name, descricao_script in scripts:
            # Carregar parâmetros associados ao script, incluindo a descrição de cada parâmetro
            cursor.execute("""
                SELECT nome_parametro, descricao_parametro 
                FROM Parametros_scripts 
                WHERE id_script = %s
            """, (script_id,))
            parametros = cursor.fetchall()
            
            # Adicionar o script com seus parâmetros e descrições
            scripts_list.append({
                "script_id": script_id,
                "script_name": script_name,
                "descricao_script": descricao_script,  # Adiciona a descrição do script
                "parametros": [
                    {
                        "nome_parametro": param[0],
                        "descricao_parametro": param[1]
                    }
                    for param in parametros
                ]
            })

        # Estrutura de dados a ser enviada ao cliente
        response_data = {
            "scripts": scripts_list,
            "ip": ip,
            "senha": senha,
            "access_type": access_type
        }
        if access_type == 'user_password':
            response_data["username"] = username

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"message": "Erro ao carregar scripts e dados do dispositivo", "error": str(e)}), 500

    finally:
        cursor.close()


@app.route('/execute-script/<string:model_name>/<int:device_id>/<string:script_name>', methods=['POST'])
def execute_script(model_name, device_id, script_name):
    try:
        # Obtém os dados da requisição
        data = request.json
        if not data:
            return jsonify({"message": "Requisição deve conter um corpo JSON válido."}), 400

        ip = data.get("ip")
        if not ip:
            return jsonify({"message": "O campo 'ip' é obrigatório."}), 400

        # Busca credenciais do dispositivo
        cursor = mysql.connection.cursor()
        query = """
            SELECT username, password, access_type
            FROM dispositivos
            WHERE id_dispositivo = %s
        """
        cursor.execute(query, (device_id,))
        device_data = cursor.fetchone()

        if not device_data:
            return jsonify({"message": "Dispositivo não encontrado."}), 404

        username, password_encrypted, access_type = device_data
        senha = cipher_suite.decrypt(password_encrypted.encode()).decode() if password_encrypted else None

        # Construção do caminho do script
        base_dir = os.path.dirname(__file__)
        script_path = os.path.join(base_dir, 'scripts', model_name, script_name)
        if not os.path.isfile(script_path):
            logging.error(f"Script não encontrado: {script_path}")
            return jsonify({"message": "Script não encontrado.", "path": script_path}), 404

        # Monta o comando base do script
        comando_script = [sys.executable, script_path, '--ip', ip]

        if access_type == 'user_password':
            comando_script += ['--username', username, '--password', senha]
        elif access_type == 'password_only':
            comando_script += ['--password', senha]

        # Adiciona outros parâmetros enviados pelo cliente
        parametros = data.get("parametros", {})
        for param, value in parametros.items():
            comando_script += [f"--{param}", str(value)]

        logging.info(f"Executando comando: {' '.join(comando_script)}")
        
        # Executa o script e captura stdout/stderr
        resultado_execucao = subprocess.run(
            comando_script,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=os.environ.copy()
        )

        # Logs detalhados para análise
        stdout = resultado_execucao.stdout.strip()
        stderr = resultado_execucao.stderr.strip()
        if resultado_execucao.returncode != 0:
            logging.error(f"Erro na execução do script: {stderr}")
            return jsonify({
                "output": stdout,
                "error": stderr,
                "command_executed": ' '.join(comando_script),
                "message": "Erro na execução do script."
            }), 500
        logging.info(f"stdout: {resultado_execucao.stdout.strip()}")
        logging.error(f"stderr: {resultado_execucao.stderr.strip()}")  

        # Processa a saída do script
        if not stdout:
            return jsonify({"message": "Erro: Saída do script vazia."}), 500


        # Verifica se há credenciais novas na saída
        new_username = None
        new_password = None
        if "NEW_CREDENTIALS" in stdout:
                credentials_part = stdout.split("NEW_CREDENTIALS")[1].strip()
                credentials = dict(item.split("=") for item in credentials_part.split(","))
                new_username = credentials.get("username")
                new_password = credentials.get("password")

        # Atualiza as credenciais no banco
        if new_password:
            try:
                encrypted_password = cipher_suite.encrypt(new_password.encode()).decode()
                update_query = """
                    UPDATE dispositivos
                    SET username = %s, password = %s
                    WHERE id_dispositivo = %s
                """
                cursor.execute(update_query, (new_username or username, encrypted_password, device_id))
                mysql.connection.commit()
            except Exception as e:
                logging.error(f"Erro ao atualizar credenciais no banco: {e}")
                return jsonify({"message": "Erro ao atualizar credenciais no banco.", "error": str(e)}), 500

        return jsonify({
            "output": stdout,
            "error": None,
            "command_executed": ' '.join(comando_script),
            "message": "Script executado com sucesso."
        })

    except Exception as e:
        logging.exception("Erro inesperado ao tentar executar o script.")
        return jsonify({"message": "Erro inesperado ao tentar executar o script.", "error": str(e)}), 500


# Rota para gerenciar dispositivos
@app.route('/managerdevices', methods=['GET', 'POST'])
@login_required
def manager_devices():
    if request.method == 'POST':
        # Recebe o `group_id` e `nome_dispositivo` via JSON no corpo da requisição
        group_id = request.json.get('group_id')
        nome_dispositivo = request.json.get('nome_dispositivo')

        cursor = mysql.connection.cursor()

        # Define a consulta base
        query = """
            SELECT d.id_dispositivo, d.nome, m.nome AS modelo_nome, g.nome AS grupo_nome, d.mac_address, d.ip 
            FROM dispositivos d
            LEFT JOIN modelo m ON d.id_modelo = m.id_modelo
            LEFT JOIN grupo g ON d.id_grupo = g.id_grupo
            WHERE 1=1
        """
        params = []

        # Filtra pelo grupo, se especificado
        if group_id:
            query += " AND d.id_grupo = %s"
            params.append(group_id)

        # Filtra pelo nome do dispositivo, se especificado
        if nome_dispositivo:
            query += " AND d.nome LIKE %s"
            params.append(f"%{nome_dispositivo}%")

        # Executa a consulta com os parâmetros
        cursor.execute(query, tuple(params))
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
    os.makedirs(scripts_path, exist_ok=True)  # Certifique-se de que a pasta 'scripts' existe

    # Busca os modelos e verifica se têm pastas existentes
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT id_modelo, nome FROM modelo")
        modelos = cursor.fetchall()
    finally:
        cursor.close()

    modelos_com_pasta = [
        {"id": modelo[0], "nome": modelo[1], "folder_path": os.path.join(scripts_path, modelo[1])}
        for modelo in modelos
    ]

    if request.method == 'POST':
        router_model_id = request.form.get('router_model_id')
        script_files = request.files.getlist('script_file')
        parametros = request.form.getlist('parameters[]')
        descricoes = request.form.getlist('descriptions[]')  # Captura as descrições dos parâmetros
        script_description = request.form.get('script_description')  # Captura a descrição do script

        # Verifica se o modelo existe em modelos_com_pasta e cria a pasta se necessário
        modelo_info = next((modelo for modelo in modelos_com_pasta if str(modelo['id']) == router_model_id), None)
        if not modelo_info:
            flash("Erro: Modelo não encontrado.", "danger upload_script")
            return redirect(url_for('upload_script'))

        upload_folder = modelo_info['folder_path']
        os.makedirs(upload_folder, exist_ok=True)

        # Processa cada arquivo de script
        for script_file in script_files:
            if not script_file.filename.endswith('.py'):
                flash(f"O arquivo {script_file.filename} não é um arquivo Python (.py).", "danger upload_script")
                continue

            cursor = mysql.connection.cursor()
            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM Scripts WHERE nome = %s AND id_modelo = %s",
                    (script_file.filename, router_model_id)
                )
                file_exists = cursor.fetchone()[0] > 0

                if file_exists:
                    flash(f"O arquivo {script_file.filename} já existe para este modelo.", "warning upload_script")
                    continue

                script_file_path = os.path.join(upload_folder, script_file.filename)
                if os.path.exists(script_file_path):
                    flash(f"O arquivo {script_file.filename} já existe na pasta e será sobrescrito.", "info upload_script")

                script_file.save(script_file_path)

                # Insere informações do script no banco de dados, incluindo a descrição
                cursor.execute(
                    "INSERT INTO Scripts (nome, descricao, id_modelo) VALUES (%s, %s, %s)",
                    (script_file.filename, script_description, router_model_id)
                )
                id_script = cursor.lastrowid

                # Adiciona os parâmetros e suas descrições relacionadas ao script
                for parametro, descricao in zip(parametros, descricoes):
                    cursor.execute(
                        "INSERT INTO Parametros_scripts (id_script, nome_parametro, descricao_parametro) VALUES (%s, %s, %s)",
                        (id_script, parametro, descricao)
                    )
                mysql.connection.commit()

            except Exception as e:
                mysql.connection.rollback()
                flash(f"Erro ao carregar o script {script_file.filename}: {e}", "danger upload_script")
                return redirect(url_for('upload_script'))

            finally:
                cursor.close()

        flash("Scripts e parâmetros carregados com sucesso!", "success upload_script")
        return redirect(url_for('upload_script'))

    return render_template('upload_script.html', router_models=modelos_com_pasta)


@app.route('/deletescript', methods=['GET', 'POST'])
def delete_script():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_path = os.path.join(base_dir, 'scripts')

    if request.method == 'POST':
        script_id = request.json.get('script_id')
        if not script_id:
            return jsonify({'success': False, 'message': 'ID do script não fornecido.'}), 400

        cursor = mysql.connection.cursor()
        try:
            # Buscar detalhes do script no banco de dados
            cursor.execute("SELECT nome, id_modelo FROM scripts WHERE id_script = %s", (script_id,))
            script_info = cursor.fetchone()
            if not script_info:
                return jsonify({'success': False, 'message': 'Script não encontrado.'}), 404

            script_name, model_id = script_info

            # Remover o arquivo do sistema de arquivos
            cursor.execute("SELECT nome FROM modelo WHERE id_modelo = %s", (model_id,))
            model_name = cursor.fetchone()[0]
            if model_name:
                script_file_path = os.path.join(scripts_path, model_name, script_name)
                if os.path.exists(script_file_path):
                    os.remove(script_file_path)

            # Deletar script e parâmetros do banco de dados
            cursor.execute("DELETE FROM parametros_scripts WHERE id_script = %s", (script_id,))
            cursor.execute("DELETE FROM scripts WHERE id_script = %s", (script_id,))
            mysql.connection.commit()

            return jsonify({'success': True, 'message': f"Script '{script_name}' excluído com sucesso."}), 200
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({'success': False, 'message': f"Erro ao excluir o script: {str(e)}"}), 500
        finally:
            cursor.close()

    # Listar todos os scripts com parâmetros agrupados
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            SELECT s.id_script, s.nome AS script_name, s.descricao AS script_description, 
                   m.nome AS model_name, 
                   GROUP_CONCAT(p.nome_parametro ORDER BY p.nome_parametro SEPARATOR ', ') AS parametros
            FROM scripts s
            JOIN modelo m ON s.id_modelo = m.id_modelo
            LEFT JOIN parametros_scripts p ON s.id_script = p.id_script
            GROUP BY s.id_script, m.nome
            ORDER BY m.nome, s.nome
        """)
        scripts = cursor.fetchall()
    finally:
        cursor.close()

    # Transformar os dados em uma estrutura utilizável pelo template
    agrupados = {}
    for script in scripts:
        model_name = script[3]
        if model_name not in agrupados:
            agrupados[model_name] = {'nome_modelo': model_name, 'scripts': []}
        agrupados[model_name]['scripts'].append({
            'id': script[0],
            'nome': script[1],
            'descricao': script[2],
            'parametros': script[4] if script[4] else 'Nenhum parâmetro'
        })

    return render_template('delete_script.html', agrupados=agrupados.values(), modelos=[(m[0], m[1]) for m in agrupados])






@app.route('/execute-group-scripts', methods=['POST'])
@login_required
def execute_group_scripts():
    try:
        data = request.json
        group_data = data.get('groupData', [])
        if not group_data:
            return jsonify({"error": "Nenhum dado fornecido para execução."}), 400

        def generate_logs():
            for group in group_data:
                model_id = group.get("modelId")
                script_id = group.get("scriptId")
                use_credentials = group.get("useCredentials", False)
                parameters = group.get("parameters", {})

                # Buscar informações do script e do modelo
                cursor = mysql.connection.cursor()
                cursor.execute("""
                    SELECT s.nome, m.nome AS modelo_nome
                    FROM Scripts s
                    JOIN modelo m ON s.id_modelo = m.id_modelo
                    WHERE s.id_script = %s
                """, (script_id,))
                script = cursor.fetchone()

                if not script:
                    error_message = f"Erro: Script ID {script_id} não encontrado.\n"
                    logging.error(error_message.strip())  # Log detalhado no terminal
                    yield f"Erro ao executar script.\n"  # Mensagem simplificada para o frontend
                    continue

                script_name, model_name = script

                cursor.execute("""
                    SELECT d.id_dispositivo, d.ip, d.username, d.password, d.access_type
                    FROM dispositivos d
                    WHERE d.id_modelo = %s
                """, (model_id,))
                dispositivos = cursor.fetchall()
                cursor.close()

                for dispositivo in dispositivos:
                    device_id, ip, username, encrypted_password, access_type = dispositivo
                    password = decrypt_password(encrypted_password) if encrypted_password else None

                    # Montar comando de execução
                    base_dir = os.path.dirname(__file__)
                    script_path = os.path.join(base_dir, 'scripts', model_name, script_name)
                    command = [sys.executable, script_path, '--ip', ip]

                    if use_credentials and access_type == 'user_password':
                        command += ['--username', username, '--password', password]
                    elif not use_credentials:
                        command += ['--password', password]

                    for param, value in parameters.items():
                        command += [f"--{param}", str(value)]

                    # Logs detalhados para o terminal
                    logging.info(
                        f"Processando: Model ID={model_id}, Script ID={script_id}, "
                        f"Use Credentials={use_credentials}, Parameters={parameters}"
                    )
                    logging.info(f"Executando comando: {' '.join(command)}")

                    # Executar script
                    yield f"Executando script '{script_name}' no dispositivo {ip}...\n"
                    result = subprocess.run(command, capture_output=True, text=True)

                    if result.returncode == 0:
                        success_message = f"Sucesso no dispositivo {ip}:\n{result.stdout.strip()}\n"
                        logging.info(success_message.strip())  # Log detalhado no terminal
                        yield success_message  # Enviado ao frontend

                        # Verificar se há novas credenciais na saída do script
                        stdout = result.stdout
                        new_username = None
                        new_password = None
                        if "NEW_CREDENTIALS" in stdout:
                            credentials_part = stdout.split("NEW_CREDENTIALS")[1].strip()
                            credentials = dict(item.split("=") for item in credentials_part.split(","))
                            new_username = credentials.get("username")
                            new_password = credentials.get("password")

                        # Atualizar as credenciais no banco de dados, se necessário
                        if new_password:
                            try:
                                encrypted_password = cipher_suite.encrypt(new_password.encode()).decode()
                                update_query = """
                                    UPDATE dispositivos
                                    SET username = %s, password = %s
                                    WHERE id_dispositivo = %s
                                """
                                cursor = mysql.connection.cursor()
                                cursor.execute(update_query, (new_username or username, encrypted_password, device_id))
                                mysql.connection.commit()
                                cursor.close()
                                yield f"Credenciais atualizadas para o dispositivo {ip}.\n"
                            except Exception as e:
                                logging.error(f"Erro ao atualizar credenciais no banco: {e}")
                                yield f"Erro ao atualizar credenciais no banco para o dispositivo {ip}.\n"
                    else:
                        error_message = f"Erro no dispositivo {ip}:\n{result.stderr.strip()}\n"
                        logging.error(error_message.strip())  # Log detalhado no terminal
                        yield error_message  # Enviado ao frontend

        return Response(stream_with_context(generate_logs()), content_type='text/plain')

    except Exception as e:
        logging.exception("Erro inesperado durante a execução dos scripts.")
        return jsonify({"error": f"Erro inesperado: {str(e)}"}), 500








@app.route('/get-group-scripts/<string:group_name>', methods=['GET'])
@login_required
def get_group_scripts(group_name):
    logging.info(f"Carregando scripts para o grupo: {group_name}")
    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT d.id_dispositivo, d.nome, m.id_modelo, m.nome AS modelo_nome, d.ip
            FROM dispositivos d
            JOIN modelo m ON d.id_modelo = m.id_modelo
            JOIN grupo g ON d.id_grupo = g.id_grupo
            WHERE g.nome = %s
        """, (group_name,))
        dispositivos = cursor.fetchall()
        logging.debug(f"Dispositivos encontrados para o grupo '{group_name}': {dispositivos}")

        if not dispositivos:
            logging.warning(f"Nenhum dispositivo encontrado para o grupo '{group_name}'")
            return jsonify({"error": "Nenhum dispositivo encontrado para este grupo."}), 404

        modelos = {}
        for dispositivo in dispositivos:
            dispositivo_id, dispositivo_nome, modelo_id, modelo_nome, ip = dispositivo
            if modelo_id not in modelos:
                modelos[modelo_id] = {
                    "id": modelo_id,
                    "name": modelo_nome,
                    "devices": [],
                    "scripts": []
                }
            modelos[modelo_id]["devices"].append(f"{dispositivo_nome} ({ip})")

        for modelo_id in modelos:
            cursor.execute("""
                SELECT s.id_script, s.nome, p.nome_parametro, p.descricao_parametro
                FROM Scripts s
                LEFT JOIN Parametros_scripts p ON s.id_script = p.id_script
                WHERE s.id_modelo = %s
            """, (modelo_id,))
            scripts = cursor.fetchall()
            logging.debug(f"Scripts para o modelo '{modelo_id}': {scripts}")

            script_data = {}
            for script_id, script_name, param_name, param_desc in scripts:
                if script_id not in script_data:
                    script_data[script_id] = {"id": script_id, "name": script_name, "parameters": []}
                if param_name:
                    script_data[script_id]["parameters"].append({
                        "name": param_name,
                        "description": param_desc
                    })
            modelos[modelo_id]["scripts"] = list(script_data.values())

        cursor.close()
        logging.info(f"Dados carregados com sucesso para o grupo '{group_name}': {modelos}")
        return jsonify({"models": list(modelos.values())})
    except Exception as e:
        logging.error(f"Erro ao carregar scripts para o grupo '{group_name}': {str(e)}")
        return jsonify({"error": f"Erro ao carregar dados do grupo: {str(e)}"}), 500



# Tratamento de erro 404
@app.errorhandler(404)  
def page_not_found(e):
    return render_template('404.html'), 404

# Executa o servidor se o script for executado diretamente
if __name__ == '__main__':
    with app.app_context():
        create_admin_user()
    app.run(debug=True, host='0.0.0.0', port=5000)
#, use_reloader=False
