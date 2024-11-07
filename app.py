# Importa as bibliotecas necessárias para o aplicativo Flask
from flask import Flask, render_template, redirect, url_for, flash, session, request, jsonify
from flask_mysqldb import MySQL  # Para conectar com o MySQL
from flask_wtf import FlaskForm  # Para formulários seguros com Flask-WTF
from wtforms import StringField, PasswordField, SubmitField  # Campos para o formulário
from wtforms.validators import DataRequired, Length  # Validações para os campos do formulário
import os  # Para manipulação do sistema operacional, como a geração de uma chave secreta
import bcrypt  # Para criptografar e verificar senhas
from functools import wraps  # Para criar decoradores personalizados

# Inicializa o aplicativo Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Gera uma chave secreta aleatória para as sessões

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
    submit = SubmitField('Criar Usuário')  # Botão de submissão do formulário

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


@app.route('/createdevice', methods=['GET', 'POST'])
@login_required
def create_device():
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        nome = data.get('nome')
        id_modelo = data.get('id_modelo')
        mac_address = data.get('mac_address')
        id_grupo = data.get('id_grupo')
        ip = data.get('ip')

        if nome and mac_address and ip:
            try:
                cursor = mysql.connection.cursor()
                cursor.execute("""
                    INSERT INTO dispositivos (nome, id_modelo, mac_address, id_grupo, ip) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (nome, id_modelo, mac_address, id_grupo, ip))
                mysql.connection.commit()
                cursor.close()

                return jsonify({"success": True, "message": "Dispositivo cadastrado com sucesso!"})
            except Exception as e:
                return jsonify({"success": False, "message": f"Erro ao cadastrar dispositivo: {str(e)}"})
        else:
            return jsonify({"success": False, "message": "Os campos Nome, MAC Address e IP são obrigatórios."})

    return render_template('createdevice.html')

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
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios")  # Seleciona todos os usuários
    usuarios = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':  # Se a requisição é POST
        usuarios_para_deletar = request.form.getlist('usuarios_para_deletar')  # Obtém os IDs dos usuários

        if usuarios_para_deletar:  # Se algum usuário foi selecionado
            try:
                cursor = mysql.connection.cursor()
                for usuario_id in usuarios_para_deletar:  # Deleta cada usuário selecionado
                    cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
                mysql.connection.commit()
                cursor.close()

                flash('Usuários excluídos com sucesso!', 'success')
                return redirect(url_for('deletar_usuarios'))
            except Exception as e:
                flash(f'Erro ao excluir usuário: {str(e)}', 'danger')

    return render_template('deletarusuarios.html', usuarios=usuarios)



# Rota para fazer upload de um script
@app.route('/uploadscript', methods=['GET', 'POST'])
def upload_script():
    if request.method == 'POST':  # Se a requisição é POST
        router_model_id = request.form['router_model_id']
        script_file = request.files['script_file']
        
        # Processa o upload (exemplo)
        return redirect(url_for('upload_script'))

    return render_template('upload_script.html')

# Rota para gerenciar dispositivos
@app.route('/managerdevices')
@login_required
def manager_devices():
    return render_template('managerdevices.html')

# Tratamento de erro 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Executa o servidor se o script for executado diretamente
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
