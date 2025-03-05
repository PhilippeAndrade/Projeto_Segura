import os
import time
import logging
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


def configurar_rede(ip, password):
    # Configurar o WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")  # Desativa o sandbox para evitar problemas de permissão
    chrome_options.add_argument("--disable-dev-shm-usage")  # Evita problemas de memória em ambientes limitados
    chrome_options.add_argument("--disable-features=TensorFlowLite")  # Desativa o TensorFlow Lite para melhorar o desempenho
    chrome_options.add_argument("--disable-extensions")  # Desativa extensões do Chrome para evitar interferências
    chrome_options.add_argument("--headless")  # Modo headless (sem interface gráfica)

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

        # Espera até que o elemento de logo esteja visível
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//img[contains(@src, 'themes/mercury/img/logo-icon.png')]"))
        )
        print("Conexão com o roteador estabelecida e página carregada corretamente.")
    except Exception as e:
        print(f"Erro: {str(e)}")  # Exibe a exceção caso ocorra algum erro durante a execução

    finally:
        time.sleep(2)  # Espera 2 segundos antes de fechar
        driver.quit()  # Fecha o navegador


if __name__ == "__main__":
    # Configuração do parser de argumentos
    parser = argparse.ArgumentParser(description="Configura a rede do roteador.")  # Cria um parser de argumentos
    parser.add_argument("--ip", required=True, help="Endereço IP do roteador")  # Adiciona o argumento --ip
    parser.add_argument("--password", required=True, help="Senha de administrador do roteador")  # Adiciona o argumento --password

    args = parser.parse_args()  # Faz o parsing dos argumentos da linha de comando

    # Chama a função de configuração com os argumentos
    configurar_rede(args.ip, args.password)  # Executa a função principal
