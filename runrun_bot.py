from playwright.sync_api import sync_playwright
import keyring
import traceback

SERVICE_NAME = "RunrunBot"

try:
    # pegar credenciais
    email = keyring.get_password(SERVICE_NAME, "email")
    senha = keyring.get_password(SERVICE_NAME, "senha")

    if not email or not senha:
        print("Credenciais não encontradas! Execute o configurar_login.exe primeiro.")
        input("Pressione ENTER para sair...")
        exit()

    print("Digite os títulos das tarefas (uma por linha).")
    print("Pressione ENTER vazio para iniciar.\n")

    tarefas = []
    while True:
        linha = input()
        if linha == "":
            break
        tarefas.append(linha)

    if len(tarefas) == 0:
        print("Nenhuma tarefa informada.")
        input("Pressione ENTER para sair...")
        exit()

    print(f"{len(tarefas)} tarefas serão criadas.")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            channel="chrome"  # usa o Chrome instalado no PC
        )
        page = browser.new_page()

        page.goto("https://app.runrun.it/pt-BR/user_session/new")

        # LOGIN
        page.fill("input[type='email']", email)
        page.fill("input[type='password']", senha)
        page.click("button[type='submit']")

        print("Login realizado!")

        page.wait_for_selector("[data-testid='task-card']")

        for titulo_tarefa in tarefas:

            print(f"\nCriando tarefa: {titulo_tarefa}")

            primeira_tarefa = page.locator("[data-testid='task-card']").first

            primeira_tarefa.locator("i.fa-ellipsis-h").click()
            page.locator("i.fa-clone").click()

            campo_titulo = page.locator("input[value*='cópia']").first
            campo_titulo.wait_for()

            campo_titulo.click()
            campo_titulo.press("Control+A")
            campo_titulo.press("Backspace")
            campo_titulo.type(titulo_tarefa)

            page.get_by_role("button", name="Clonar").click()

            page.get_by_text(titulo_tarefa, exact=True).first.wait_for()

            print("Abrindo tarefa criada...")

            page.get_by_text(titulo_tarefa, exact=True).first.click()

            page.wait_for_selector("span[role='button']:has-text('00h00')")

            print("Abrindo campo de tempo...")

            page.locator("span[role='button']:has-text('00h00')").click()

            secao_tempo = page.locator("div:has-text('Tempo investido')")
            botao_plus = secao_tempo.locator("button:has(i.fa-plus)").first

            botao_plus.wait_for()
            botao_plus.click()

            campo_tempo = page.locator("input[data-testid='input-editor']").first
            campo_tempo.wait_for()

            campo_tempo.click()
            campo_tempo.press("Control+A")
            campo_tempo.press("Backspace")
            campo_tempo.type("00:10")

            print("Confirmando tempo")

            page.get_by_test_id("modal-wrapper").get_by_role("button", name="Adicionar").click()

            page.wait_for_selector("input[data-testid='input-editor']", state="hidden")

            print("Voltando para o board...")

            page.goto("https://app.runrun.it/pt-BR/boards")
            page.wait_for_selector("[data-testid='task-card']")

    print("\nProcesso finalizado com sucesso!")

except Exception as e:
    print("\nERRO DETECTADO:\n")
    print(e)
    print("\nDETALHES:")
    traceback.print_exc()

finally:
    input("\nPressione ENTER para fechar...")