from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuração do formulário com Flask-WTF
class RegistrationForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
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
    # Verifica se o usuário está logado
    if 'username' not in session:
        flash('Você precisa fazer login para acessar essa página.', 'danger')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

@app.route('/')
def home():
    return redirect(url_for('login'))

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
