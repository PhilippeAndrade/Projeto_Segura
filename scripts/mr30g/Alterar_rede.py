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
        time.sleep(5)

        # Navegação nas configurações de rede
        botao_avancado = driver.find_element(By.XPATH, "//span[@class='sub-navigator-text' and text()='Avançado']")
        botao_avancado.click()
        time.sleep(5)

        botao_configuracaorapida = driver.find_element(By.XPATH, "//span[@class='sub-navigator-text' and text()='Configuração Rápida']")
        botao_configuracaorapida.click()
        time.sleep(5)

        # Configurar Rede 2.4 GHz
        nome1_rede_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[1]/div[2]/div[2]/div[2]/div[3]/div[2]/div[2]/div[2]/div[1]/span[2]/input'))
        )
        nome1_rede_field.clear()
        nome1_rede_field.send_keys(nome1_rede)

        senha1_rede_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[1]/div[2]/div[2]/div[2]/div[3]/div[2]/div[3]/div[2]/div[1]/span[2]/input'))
        )
        senha1_rede_field.clear()
        senha1_rede_field.send_keys(senha1_rede)

        # Configurar Rede 5 GHz
        nome2_rede_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[1]/div[2]/div[2]/div[2]/div[4]/div/div[2]/div[2]/div[2]/div[1]/span[2]/input'))
        )
        nome2_rede_field.clear()
        nome2_rede_field.send_keys(nome2_rede)

        senha2_rede_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[1]/div[2]/div[2]/div[2]/div[4]/div/div[2]/div[3]/div[2]/div[1]/span[2]/input'))
        )
        senha2_rede_field.clear()
        senha2_rede_field.send_keys(senha2_rede)

        print("Configurações de rede atualizadas.")
        time.sleep(2)

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
