from flask import Flask, render_template, redirect, url_for, flash, session, request,jsonify
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
import os
import bcrypt
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuração de conexão com o MySQL
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "admin"
app.config['MYSQL_DB'] = "segura"

mysql = MySQL(app)

# Formulário para criação de usuários
class UserForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Criar Usuário')

# Decorador para verificar se o usuário está logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Você precisa fazer login para acessar essa página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT password FROM usuarios WHERE username = %s", (username,))  # Seleciona a senha do usuário
        bd_password = cursor.fetchone()  # Obtém a senha do banco (deve ser um único resultado)
        cursor.close()
        
        if bd_password:  # Se o usuário existe
            senha_hashed = bd_password[0]  # Pega o hash da senha
            print(f'Senha digitada: {password}')  # Para depuração
            print(f'Senha hash armazenada: {senha_hashed}')  # Para depuração
            
            if verificar_senha(password, senha_hashed):  # Verifica se a senha está correta
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                flash('Senha incorreta!', 'danger')  # Mensagem específica para senha incorreta
        else:
            flash('Usuário não encontrado!', 'danger')  # Mensagem específica para usuário não encontrado
    
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/createuser', methods=['GET', 'POST'])
@login_required
def create_user():
    form = UserForm()
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if username and password:
            password_hashed = hash_senha(password)
            
            try:
                cursor = mysql.connection.cursor()
                cursor.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", (username, password_hashed))
                mysql.connection.commit()
                cursor.close()
                
                # Retorna JSON em vez de redirecionar
                return jsonify({"success": True, "message": "Usuário criado com sucesso!"})
            except Exception as e:
                return jsonify({"success": False, "message": f"Erro ao criar usuário: {str(e)}"})
        else:
            return jsonify({"success": False, "message": "Todos os campos são obrigatórios."})

    return render_template('createuser.html', form=form)

def hash_senha(senha):
    # Gera um "salt"
    salt = bcrypt.gensalt()
    # Gera o hash da senha
    senha_hashed = bcrypt.hashpw(senha.encode(), salt)
    return senha_hashed.decode('utf-8')  # Armazena como string

def verificar_senha(senha, senha_hashed):
    # Verifica se a senha corresponde ao hash armazenado
    return bcrypt.checkpw(senha.encode(), senha_hashed.encode())  # Converte senha_hashed para bytes

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Você foi deslogado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/alterarusuarios', methods=['GET', 'POST'])
@login_required
def alterar_usuarios():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios")  # Seleciona todos os usuários do banco
    usuarios = cursor.fetchall()  # Retorna todos os usuários
    cursor.close()

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')

        # Verificação de senha
        if nova_senha != confirmar_senha:
            flash("As senhas não coincidem. Por favor, tente novamente.", "danger")
        elif len(nova_senha) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.", "danger")
        else:
            try:
                # Gera o hash da nova senha
                nova_senha_hashed = hash_senha(nova_senha)
                cursor = mysql.connection.cursor()
                cursor.execute("UPDATE usuarios SET password = %s WHERE id = %s", (nova_senha_hashed, user_id))
                mysql.connection.commit()
                cursor.close()
                
                flash("Senha do usuário alterada com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao alterar senha: {str(e)}", "danger")

    return render_template('alterarusuarios.html', usuarios=usuarios)

@app.route('/visualizarusuarios')
@login_required
def visualizar_usuarios():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios")  # Seleciona todos os usuários do banco
    usuarios = cursor.fetchall()  # Retorna todos os usuários
    cursor.close()

    return render_template('visualizarusuarios.html', usuarios=usuarios)

@app.route('/deletarusuarios', methods=['GET', 'POST'])
@login_required
def deletar_usuarios():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios")  # Seleciona todos os usuários
    usuarios = cursor.fetchall()  # Retorna todos os usuários
    cursor.close()

    if request.method == 'POST':
        usuarios_para_deletar = request.form.getlist('usuarios_para_deletar')  # Obtém os IDs dos usuários selecionados

        if usuarios_para_deletar:
            try:
                cursor = mysql.connection.cursor()
                for usuario_id in usuarios_para_deletar:
                    cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
                mysql.connection.commit()
                cursor.close()

                flash('Usuários excluídos com sucesso!', 'success')
                return redirect(url_for('deletar_usuarios'))  # Redireciona de volta para a página de exclusão
            except Exception as e:
                flash(f'Erro ao excluir usuário: {str(e)}', 'danger')

    return render_template('deletarusuarios.html', usuarios=usuarios)

@app.route('/add_device', methods=['POST'])
def add_device():
    data = request.get_json()
    device_name = data.get('deviceName')
    device_ip = data.get('deviceIP')

    # Aqui você pode adicionar lógica para salvar o dispositivo no banco de dados
    # Para este exemplo, vamos apenas retornar uma resposta de sucesso

    response = {
        "success": True,
        "message": f"Dispositivo '{device_name}' com IP '{device_ip}' adicionado com sucesso!"
    }
    return jsonify(response)
@app.route('/uploadscript', methods=['GET', 'POST'])
def upload_script():
    if request.method == 'POST':
        # Aqui você pode adicionar a lógica para processar o upload do script
        router_model_id = request.form['router_model_id']
        script_file = request.files['script_file']
        
        # Por exemplo, salvar o arquivo e processá-lo de acordo com o modelo selecionado
        # script_file.save(f"caminho/para/salvar/{script_file.filename}")

        # Redirecionar ou mostrar uma mensagem de sucesso (opcional)
        return redirect(url_for('upload_script'))

    # Renderiza o template com a lista de modelos de roteadores
    return render_template('upload_script.html')
@app.route('/managerdevices')
@login_required
def manager_devices():
    return render_template('managerdevices.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)