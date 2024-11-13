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
time.sleep(5)

botao_avancado = driver.find_element(By.XPATH, "//span[@class='sub-navigator-text' and text()='Avançado']")
botao_avancado.click()
time.sleep(5)

botao_configuracaorapida = driver.find_element(By.XPATH, "//span[@class='sub-navigator-text' and text()='Configuração Rápida']")
botao_configuracaorapida.click()
time.sleep(5)


pular = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[4]/div[2]/div[1]/a/span[2]'))
)
driver.execute_script("arguments[0].scrollIntoView(true);", pular)

botao_pular =  WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[4]/div[2]/div[1]/a/span[2]'))
)
botao_pular.click()
nome1_rede = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[1]/div[2]/div[2]/div[2]/div[3]/div[2]/div[2]/div[2]/div[1]/span[2]/input'))
)
nome1_rede.click()
nome1_rede.clear()
time.sleep(3)
nome1_rede.send_keys("Tcc2_2Ghz")
time.sleep(1)


senha1_rede = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[1]/div[2]/div[2]/div[2]/div[3]/div[2]/div[3]/div[2]/div[1]/span[2]/input'))
)
time.sleep(1)
senha1_rede.click()
senha1_rede.clear()
time.sleep(1)
senha1_rede.send_keys("Notadez!")
time.sleep(1)

nome2_rede = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[1]/div[2]/div[2]/div[2]/div[4]/div/div[2]/div[2]/div[2]/div[1]/span[2]/input'))
)
nome2_rede.click()
nome2_rede.clear()
time.sleep(1)
nome2_rede.send_keys("Tcc2_5Ghz")
time.sleep(1)


senha2_rede = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[1]/div[2]/div[2]/div[2]/div[4]/div/div[2]/div[3]/div[2]/div[1]/span[2]/input'))
)
time.sleep(1)
senha2_rede.click()
senha2_rede.clear()
time.sleep(1)
senha2_rede.send_keys("Notadez!")
time.sleep(1)

botao_proximo = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[2]/div[1]/a'))
)
botao_proximo.click()
time.sleep(1)



finalizar = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[5]/div/div/div[2]/div[2]/div[2]/div[4]/div[2]/div[1]/a'))
)
driver.execute_script("arguments[0].scrollIntoView(true);", finalizar)
time.sleep(2)
finalizar.click()

time.sleep(3)
driver.quit()