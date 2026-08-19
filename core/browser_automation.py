import keyring
import time
import re
from playwright.sync_api import sync_playwright
from config.constants import SERVICE_NAME


def executar_bot(tarefas, logger):
    if not tarefas:
        raise ValueError("Adicione pelo menos uma tarefa antes de iniciar a automação.")

    email = keyring.get_password(SERVICE_NAME, "email")
    senha = keyring.get_password(SERVICE_NAME, "senha")

    if not email or not senha:
        raise ValueError("Credenciais não encontradas!")

    logger("🚀 Iniciando automação...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        page = browser.new_page()

        page.goto("https://app.runrun.it/pt-BR/user_session/new")
        page.fill("input[type='email']", email)
        page.fill("input[type='password']", senha)
        page.click("button[type='submit']")
        page.wait_for_selector("[data-testid='task-card']")

        logger("✅ Login realizado")

        for t in tarefas:
            titulo = t["titulo"]
            imagem = t["imagem"]

            logger(f"📌 Criando: {titulo}")

            clone_card = page.locator(
                "[data-testid='task-card']"
            ).filter(
                has_text="CLONE"
            ).first

            clone_card.wait_for()

            box = clone_card.bounding_box()

            page.mouse.move(
                box["x"] + box["width"] - 15,
                box["y"] + 15
            )

            page.wait_for_timeout(200)

            page.mouse.click(
                box["x"] + box["width"] - 15,
                box["y"] + 15
            )

            page.wait_for_timeout(200)

            page.locator("i.fa-solid.fa-clone").click()

            campo = page.locator("input[value*='cópia']").first
            campo.wait_for()

            campo.click()
            campo.press("Control+A")
            campo.press("Backspace")

            uid = str(int(time.time() * 1000))
            titulo_unico = f"{titulo} ##{uid}"

            campo.type(titulo_unico)

            page.get_by_role("button", name="Clonar").click()

            task = page.get_by_text(
                f"##{uid}",
                exact=False
            ).first

            task.wait_for()
            task.click()

            logger("✏️ Limpando identificador do título...")

            botao_editar = page.locator(
                f"[data-testid='inline-editor-change']:has-text('##{uid}')"
            )

            botao_editar.wait_for()
            botao_editar.scroll_into_view_if_needed()
            botao_editar.click()

            campo_titulo = page.locator(
                "[data-testid='input-editor-without-mask']"
            )

            campo_titulo.wait_for()
            campo_titulo.fill(titulo)
            campo_titulo.press("Enter")

            logger("📂 Abrindo opções da tarefa...")

            page.locator("div").filter(
                has_text=re.compile(
                    r"^DescriçãoRequisitos da etapaComentáriosEmailsAnexosSubtarefasRegras$"
                )
            ).first.click()

            page.wait_for_timeout(300)


            logger("📝 Clicando na aba Descrição...")

            page.get_by_role(
                "tab",
                name="Descrição"
            ).click()

            page.wait_for_timeout(500)

            logger("✅ Aba Descrição selecionada")

            logger("🖼️ Adicionando imagem...")

            with page.expect_file_chooser() as fc_info:
                page.locator("button.ql-image").click()

            fc_info.value.set_files(imagem)

            page.wait_for_timeout(1500)

            page.wait_for_selector(
                "span[role='button']:has-text('00h00')"
            )

            page.locator(
                "span[role='button']:has-text('00h00')"
            ).click()

            secao = page.locator(
                "div:has-text('Tempo investido')"
            )

            botao_plus = secao.locator(
                "button:has(i.fa-plus)"
            ).first

            botao_plus.wait_for()
            botao_plus.click()

            campo_tempo = page.locator(
                "input[data-testid='input-editor']"
            ).first

            campo_tempo.wait_for()
            campo_tempo.click()

            campo_tempo.press("Control+A")
            campo_tempo.press("Backspace")

            campo_tempo.type(
                "00:10",
                delay=50
            )

            campo_tempo.press("Tab")

            page.wait_for_timeout(300)

            page.get_by_test_id(
                "modal-wrapper"
            ).get_by_role(
                "button",
                name="Adicionar"
            ).click()

            logger("⏳ Aguardando tempo ser aplicado...")

            page.wait_for_selector(
                "span[role='button']:has-text('00h10')",
                timeout=5000
            )

            logger("✅ Tempo aplicado com sucesso")

            page.locator(
                "[data-testid='close-modal-button']"
            ).click()

            page.wait_for_timeout(500)

            logger("⏳ Aguardando botão de entrega...")

            botao_entregar = page.locator(
                "[data-onboarding='taskshow-deliver-button']"
            )

            botao_entregar.wait_for()

            page.wait_for_timeout(1500)

            logger("🚀 Tentando entregar tarefa...")

            try:
                botao_entregar.click()
            except Exception:
                page.wait_for_timeout(1000)
                botao_entregar.click()

            page.wait_for_timeout(2000)

            logger("✅ Tarefa entregue!")

            page.goto(
                "https://app.runrun.it/pt-BR/boards"
            )

            page.wait_for_selector(
                "[data-testid='task-card']"
            )

        browser.close()

    logger("🎉 Processo finalizado com sucesso!")

    return True