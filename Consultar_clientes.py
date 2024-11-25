import re
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import argparse


def main(ip, password):
    # Configura o ChromeDriver usando o webdriver_manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    driver.get(f'http://{ip}/')

    campo_senha = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="local-pwd-tb"]/div[2]/div[1]/span[2]/input[1]'))
    )
    campo_senha.send_keys(password)
    time.sleep(2)

    botao_entrar = driver.find_element(By.XPATH, '//*[@id="local-login-button"]/div[2]/div[1]/a')
    botao_entrar.click()
    time.sleep(10)

    clientes = driver.find_elements(By.CSS_SELECTOR, '.map-clients-icon-num')

    # Verifica a quantidade de elementos e seleciona o segundo elemento, por exemplo
    num_clientes_desejado = "0"  # Valor padrão caso não encontre clientes
    if len(clientes) > 1:
        num_clientes_desejado = clientes[1].text  # Seleciona o segundo elemento (índice 1)
        
    driver.quit()
    return f"Número de clientes conectados: {num_clientes_desejado}"


if __name__ == "__main__":
    # Configuração do parser de argumentos
    parser = argparse.ArgumentParser(description="Configura a rede do roteador.")
    parser.add_argument("--ip", required=True, help="Endereço IP do roteador")
    parser.add_argument("--password", required=True, help="Senha de administrador do roteador")
    
    args = parser.parse_args()

    # Chama a função main com os argumentos e imprime o resultado
    resultado = main(args.ip, args.password)
    print(resultado)
