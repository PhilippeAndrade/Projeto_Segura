from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import argparse
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def main(ip):
    """Função principal para acessar o roteador."""
    # Configurações do ChromeDriver em modo headless
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-application-cache')
    options.add_argument('--incognito')
    options.add_argument('--disable-gpu')
    options.add_argument('--use-gl=swiftshader')

    # Inicialização do WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        logging.info(f"Acessando a página do roteador em http://{ip}/...")
        # Tenta acessar a página do roteador
        driver.get(f'http://{ip}/')

        # Espera até que o logo do roteador esteja visível
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, "//img[contains(@src, 'themes/mercury/img/logo-icon.png')]")
            )
        )
        logging.info("Página carregada com sucesso.")
        return "Conexão com o roteador estabelecida e página carregada corretamente."
    
    except Exception as e:
        logging.error(f"Erro ao tentar acessar o roteador: {str(e)}")
        return f"Erro: Não foi possível acessar o IP {ip}. Detalhes: {str(e)}"
    
    finally:
        # Fecha o WebDriver
        driver.quit()
        logging.info("Driver fechado e operação finalizada.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Teste de conexão com o roteador.")
    parser.add_argument(
        "--ip",
        required=False,
        default="192.168.1.1",
        help="Endereço IP do roteador (padrão: 192.168.1.1)"
    )
    args = parser.parse_args()

    # Recebe o resultado da função main
    resultado = main(args.ip)

    # Exibe o resultado no terminal
    print(resultado)

    # Opcional: registra a mensagem de retorno no log
    logging.info(f"Resultado do teste: {resultado}")