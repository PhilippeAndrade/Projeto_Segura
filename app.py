from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
import os

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
        
        if username == 'cereja' and password == '123456':
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Login não encontrado!', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Você precisa fazer login para acessar essa página.', 'danger')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

@app.route('/createuser', methods=['GET', 'POST'])
def create_user():
    form = UserForm()  # Instancia o formulário
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        if username and password:
            try:
                cursor = mysql.connection.cursor()
                cursor.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", (username, password))
                mysql.connection.commit()
                cursor.close()
                
                flash('Usuário criado com sucesso!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f'Erro ao criar usuário: {str(e)}', 'danger')
        else:
            flash('Todos os campos são obrigatórios.', 'danger')

    return render_template('createuser.html', form=form)  # Renderiza o formulário

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Você foi deslogado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
