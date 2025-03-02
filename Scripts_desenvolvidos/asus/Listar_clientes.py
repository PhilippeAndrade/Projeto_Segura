from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

def configurar_rede(ip, username, password):
    # Configurar as opções do Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-application-cache')
    options.add_argument('--incognito')
    options.add_argument('--disable-gpu')
    options.add_argument('--use-gl=swiftshader')


    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Acessa a página de login do roteador
        driver.get(f"http://{ip}")

        # Preenche o formulário de login
        campo_username_login = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="login_username"]'))
        )
        campo_username_login.send_keys(username)

        campo_senha_login = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/form/div/div/div[3]/div[5]/input'))
        )
        campo_senha_login.send_keys(password)
        driver.find_element(By.XPATH, '//*[@id="login_filed"]/div[9]').click()
        time.sleep(5)

        # Aguardar o carregamento da página após o login
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "clientsContainer"))
        )

        # Clicar no botão de clientes
        try:
            clients_container = driver.find_element(By.ID, "clientsContainer")

            # Verificar se o botão está visível e habilitado
            if clients_container.is_displayed() and clients_container.is_enabled():
                # Forçar o clique usando JavaScript
                driver.execute_script("arguments[0].click();", clients_container)
        except Exception as e:
            driver.quit()
            return

        # Mudar para o iframe "statusframe"
        try:
            WebDriverWait(driver, 20).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, "statusframe"))
            )
        except Exception as e:
            driver.quit()
            return

        # Aguardar o carregamento da lista de clientes dentro do iframe
        try:
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.ID, "client_list_Block"))
            )
        except Exception as e:
            driver.quit()
            return

        # Coleta os clientes na lista
        clientes = driver.find_elements(By.CLASS_NAME, "clientBg")
        lista_clientes = []

        for cliente in clientes:
            try:
                if cliente.is_displayed():
                    # Coleta das informações do cliente
                    nome_cliente = cliente.find_element(By.XPATH, ".//td[2]/div").text
                    ip_cliente = cliente.find_element(By.XPATH, ".//tr[2]/td[1]").text
                    mac_cliente = cliente.find_element(By.XPATH, ".//tr[3]/td/div").text
                    
                    # Coleta do tipo de conexão
                    try:
                        tipo_conexao = cliente.find_element(By.XPATH, ".//tr[2]/td[2]/div/div[contains(@class, 'radioIcon')]").get_attribute("title")
                    except:
                        tipo_conexao = "Desconhecido"
                    
                    cliente_info = {
                        "nome": nome_cliente,
                        "ip": ip_cliente,
                        "mac": mac_cliente,
                        "conexao": tipo_conexao
                    }

                    lista_clientes.append(cliente_info)

            except Exception as e:
                print(f"Erro ao coletar dados de um cliente: {e}")

        # Exibe as informações coletadas
        if lista_clientes:
            print("Lista de Clientes:")
            for cliente in lista_clientes:
                print(cliente)
        else:
            print("Nenhum cliente encontrado.")

        # Mudar de volta para o contexto principal
        driver.switch_to.default_content()

    finally:
        time.sleep(2)
        driver.quit()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Configura a rede do roteador.")
    parser.add_argument("--ip", required=True, help="Endereço IP do roteador")
    parser.add_argument("--username", required=True, help="Usuário de administrador do roteador")
    parser.add_argument("--password", required=True, help="Senha de administrador do roteador")

    args = parser.parse_args()

    configurar_rede(args.ip, args.username, args.password)