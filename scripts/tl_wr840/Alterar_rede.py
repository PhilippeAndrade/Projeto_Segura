import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# Configura o ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Função para definir SSID e senha da rede
def configurar_rede(driver, ssid_xpath, senha_xpath, ssid_valor, senha_valor):
    # Espera pelo campo de SSID e define o valor
    campo_ssid = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, ssid_xpath))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", campo_ssid)
    campo_ssid.clear()
    campo_ssid.send_keys(ssid_valor)
    time.sleep(1)
    
    # Espera pelo campo de Senha e define o valor
    campo_senha = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, senha_xpath))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", campo_senha)
    campo_senha.clear()
    campo_senha.send_keys(senha_valor)
    time.sleep(1)

try:
    # Acessa a página de login do roteador
    driver.get('http://192.168.1.1/')

    # Insere a senha e faz login
    campo_senha_login = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="local-pwd-tb"]/div[2]/div[1]/span[2]/input[1]'))
    )
    campo_senha_login.send_keys('4dm1nd4r3d3')
    driver.find_element(By.XPATH, '//*[@id="local-login-button"]/div[2]/div[1]/a').click()
    time.sleep(5)

    # Navega para as configurações Wireless
    botao_wireless = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#main-menu .navigator-ul .navigator-li:nth-child(3)"))
    )
    botao_wireless.click()
    time.sleep(5)

    # Configura o SSID e Senha para a rede de 2.4GHz
    configurar_rede(
        driver,
        ssid_xpath='/html/body/div[2]//input[contains(@data-bind,"wirelessBasicM.cSsid")]',  # Substitua pelo caminho exato
        senha_xpath='/html/body/div[2]//input[contains(@data-bind,"wirelessBasicM.cPskSecret")]',  # Substitua pelo caminho exato
        ssid_valor="Tcc2_2Ghz",
        senha_valor="Notadez!"
    )

    # Configura o SSID e Senha para a rede de 5GHz
    configurar_rede(
        driver,
        ssid_xpath='/html/body/div[2]//input[contains(@data-bind,"wirelessBasicM5g.cSsid")]',  # Substitua pelo caminho exato
        senha_xpath='/html/body/div[2]//input[contains(@data-bind,"wirelessBasicM5g.cPskSecret")]',  # Substitua pelo caminho exato
        ssid_valor="Tcc2_5Ghz",
        senha_valor="Notadez!"
    )

    # Clica no botão para salvar as configurações
    botao_salvar = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#save-data .button-wrap a'))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", botao_salvar)
    botao_salvar.click()
    time.sleep(1)

except TimeoutException:
    print("Ocorreu um Timeout - um elemento não foi encontrado dentro do tempo esperado.")
finally:
    driver.quit()
