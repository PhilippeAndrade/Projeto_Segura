import time  # Importa a biblioteca time para usar pausas (time.sleep)
import argparse  # Importa a biblioteca argparse para lidar com argumentos de linha de comando
from selenium import webdriver  # Importa o WebDriver do Selenium para automação do navegador
from selenium.webdriver.common.by import By  # Importa a classe By para localizar elementos na página
from selenium.webdriver.support.ui import WebDriverWait  # Importa WebDriverWait para esperar condições específicas
from selenium.webdriver.support import expected_conditions as EC  # Importa expected_conditions para definir condições de espera
from selenium.webdriver.chrome.service import Service  # Importa Service para configurar o ChromeDriver
from webdriver_manager.chrome import ChromeDriverManager  # Importa ChromeDriverManager para gerenciar a instalação do ChromeDriver
from selenium.webdriver.chrome.options import Options  # Importa Options para configurar opções do Chrome
import logging  # Importa a biblioteca logging para gerenciar logs
import os  # Importa a biblioteca os para interagir com o sistema operacional

def configurar_rede(ip, username, password, senha_nova):
    # Configurar as opções do Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-features=TensorFlowLite")
    chrome_options.add_argument("--disable-extensions")

    service = Service(ChromeDriverManager().install())  # Instala o ChromeDriver automaticamente e cria um serviço
    service.creationflags = 0x08000000  # Suprime a janela do console no Windows
    service.arguments = ['--log-level=3']  # Define o nível de log do ChromeDriver como mínimo
    service.log_path = os.devnull  # Descarta os logs do ChromeDriver

    # Configura o Selenium para suprimir logs
    selenium_logger = logging.getLogger('selenium')  # Obtém o logger do Selenium
    selenium_logger.setLevel(logging.CRITICAL)  # Define o nível de log do Selenium como CRITICAL (suprime logs)

    # Configura o logger global para suprimir logs
    logging.basicConfig(level=logging.CRITICAL)  # Define o nível de log global como CRITICAL

    driver = webdriver.Chrome(service=service, options=chrome_options)  # Inicializa o WebDriver do Chrome com as opções configuradas
    
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

        # Localiza o elemento "Administração" e clica nele
        admin_menu = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "Advanced_OperationMode_Content_menu"))
        )
        admin_menu.click()

        # Aguarda um pouco antes de buscar o próximo elemento
        time.sleep(2)  # Espera a página de administração carregar

        # Localiza o elemento "Sistema" e clica nele
        sistema_tab = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "Advanced_System_Content_tab"))
        )
        sistema_tab.click()  # Clica no elemento "Sistema"

        time.sleep(5)  # Aguarda um tempo para garantir que a nova página foi carregada

        alterar_links = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//span[text()='Alterar']"))
        )  # Espera até que todos os links "Alterar" estejam visíveis

        # Clica no **segundo** "Alterar" na lista
        if len(alterar_links) > 1:  # Garante que existe mais de um "Alterar"
            alterar_links[1].click()  # Clica no segundo link "Alterar"

        # Espera até que o campo de senha do modal esteja visível
        campo_senha_modal = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "http_passwd_cur"))
        )  # Espera até que o campo de senha esteja visível dentro do modal

        # Preenche o campo de senha com a nova senha
        campo_senha_modal.send_keys(password)  # Substitua "nova_senha_aqui" pela senha desejada

        campo_nova_senha_modal = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "http_passwd_new"))
        )  # Espera até que o campo de nova senha esteja visível dentro do modal

        # Preenche o campo de nova senha com a nova senha
        campo_nova_senha_modal.send_keys(senha_nova)  # Preenche o campo de nova senha com a nova senha desejada

        time.sleep(2)  # Aguarda 2 segundos para garantir que o campo de senha foi preenchido

        campo_confirmacao_nova_senha_modal = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "http_passwd_re"))
        )  # Espera até que o campo de confirmação da nova senha esteja visível dentro do modal

        # Preenche o campo de confirmação de nova senha com o mesmo valor da nova senha
        campo_confirmacao_nova_senha_modal.send_keys(senha_nova)  # Confirma a nova senha preenchendo o campo de confirmação

        time.sleep(2)  # Aguarda 2 segundos para garantir que os campos foram preenchidos

        # Clica no botão "OK" com o id "apply_chpass"
        botao_ok = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "apply_chpass"))
        ) # Espera até que o botão esteja visível e clicável
        botao_ok.click()  # Clica no botão "OK"

        time.sleep(1)




    finally:
        print(f"NEW_CREDENTIALS password={senha_nova}")
        time.sleep(2)  # Aguarda um pouco antes de fechar
        driver.quit()  # Fecha o navegador

if __name__ == "__main__":
    # Configuração do parser de argumentos
    parser = argparse.ArgumentParser(description="Configura a rede do roteador.")  # Cria um parser de argumentos
    parser.add_argument("--ip", required=True, help="Endereço IP do roteador")  # Adiciona o argumento --ip
    parser.add_argument("--username", required=True, help="Usuário de administrador do roteador")  # Adiciona o argumento --username
    parser.add_argument("--password", required=True, help="Senha de administrador do roteador")  # Adiciona o argumento --password
    parser.add_argument("--senha_nova", required=True, help="Senha nova de administrador do roteador")  # Adiciona o argumento --senha_nova

    args = parser.parse_args()  # Faz o parsing dos argumentos da linha de comando

    # Chama a função de configuração com os argumentos
    configurar_rede(args.ip, args.username, args.password, args.senha_nova)  # Executa a função principal
