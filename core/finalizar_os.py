import time
import keyring

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from urllib.parse import quote

SERVICE_NAME_DETRAN = "BOT_DETRAN"

def executar_finalizar_os(logger):


    usuario_intr = keyring.get_password(
        SERVICE_NAME_DETRAN,
        "usuario_intr"
    )

    senha_intr = keyring.get_password(
        SERVICE_NAME_DETRAN,
        "senha_intr"
    )

    usuario_portal = keyring.get_password(
        SERVICE_NAME_DETRAN,
        "usuario_portal"
    )

    senha_portal = keyring.get_password(
        SERVICE_NAME_DETRAN,
        "senha_portal"
    )

    if (
        not usuario_intr
        or not senha_intr
        or not usuario_portal
        or not senha_portal
    ):
        raise ValueError(
            "Credenciais do DETRAN não encontradas!"
        )

    logger("🚀 Iniciando automação Finalizar OS...")
    logger("🌐 Abrindo navegador...")

    options = Options()

    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-logging"]
    )

    service = Service()

    driver = webdriver.Chrome(
        service=service,
        options=options
    )

    driver.maximize_window()

    wait = WebDriverWait(
        driver,
        15
    )

    try:

        logger("🔐 Acessando Intranet...")

        senha_url = quote(
            senha_intr
        )

        usuario_url = quote(
            usuario_intr
        )

        url_intranet = (
            f"http://{usuario_url}:{senha_url}"
            "@intranet.detran.gov-se/novo_inicio.asp"
        )

        driver.get(
            url_intranet
        )

        token_element = wait.until(
            EC.presence_of_element_located(
                (
                    By.ID,
                    "divNumeroToken"
                )
            )
        )

        wait.until(
            lambda d: token_element.text.strip() != ""
        )

        token = token_element.text.strip()

        logger(
            "✅ Token obtido com sucesso"
        )

        logger(
            "🔐 Acessando Portal DETRAN..."
        )

        driver.get(
            "http://portal.detran.gov-se/default.asp"
            "?pg=login&redir=ordem_servico_fila"
        )

        wait.until(
            EC.presence_of_element_located(
                (
                    By.ID,
                    "nscUser"
                )
            )
        )

        driver.find_element(
            By.ID,
            "nscUser"
        ).send_keys(
            usuario_portal
        )

        driver.find_element(
            By.ID,
            "nscPwd"
        ).send_keys(
            senha_portal
        )

        driver.find_element(
            By.ID,
            "nrToken"
        ).send_keys(
            token
        )

        logger(
            "🚀 Realizando login..."
        )

        botao_confirmar = wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "btSubmeter"
                )
            )
        )

        botao_confirmar.click()

        wait.until(
            lambda d:
            d.current_url
            !=
            "http://portal.detran.gov-se/default.asp"
            "?pg=login&redir=ordem_servico_fila"
        )

        logger(
            "✅ Login realizado com sucesso"
        )

        logger(
            "📋 Acessando fila de Ordens de Serviço..."
        )

        wait.until(
            EC.presence_of_element_located(
                (
                    By.ID,
                    "fsOrdemServico"
                )
            )
        )

        select_element = wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "codAtendimento"
                )
            )
        )

        select = Select(
            select_element
        )

        select.select_by_visible_text(
            "Suporte de Equipamentos"
        )

        botao_confirmar = wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "btSubmeter"
                )
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            botao_confirmar
        )

        logger(
            "✅ Setor selecionado: Suporte de Equipamentos"
        )

        logger(
            "👀 Monitorando novas Ordens de Serviço..."
        )

        os_anteriores = set()

        while True:

            if not driver.service.process:

                logger(
                    "⚠️ Navegador foi encerrado."
                )

                break

            try:

                botao_fila = WebDriverWait(
                    driver,
                    10
                ).until(
                    EC.element_to_be_clickable(
                        (
                            By.NAME,
                            "btFila"
                        )
                    )
                )

                driver.execute_script(
                    "arguments[0].click();",
                    botao_fila
                )

                WebDriverWait(
                    driver,
                    10
                ).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            "#tblForm > tbody > tr"
                        )
                    )
                )

                linhas = driver.find_elements(
                    By.CSS_SELECTOR,
                    "#tblForm > tbody > tr"
                )

                os_atual = set()

                for linha in linhas:

                    try:

                        colunas = linha.find_elements(
                            By.TAG_NAME,
                            "td"
                        )

                        if len(colunas) == 7:

                            numero = colunas[0].text.strip()

                            if numero.isdigit():

                                os_atual.add(
                                    numero
                                )

                    except Exception:

                        continue

                novas = (
                    os_atual
                    -
                    os_anteriores
                )

                if novas:

                    lista_os = "\n".join(
                        sorted(
                            novas
                        )
                    )

                    logger(
                        "🚨 NOVAS OS DETECTADAS:"
                    )

                    logger(
                        lista_os
                    )

                os_anteriores = os_atual

            except Exception as e:

                logger(
                    f"⚠️ Monitoramento encerrado: {e}"
                )

                break

            time.sleep(
                60
            )

    finally:

        logger(
            "🛑 Encerrando automação Finalizar OS..."
        )

        try:

            driver.quit()

        except Exception:

            pass

