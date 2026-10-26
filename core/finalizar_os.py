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


def aceitar_aviso_lgpd_se_exibido(driver, wait):
    botoes_aceitar = driver.find_elements(
        By.CSS_SELECTOR,
        "button.save-lgpd.botaoFull"
    )

    for botao in botoes_aceitar:
        if botao.is_displayed() and botao.is_enabled():
            botao.click()
            wait.until(
                EC.invisibility_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div.content-lgpd"
                    )
                )
            )
            return True

    return False


def executar_finalizar_os(logger, atendente, mensagem_conclusao):


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

    logger("Iniciando automação Finalizar OS...")
    logger("Abrindo navegador...")

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
    tela_fila_aberta = False

    try:

        logger("Acessando Intranet...")

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
            "Token obtido com sucesso"
        )

        logger(
            "Acessando Portal DETRAN..."
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
            "Realizando login..."
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
            "Login realizado com sucesso"
        )

        logger(
            "Acessando fila de Ordens de Serviço..."
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
            "Setor selecionado: Suporte de Equipamentos"
        )

        seletor_tabela_atendente = (
            "//table[@id='tblForm']"
            "[.//b[normalize-space(.)="
            f"'Atendente: {atendente}']]"
        )

        tabela_atendente = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    seletor_tabela_atendente
                )
            )
        )

        ordens_servico = []
        for linha in tabela_atendente.find_elements(By.TAG_NAME, "tr"):
            celulas = linha.find_elements(By.TAG_NAME, "td")
            if len(celulas) != 6:
                continue

            numero_os = celulas[0].text.strip()
            if not numero_os.isdigit():
                continue

            ordens_servico.append(
                {
                    "numero": numero_os,
                    "solicitante": celulas[1].text.strip(),
                    "situacao": celulas[4].text.strip(),
                }
            )

        logger(f"OS atribuídas a {atendente}:")
        if ordens_servico:
            for os_atribuida in ordens_servico:
                logger(
                    f"OS {os_atribuida['numero']} | "
                    f"{os_atribuida['situacao']} | "
                    f"Solicitante: {os_atribuida['solicitante']}"
                )
        else:
            logger("Nenhuma OS atribuída no momento.")

        tela_fila_aberta = True
        logger(
            "Tela de Suporte de Equipamentos aberta. "
            "Iniciando conclusão das OS listadas."
        )

        os_concluidas = 0
        for os_atribuida in ordens_servico:
            numero_os = os_atribuida["numero"]
            if aceitar_aviso_lgpd_se_exibido(driver, wait):
                logger("Aviso de privacidade aceito.")

            tabela_atendente = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        seletor_tabela_atendente
                    )
                )
            )

            linha_os = tabela_atendente.find_elements(
                By.XPATH,
                f".//tr[td[1][normalize-space(.)='{numero_os}']]"
            )
            if not linha_os:
                logger(
                    f"OS {numero_os} não está mais na fila deste "
                    "atendente; ignorando."
                )
                continue

            celulas_os = linha_os[0].find_elements(
                By.TAG_NAME,
                "td"
            )
            if len(celulas_os) != 6:
                raise RuntimeError(
                    f"Formato inesperado na linha da OS {numero_os}."
                )

            situacao_atual = celulas_os[4].text.strip()
            if situacao_atual != "EM ABERTO":
                logger(
                    f"OS {numero_os} está com situação "
                    f"'{situacao_atual}'; ignorando."
                )
                continue

            botao_concluir = tabela_atendente.find_elements(
                By.XPATH,
                ".//a[contains(@href, "
                f"'concluirOrdemServico({numero_os})')]"
            )
            if not botao_concluir:
                raise RuntimeError(
                    f"Botão Concluir não encontrado para a OS "
                    f"{numero_os}, que ainda está aberta."
                )

            logger(f"Concluindo OS {numero_os}...")
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                botao_concluir[0]
            )
            botao_concluir[0].click()

            campo_motivo = wait.until(
                EC.visibility_of_element_located(
                    (
                        By.ID,
                        "edtMotivoConclusao"
                    )
                )
            )
            campo_motivo.clear()
            campo_motivo.send_keys(mensagem_conclusao)

            botao_confirmar_conclusao = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.NAME,
                        "btConcluir"
                    )
                )
            )
            botao_confirmar_conclusao.click()

            alerta = wait.until(
                EC.alert_is_present()
            )
            mensagem_alerta = alerta.text.strip()
            alerta.accept()

            if "Ordem de Serviço Concluída com Sucesso" not in mensagem_alerta:
                raise RuntimeError(
                    f"Falha ao concluir a OS {numero_os}: "
                    f"{mensagem_alerta or 'alerta sem mensagem'}"
                )

            wait.until(
                EC.staleness_of(tabela_atendente)
            )
            wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        seletor_tabela_atendente
                    )
                )
            )

            os_concluidas += 1
            logger(f"OS {numero_os} concluída com sucesso.")

        logger(
            f"Processo finalizado: {os_concluidas} OS concluídas."
        )
        logger(
            "O navegador permanecerá aberto na tela de "
            "Suporte de Equipamentos."
        )

    finally:

        if not tela_fila_aberta:
            driver.quit()
