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

def configurar_rede(ip, username, password, ssid1, senha1, ssid2, senha2):
    # Configurar o WebDriver
    chrome_options = Options()  # Cria uma instância de Options para configurar o Chrome
    chrome_options.add_argument("--no-sandbox")  # Desativa o sandbox para evitar problemas de permissão
    chrome_options.add_argument("--disable-dev-shm-usage")  # Evita problemas de memória em ambientes limitados
    chrome_options.add_argument("--disable-features=TensorFlowLite")  # Desativa o TensorFlow Lite para melhorar o desempenho
    chrome_options.add_argument("--disable-extensions")  # Desativa extensões do Chrome para evitar interferências

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

        # Verifica se o elemento está dentro de um iframe
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')  # Localiza todos os iframes na página
        if iframes:
            for iframe in iframes:
                try:
                    driver.switch_to.frame(iframe)  # Muda o foco para o iframe atual
                    
                    # Aguarda até que os elementos estejam presentes
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'wl0_ssid'))
                    )  # Espera até que o campo SSID da rede 2.4GHz esteja presente
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'wl0_wpa_psk'))
                    )  # Espera até que o campo de senha da rede 2.4GHz esteja presente
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'wl1_ssid'))
                    )  # Espera até que o campo SSID da rede 5GHz esteja presente
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'wl1_wpa_psk'))
                    )  # Espera até que o campo de senha da rede 5GHz esteja presente

                    # Preenche os campos
                    input_ssid1 = driver.find_element(By.ID, 'wl0_ssid')  # Localiza o campo SSID da rede 2.4GHz
                    input_senha1 = driver.find_element(By.ID, 'wl0_wpa_psk')  # Localiza o campo de senha da rede 2.4GHz
                    input_ssid2 = driver.find_element(By.ID, 'wl1_ssid')  # Localiza o campo SSID da rede 5GHz
                    input_senha2 = driver.find_element(By.ID, 'wl1_wpa_psk')  # Localiza o campo de senha da rede 5GHz

                    botao_aplicar = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//input[@class="button_gen" and @value="Aplicar"]'))
                    )  # Espera até que o botão "Aplicar" esteja clicável
                    
                    input_ssid1.clear()  # Limpa o campo SSID da rede 2.4GHz
                    input_ssid1.send_keys(ssid1)  # Preenche o campo SSID da rede 2.4GHz com o valor fornecido
                    input_senha1.clear()  # Limpa o campo de senha da rede 2.4GHz
                    input_senha1.send_keys(senha1)  # Preenche o campo de senha da rede 2.4GHz com o valor fornecido
                    input_ssid2.clear()  # Limpa o campo SSID da rede 5GHz
                    input_ssid2.send_keys(ssid2)  # Preenche o campo SSID da rede 5GHz com o valor fornecido
                    input_senha2.clear()  # Limpa o campo de senha da rede 5GHz
                    input_senha2.send_keys(senha2)  # Preenche o campo de senha da rede 5GHz com o valor fornecido

                    botao_aplicar.click()  # Clica no botão "Aplicar" para salvar as configurações
                    WebDriverWait(driver, 30).until(
                        EC.invisibility_of_element_located((By.XPATH, '//*[@id="proceeding_main_txt" and text()="Concluído"]'))
                    )  # Espera até que a mensagem "Concluído" desapareça
                    time.sleep(20)

                    print("Campos preenchidos com sucesso!")  # Exibe uma mensagem de sucesso
                    break  # Sai do loop se os elementos forem encontrados e preenchidos
                except Exception:
                    # Continua para o próximo iframe sem exibir erros
                    driver.switch_to.default_content()  # Retorna ao contexto principal
                    continue

            # Retorna ao contexto principal após o loop
            driver.switch_to.default_content()  # Retorna ao contexto principal
        else:
            print("Nenhum iframe encontrado na página.")  # Exibe uma mensagem se nenhum iframe for encontrado

    except Exception:
        # Exibe apenas uma mensagem personalizada, sem a stacktrace
        print("Erro durante a execução.")  # Exibe uma mensagem de erro genérica
    finally:
        time.sleep(2)
        driver.quit()  # Fecha o navegador

if __name__ == "__main__":
    # Configuração do parser de argumentos
    parser = argparse.ArgumentParser(description="Configura a rede do roteador.")  # Cria um parser de argumentos
    parser.add_argument("--ip", required=True, help="Endereço IP do roteador")  # Adiciona o argumento --ip
    parser.add_argument("--username", required=True, help="Usuário de administrador do roteador")  # Adiciona o argumento --username
    parser.add_argument("--password", required=True, help="Senha de administrador do roteador")  # Adiciona o argumento --password
    parser.add_argument("--ssid1", required=True, help="Nome da rede 2.4GHz")  # Adiciona o argumento --ssid1
    parser.add_argument("--senha1", required=True, help="Senha da rede 2.4GHz")  # Adiciona o argumento --senha1
    parser.add_argument("--ssid2", required=True, help="Nome da rede 5GHz")  # Adiciona o argumento --ssid2
    parser.add_argument("--senha2", required=True, help="Senha da rede 5GHz")  # Adiciona o argumento --senha2

    args = parser.parse_args()  # Faz o parsing dos argumentos da linha de comando

    # Chama a função de configuração com os argumentos
    configurar_rede(args.ip, args.username, args.password, args.ssid1, args.senha1, args.ssid2, args.senha2)  # Executa a função principal