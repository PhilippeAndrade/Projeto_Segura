from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# Caminho para o executável do driver (substitua pelo seu caminho real)
driver_path = r'C:\Users\Cereja\Desktop\Teste\chromedriver.exe'


# Configura o serviço do Chrome
service = Service(driver_path)

# Inicializa o navegador Chrome com o serviço configurado
driver = webdriver.Chrome(service=service)

# Abre o site do Gmail
driver.get("https://mail.google.com")

# Encontra o campo de e-mail pelo atributo 'type'
campo_email = driver.find_element("css selector", 'input[type="email"]')

# Digita o e-mail e pressiona Enter
campo_email.send_keys("l.cereja@gsuite.iff.edu.br")
# Localiza o elemento "Avançar" pelo texto usando XPath
botao_avancar = driver.find_element(By.XPATH, '//span[text()="Avançar"]')

botao_avancar.click()
# campo_email.send_keys(Keys.RETURN)

# Aguarde alguns segundos para a página de senha carregar completamente
time.sleep(5)

# Aguarda até 10 segundos para o campo de senha estar presente na página
campo_usuario=WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]'))
)
campo_senha = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
)

# Digita a senha e pressiona Enter
campo_usuario.send_keys("15982575798")
campo_senha.send_keys("102036.Luca")
campo_senha.send_keys(Keys.RETURN)

# Aguarde alguns segundos para visualizar a caixa de entrada
time.sleep(5)


# Fecha o navegador
while True:
    pass
