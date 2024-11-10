import re
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Configura o ChromeDriver usando o webdriver_manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

driver.get('http://192.168.1.1/')

actions = ActionChains(driver)

campo_senha = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="local-pwd-tb"]/div[2]/div[1]/span[2]/input[1]'))
)
campo_senha.send_keys('4dm1nd4r3d3')
time.sleep(2)

botao_entrar = driver.find_element(By.XPATH, '//*[@id="local-login-button"]/div[2]/div[1]/a')
botao_entrar.click()
time.sleep(10)

clientes = driver.find_elements(By.CSS_SELECTOR, '.map-clients-icon-num')

# Verifica a quantidade de elementos e seleciona o segundo elemento, por exemplo
if len(clientes) > 1:
    num_clientes_desejado = clientes[1].text  # Seleciona o segundo elemento (índice 1)
    print(f"Número de clientes conectados: {num_clientes_desejado}")
driver.quit()