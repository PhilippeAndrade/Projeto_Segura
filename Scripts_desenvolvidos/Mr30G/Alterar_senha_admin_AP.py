import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager



def configurar_senha(ip, password, senha_nova):
    # Configurar o WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(f"http://{ip}")
    campo_senha_login = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="local-pwd-tb"]/div[2]/div[1]/span[2]/input[1]'))
    )
    campo_senha_login.send_keys(password)
    driver.find_element(By.XPATH, '//*[@id="local-login-button"]/div[2]/div[1]/a').click()
    time.sleep(5)

    driver.find_element(By.XPATH, "(//ul[@class='navigator-ul navigator-ul-level1']/li)[4]/a").click()
    
    botao_sistema = driver.find_element(By.XPATH, "//span[@class='sub-navigator-text' and text()='Sistema']")
    driver.execute_script("arguments[0].scrollIntoView(true);", botao_sistema)
    time.sleep(2)
    botao_sistema.click()
    time.sleep(5)

    botao_administracao = driver.find_element(By.XPATH, "//span[@class='sub-navigator-text' and text()='Administração']")
    driver.execute_script("arguments[0].scrollIntoView(true);", botao_administracao)
    botao_administracao.click()

    wait = WebDriverWait(driver, 20)

    # Aguardar o campo de "Senha Antiga" estar presente
    senha_antiga_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//label[text()='Senha Antiga']/../../..//input[@type='password']"))
    )
    senha_antiga_input.clear()
    senha_antiga_input.send_keys(password)

    # Aguardar o campo de "Nova Senha"
    senha_nova_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//label[text()='Nova Senha']/../../..//input[@type='password']"))
    )
    senha_nova_input.clear()
    senha_nova_input.send_keys(senha_nova)

    # Aguardar o campo de "Confirmar Nova Senha"
    confirmar_nova_senha_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//label[text()='Confirmar Nova Senha']/../../..//input[@type='password']"))
    )
    confirmar_nova_senha_input.clear()
    confirmar_nova_senha_input.send_keys(senha_nova)


    botao_salvar = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#save-data > div.widget-wrap-outer.button-wrap-outer > div.widget-wrap.button-wrap > a > span.text.button-text'))
        )
    driver.execute_script("arguments[0].scrollIntoView(true);", botao_salvar)
    botao_salvar.click()
    time.sleep(5)

    print(f"NEW_CREDENTIALS password={senha_nova}")

if __name__ == "__main__":
        # Configuração do parser de argumentos
    parser = argparse.ArgumentParser(description="Configura a rede do roteador.")
    parser.add_argument("--ip", required=True, help="Endereço IP do roteador")
    parser.add_argument("--password", required=True, help="Senha de administrador do roteador")
    parser.add_argument("--senha_nova", required=True, help="Senha de administrador nova")
    


    args = parser.parse_args()

        # Chama a função de configuração com os argumentos
    configurar_senha(args.ip, args.password, args.senha_nova)

