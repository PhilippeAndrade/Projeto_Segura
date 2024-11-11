import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Configura o ChromeDriver usando o webdriver_manager
options = Options()
options.add_argument("--start-maximized")
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

botao_avancado = driver.find_element(By.XPATH, "//span[@class='sub-navigator-text' and text()='Avançado']")
botao_avancado.click()
time.sleep(5)

botao_sistema = driver.find_element(By.XPATH, "//span[@class='sub-navigator-text' and text()='Sistema']")
driver.execute_script("arguments[0].scrollIntoView(true);", botao_sistema)
time.sleep(2)
botao_sistema.click()
time.sleep(5)

botao_restaurar = driver.find_element(By.XPATH, "//span[@class='sub-navigator-text' and text()='Salvar e Restaurar']")
driver.execute_script("arguments[0].scrollIntoView(true);", botao_restaurar)
botao_restaurar.click()
time.sleep(5)

botao_restaura_fab = driver.find_element(By.XPATH, "//span[@class='text button-text' and text()='RESTAURAÇÃO DE FÁBRICA']")
driver.execute_script("arguments[0].scrollIntoView(true);", botao_restaura_fab)
botao_restaura_fab.click()
time.sleep(5)

botao_restaura_confirm = driver.find_element(By.CSS_SELECTOR, '#factory-confirm-msg-btn-ok > div.widget-wrap-outer.button-wrap-outer > div.widget-wrap.button-wrap > a')
botao_restaura_confirm.click()
time.sleep(50)

print("O AP foi resetado de fábrica!")
driver.quit()