import time
import argparse
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def configurar_rede(ip, senha_admin, nome1_rede, senha1_rede, nome2_rede, senha2_rede):
    url = f"http://{ip}/"
    print(f"Acessando URL do roteador: {url}")

    # Inicia o ChromeDriver
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
    except Exception as e:
        print("Erro ao iniciar o ChromeDriver:", str(e))
        return

    try:
        driver.get(url)
        print("Carregando URL do roteador.")

        # Login no sistema
        campo_senha = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="local-pwd-tb"]/div[2]/div[1]/span[2]/input[1]'))
        )
        campo_senha.send_keys(senha_admin)
        print("Senha do roteador inserida.")

        botao_entrar = driver.find_element(By.XPATH, '//*[@id="local-login-button"]/div[2]/div[1]/a')
        botao_entrar.click()
        print("Botão de login clicado.")
        time.sleep(5)  # Espera para garantir que o login foi processado

        # Navegação para a seção de configurações de rede wireless
        botao_wireless = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#main-menu > div > div.widget-wrap.navigator-wrap > ul > li:nth-child(3) > a > span.sub-navigator-icon"))
        )
        botao_wireless.click()
        time.sleep(5)  # Espera para garantir que a seção wireless seja carregada

        # Configurar Rede 2.4 GHz
        ssid_2_4_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "widget--4291c95f-a134-dacf-e9a9-0c5fa42bfd8f"))
        )
        ssid_2_4_field.clear()
        ssid_2_4_field.send_keys(nome1_rede)
        print("Nome da rede 2.4 GHz configurado.")

        senha_2_4_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "widget--07ceabd1-d134-dacf-e9a9-0ccaa8d916c9"))
        )
        senha_2_4_field.clear()
        senha_2_4_field.send_keys(senha1_rede)
        print("Senha da rede 2.4 GHz configurada.")

        # Configurar Rede 5 GHz
        ssid_5_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#widget--8472554e-6134-dace-15f6-a953446ac868 > div.widget-wrap-outer.text-wrap-outer > div.widget-wrap.text-wrap > span.text-wrap-inner > input[type="text"]'))
        )
        ssid_5_field.clear()
        ssid_5_field.send_keys(nome2_rede)
        print("Nome da rede 5 GHz configurado.")

        senha_5_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#widget--40969dbd-f134-dace-15f6-a9529940bd39 > div.widget-wrap-outer.text-wrap-outer > div.widget-wrap.text-wrap > span.text-wrap-inner > input[type="text"]'))
        )
        senha_5_field.clear()
        senha_5_field.send_keys(senha2_rede)
        print("Senha da rede 5 GHz configurada.")

        # Verificar e trocar para iframe, se necessário
        try:
            iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            driver.switch_to.frame(iframe)
            print("Mudou para o iframe.")
        except Exception:
            print("Iframe não encontrado ou não necessário.")

        # Localizar e rolar até o botão de Salvar
        botao_salvar = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#save-data > div.widget-wrap-outer.button-wrap-outer > div.widget-wrap.button-wrap > a'))
        )
        
        # Rolagem para garantir visibilidade do botão
        driver.execute_script("arguments[0].scrollIntoView(true);", botao_salvar)
        time.sleep(2)  # Dê um tempo para rolagem
        
        # Tentativa de clique com JavaScript, caso o clique padrão não funcione
        try:
            driver.execute_script("arguments[0].click();", botao_salvar)
            print("Tentativa de clique no botão de salvar usando JavaScript.")
        except Exception as e:
            print("Erro ao tentar clicar no botão de salvar com JavaScript:", str(e))

        # Verificar se há erros no console do navegador
        logs = driver.get_log("browser")
        for entry in logs:
            print("Log do navegador:", entry)
        
        time.sleep(5)  # Espera para garantir que as configurações sejam aplicadas
        
    except Exception as e:
        print("Erro ao configurar a rede:", str(e))
    finally:
        driver.quit()

if __name__ == "__main__":
    # Configuração do parser de argumentos
    parser = argparse.ArgumentParser(description="Configura a rede do roteador.")
    parser.add_argument("--ip", required=True, help="Endereço IP do roteador")
    parser.add_argument("--password", required=True, help="Senha de administrador do roteador")
    parser.add_argument("--ssid1", required=True, help="Nome da rede 2.4 GHz")
    parser.add_argument("--senha1", required=True, help="Senha da rede 2.4 GHz")
    parser.add_argument("--ssid2", required=True, help="Nome da rede 5 GHz")
    parser.add_argument("--senha2", required=True, help="Senha da rede 5 GHz")

    args = parser.parse_args()

    # Chama a função principal com os argumentos
    configurar_rede(args.ip, args.password, args.ssid1, args.senha1, args.ssid2, args.senha2)
