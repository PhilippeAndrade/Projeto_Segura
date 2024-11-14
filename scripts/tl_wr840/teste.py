import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys

# Caminho para o executável do driver (substitua pelo seu caminho real)
driver_path = r'C:\Users\ti\OneDrive\Desktop\Conhecimento\TCC\Teste\Teste'

# Configura o serviço do Chrome
service = Service(driver_path)

# Inicializa o navegador Chrome com o serviço configurado
driver = webdriver.Chrome(service=service)

# Abre o site do Google
driver.get("https://www.google.com")

# Encontra o campo de pesquisa pelo nome (no caso do Google, é 'q')
search_box = driver.find_element("name", "q")

# Digita algo no campo de pesquisa
search_box.send_keys("Selenium em Python")

# Pressiona Enter para fazer a pesquisa
search_box.send_keys(Keys.RETURN)

# Aguarde alguns segundos para visualizar os resultados (opcional)
#driver.implicitly_wait(20)

time.sleep(5)

# Mantém o navegador aberto indefinidamente
while True:
    pass
input("Pressione Enter para fechar o navegador...")

 #Fecha o navegador
driver.quit()
