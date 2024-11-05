from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length



import os



app = Flask(__name__)
app.secret_key = os.urandom(24)  # Chave secreta para sessões seguras

# Configuração do formulário com Flask-WTF
class RegistrationForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

class UserCreationForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Papel', choices=[('admin', 'Admin'), ('user', 'Usuário')], validators=[DataRequired()])
    submit = SubmitField('Criar Usuário')


@app.route('/login', methods=['GET', 'POST'])  # Rota para registro de usuários
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Aqui você pode adicionar a lógica para salvar os dados no banco de dados
        flash('Usuário registrado com sucesso!', 'success')
        return redirect(url_for('register'))
    return render_template('login.html', form=form)
@app.route('/')
def home():
    # Redireciona para a rota de login
    return redirect(url_for('register'))
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__app__':
    app.run(debug=True, host='0.0.0.0', port=5000)
