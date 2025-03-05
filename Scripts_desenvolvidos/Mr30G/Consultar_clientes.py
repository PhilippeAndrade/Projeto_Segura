import os
import time
import logging
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def configurar_rede(ip, password):
    # Configurar o WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")  # Desativa o sandbox para evitar problemas de permissão
    chrome_options.add_argument("--disable-dev-shm-usage")  # Evita problemas de memória em ambientes limitados
    chrome_options.add_argument("--disable-features=TensorFlowLite")  # Desativa o TensorFlow Lite para melhorar o desempenho
    chrome_options.add_argument("--disable-extensions")  # Desativa extensões do Chrome para evitar interferências
    chrome_options.add_argument("--headless")  # Comente esta linha para testar sem o modo headless

    # Configura o ChromeDriver para suprimir logs
    service = Service(ChromeDriverManager().install())  # Instala o ChromeDriver automaticamente e cria um serviço
    service.creationflags = 0x08000000  # Suprime a janela do console no Windows
    service.arguments = ['--log-level=3']  # Define o nível de log do ChromeDriver como mínimo
    service.log_path = os.devnull  # Descarta os logs do ChromeDriver

    # Configura o logger global para suprimir logs
    logging.basicConfig(level=logging.CRITICAL)  # Define o nível de log global como CRITICAL
    selenium_logger = logging.getLogger('selenium')  # Obtém o logger do Selenium
    selenium_logger.setLevel(logging.CRITICAL)  # Define o nível de log do Selenium como CRITICAL (suprime logs)

    driver = webdriver.Chrome(service=service, options=chrome_options)  # Inicializa o WebDriver do Chrome com as opções configuradas

    try:
        # Acessa a página de login do roteador
        driver.get(f"http://{ip}")  # Navega até o endereço IP do roteador

    
        # Ações de login
        campo_senha = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="local-pwd-tb"]/div[2]/div[1]/span[2]/input[1]'))
        )
        campo_senha.send_keys(password)

        botao_entrar = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="local-login-button"]/div[2]/div[1]/a'))
        )
        botao_entrar.click()

        time.sleep(10)  # Aguarda 10 segundos para garantir que a página seja carregada

        # Verifica o número de clientes conectados
        clientes = driver.find_elements(By.CSS_SELECTOR, '.map-clients-icon-num')

        # Verifica a quantidade de elementos e seleciona o segundo elemento, por exemplo
        if len(clientes) > 1:
            num_clientes_desejado = clientes[1].text  # Seleciona o segundo elemento (índice 1)
            print(f"Número de clientes conectados: {num_clientes_desejado}")
        else:
            print("Número de clientes não encontrado ou insuficientes elementos.")

    except Exception as e:
        print(f"Erro ocorreu durante a execução: {str(e)}")
    finally:
        driver.quit()  # Fecha o navegador após o término da execução


if __name__ == "__main__":
    # Configuração do parser de argumentos
    parser = argparse.ArgumentParser(description="Configura a rede do roteador.")  # Cria um parser de argumentos
    parser.add_argument("--ip", required=True, help="Endereço IP do roteador")  # Adiciona o argumento --ip
    parser.add_argument("--password", required=True, help="Senha de administrador do roteador")  # Adiciona o argumento --password

    args = parser.parse_args()  # Faz o parsing dos argumentos da linha de comando

    # Chama a função de configuração com os argumentos
    configurar_rede(args.ip, args.password)  # Executa a função principal
