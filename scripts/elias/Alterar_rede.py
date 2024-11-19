import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager



def configurar_rede(ip, password, ssid1, senha1, ssid2, senha2):
    # Configurar o WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

        
        # Acessa a página de login do roteador
    driver.get(f"http://{ip}")
    wait = WebDriverWait(driver, 30)
        # Insere a senha de administrador e faz login
    campo_senha_login = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="local-pwd-tb"]/div[2]/div[1]/span[2]/input[1]'))
    )
    campo_senha_login.send_keys(password)
    driver.find_element(By.XPATH, '//*[@id="local-login-button"]/div[2]/div[1]/a').click()
    time.sleep(5)

            # Navega para as configurações Wireless
    botao_wireless = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#main-menu .navigator-ul .navigator-li:nth-child(3)"))
    )
    botao_wireless.click()
    time.sleep(5)

        # Localizar o elemento pelo seletor CSS
    try:
            
                # Localiza o campo de SSID 2.4GHz
        nomerede1 = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/div[1]/div[2]/div[2]/div[2]/div[5]/div[2]/div[1]/div[2]/div[1]/span[2]/input"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", nomerede1)
        nomerede1.clear()
        nomerede1.send_keys(ssid1)



        senha_rede1 = driver.find_element(By.XPATH, "//label[text()='Senha']/../../..//input")
        senha_rede1.clear()
        senha_rede1.send_keys(senha1)    
        # Localiza o campo de Senha 2.4GHz
        

        nomerede2 = driver.find_element(By.XPATH, "(//label[text()='Nome de Rede (SSID)']/../../..//input)[2]")
        driver.execute_script("arguments[0].scrollIntoView(true);", nomerede2)
        nomerede2.clear()
        nomerede2.send_keys(ssid2)

    # Localizar e rolar até o campo Senha da Rede 2
        senha_rede2 = driver.find_element(By.XPATH, "(//label[text()='Senha']/../../..//input)[2]")
        driver.execute_script("arguments[0].scrollIntoView(true);", senha_rede2)
        senha_rede2.clear()
        senha_rede2.send_keys(senha2)


            # # Clica no botão para salvar as configurações
        botao_salvar = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#save-data .button-wrap a'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", botao_salvar)
        botao_salvar.click()
        time.sleep(5)
    finally:
        print("Configuração realizada com sucesso!")

if __name__ == "__main__":
        # Configuração do parser de argumentos
    parser = argparse.ArgumentParser(description="Configura a rede do roteador.")
    parser.add_argument("--ip", required=True, help="Endereço IP do roteador")
    parser.add_argument("--password", required=True, help="Senha de administrador do roteador")
    parser.add_argument("--rede1", required=True, help="Nome da rede 2.4GHz")
    parser.add_argument("--senha1", required=True, help="Senha da rede 2.4GHz")
    parser.add_argument("--rede2", required=True, help="Nome da rede 5GHz")
    parser.add_argument("--senha2", required=True, help="Senha da rede 5GHz")


    args = parser.parse_args()

        # Chama a função de configuração com os argumentos
    configurar_rede(args.ip, args.password, args.rede1, args.senha1, args.rede2, args.senha2)
