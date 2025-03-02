import time  # Importa a biblioteca time para usar pausas (time.sleep)
import argparse  # Importa a biblioteca argparse para lidar com argumentos de linha de comando
from selenium import webdriver  # Importa o WebDriver do Selenium para automação do navegador
from selenium.webdriver.common.by import By  # Importa a classe By para localizar elementos na página
from selenium.webdriver.support.ui import WebDriverWait  # Importa WebDriverWait para esperar condições específicas
from selenium.webdriver.support import expected_conditions as EC  # Importa expected_conditions para definir condições de espera
from selenium.webdriver.chrome.service import Service  # Importa Service para configurar o ChromeDriver
from webdriver_manager.chrome import ChromeDriverManager  # Importa ChromeDriverManager para gerenciar a instalação do ChromeDrive
import logging  # Importa a biblioteca logging para gerenciar logs
import os  # Importa a biblioteca os para interagir com o sistema operacional

def configurar_rede(ip, username, password):
     # Configurações do ChromeDriver em modo headless
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-application-cache')
    options.add_argument('--incognito')
    options.add_argument('--disable-gpu')
    options.add_argument('--use-gl=swiftshader')


    # Configura o ChromeDriver para suprimir logs
    service = Service(ChromeDriverManager().install())  # Instala o ChromeDriver automaticamente e cria um serviço
    service.creationflags = 0x08000000  # Suprime a janela do console no Windows
    service.arguments = ['--log-level=3']  # Define o nível de log do ChromeDriver como mínimo
    service.log_path = os.devnull  # Descarta os logs do ChromeDriver

    # Configura o Selenium para suprimir logs
    selenium_logger = logging.getLogger('selenium')  # Obtém o logger do Selenium
    selenium_logger.setLevel(logging.CRITICAL)  # Define o nível de log do Selenium como CRITICAL (suprime logs)

    # Configura o logger global para suprimir logs
    logging.basicConfig(level=logging.CRITICAL)  # Define o nível de log global como CRITICAL

    driver = webdriver.Chrome(service=service, options=options)  # Inicializa o WebDriver do Chrome com as opções configuradas
    
    try:
        # Acessa a página de login do roteador
        driver.get(f"http://{ip}")  # Navega até o endereço IP do roteador

        # Preenche o formulário de login
        campo_username_login = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="login_username"]'))
        )  # Espera até que o campo de usuário esteja presente na página
        campo_username_login.send_keys(username)  # Preenche o campo de usuário com o nome de usuário fornecido

        campo_senha_login = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/form/div/div/div[3]/div[5]/input'))
        )  # Espera até que o campo de senha esteja presente na página
        campo_senha_login.send_keys(password)  # Preenche o campo de senha com a senha fornecida
        driver.find_element(By.XPATH, '//*[@id="login_filed"]/div[9]').click()  # Clica no botão de login
        time.sleep(5)  # Aguarda 5 segundos para a página carregar
        # Localiza o elemento com o id "_clientNumber" e lê o valor
        client_number_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "_clientNumber"))
        )
        client_number = client_number_element.text  # Captura o valor do texto
        print(f"Número de clientes: {client_number}")  # Imprime o valor encontrado

    finally:
        time.sleep(2)  # Aguarda um pouco antes de fechar
        driver.quit()  # Fecha o navegador

if __name__ == "__main__":
    # Configuração do parser de argumentos
    parser = argparse.ArgumentParser(description="Configura a rede do roteador.")  # Cria um parser de argumentos
    parser.add_argument("--ip", required=True, help="Endereço IP do roteador")  # Adiciona o argumento --ip
    parser.add_argument("--username", required=True, help="Usuário de administrador do roteador")  # Adiciona o argumento --username
    parser.add_argument("--password", required=True, help="Senha de administrador do roteador")  # Adiciona o argumento --password

    args = parser.parse_args()  # Faz o parsing dos argumentos da linha de comando

    # Chama a função de configuração com os argumentos
    configurar_rede(args.ip, args.username, args.password)  # Executa a função principal