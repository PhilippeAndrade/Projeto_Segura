from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configura o ChromeDriver em modo headless e desativa o cache
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-application-cache')
options.add_argument('--incognito')
options.page_load_strategy = 'none'

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Define um timeout para o carregamento da página
    driver.set_page_load_timeout(2)
    
    # Tenta acessar a página do roteador
    driver.get('http://192.168.1.1/')
    
    # Espera até que o elemento de logo esteja visível
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//img[contains(@src, 'themes/mercury/img/logo-icon.png')]"))
        )
        print("Conexão com o roteador estabelecida e página carregada corretamente.")
    except Exception:
        print("Erro: A página do roteador não foi carregada corretamente ou o elemento de logo não foi encontrado.")
    
except Exception:
    print("Erro: Não foi possível acessar o IP 192.168.1.1")
    
finally:
    # Fecha o driver
    driver.quit()
