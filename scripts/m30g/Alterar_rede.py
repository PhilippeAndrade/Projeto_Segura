import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import argparse

def configurar_rede(ip, senha_admin, nome1_rede, senha1_rede, nome2_rede, senha2_rede):
    url = f"http://{ip}/"
    print(f"Acessando URL do roteador: {url}")

    # Configura o ChromeDriver usando o webdriver_manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
        driver.get(url)
        actions = ActionChains(driver)

        # Campo de senha
        campo_senha = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="local-pwd-tb"]/div[2]/div[1]/span[2]/input[1]'))
        )
        campo_senha.send_keys(senha_admin)
        time.sleep(2)

        # Botão Entrar
        botao_entrar = driver.find_element(By.XPATH, '//*[@id="local-login-button"]/div[2]/div[1]/a')
        botao_entrar.click()
        time.sleep(5)

        # Navegação para "Avançado" e "Configuração Rápida"
        botao_avancado = driver.find_element(By.XPATH, "//span[@class='sub-navigator-text' and text()='Avançado']")
        botao_avancado.click()
        time.sleep(5)

        botao_configuracaorapida = driver.find_element(By.XPATH, "//span[@class='sub-navigator-text' and text()='Configuração Rápida']")
        botao_configuracaorapida.click()
        time.sleep(5)


        pular = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[4]/div[2]/div[1]/a/span[2]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", pular)

        botao_pular =  WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[4]/div[2]/div[1]/a/span[2]'))
        )
        botao_pular.click()

        # Configuração da rede 2.4 GHz
        nome1_elemento = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[1]/div[2]/div[2]/div[2]/div[3]/div[2]/div[2]/div[2]/div[1]/span[2]/input'))
        )
        nome1_elemento.click()
        nome1_elemento.clear()
        nome1_elemento.send_keys(nome1_rede)
        
        senha1_elemento = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[1]/div[2]/div[2]/div[2]/div[3]/div[2]/div[3]/div[2]/div[1]/span[2]/input'))
        )
        senha1_elemento.click()
        senha1_elemento.clear()
        senha1_elemento.send_keys(senha1_rede)

        # Configuração da rede 5 GHz
        nome2_elemento = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[1]/div[2]/div[2]/div[2]/div[4]/div/div[2]/div[2]/div[2]/div[1]/span[2]/input'))
        )
        nome2_elemento.click()
        nome2_elemento.clear()
        nome2_elemento.send_keys(nome2_rede)
        
        senha2_elemento = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[1]/div[2]/div[2]/div[2]/div[4]/div/div[2]/div[3]/div[2]/div[1]/span[2]/input'))
        )
        senha2_elemento.click()
        senha2_elemento.clear()
        senha2_elemento.send_keys(senha2_rede)

        # Avançar e finalizar
        botao_proximo = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]/div[2]/div[1]/a'))
        )
        botao_proximo.click()

        finalizar = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div[5]/div/div/div[2]/div[2]/div[2]/div[4]/div[2]/div[1]/a'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", finalizar)
        finalizar.click()
    finally:
        time.sleep(3)
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
