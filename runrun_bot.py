import json
from playwright.sync_api import sync_playwright

# carregar config
with open("config.json") as f:
    config = json.load(f)

print("Digite os títulos das tarefas (uma por linha).")
print("Pressione ENTER vazio para iniciar.\n")

tarefas = []
while True:
    linha = input()
    if linha == "":
        break
    tarefas.append(linha)

print(f"{len(tarefas)} tarefas serão criadas.")

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://app.runrun.it/pt-BR/user_session/new")

    # LOGIN
    page.fill("input[type='email']", config["email"])
    page.fill("input[type='password']", config["senha"])
    page.click("button[type='submit']")

    print("Login realizado!")

    # esperar board carregar
    page.wait_for_selector("[data-testid='task-card']")

    primeira_tarefa = page.locator("[data-testid='task-card']").first

    for titulo_tarefa in tarefas:

        print(f"\nCriando tarefa: {titulo_tarefa}")

        # abrir menu
        primeira_tarefa.locator("i.fa-ellipsis-h").click()

        # clicar em clonar
        page.locator("i.fa-clone").click()

        # esperar campo de título
        campo_titulo = page.locator("input[value*='cópia']").first
        campo_titulo.wait_for()

        campo_titulo.click()
        campo_titulo.press("Control+A")
        campo_titulo.press("Backspace")
        campo_titulo.type(titulo_tarefa)

        # confirmar clone
        page.get_by_role("button", name="Clonar").click()

        # esperar tarefa aparecer
        page.get_by_text(titulo_tarefa, exact=True).first.wait_for()

        print("Abrindo tarefa criada...")

        page.get_by_text(titulo_tarefa, exact=True).first.click()

        # esperar painel abrir
        page.wait_for_selector("span[role='button']:has-text('00h00')")

        print("Abrindo campo de tempo...")

        page.locator("span[role='button']:has-text('00h00')").click()

        # clicar no +
        secao_tempo = page.locator("div:has-text('Tempo investido')")
        botao_plus = secao_tempo.locator("button:has(i.fa-plus)").first

        botao_plus.wait_for()
        botao_plus.click()

        # esperar campo de tempo
        campo_tempo = page.locator("input[data-testid='input-editor']").first
        campo_tempo.wait_for()

        campo_tempo.click()
        campo_tempo.press("Control+A")
        campo_tempo.press("Backspace")
        campo_tempo.type("00:10")

        print("Confirmando tempo")

        page.get_by_test_id("modal-wrapper").get_by_role("button", name="Adicionar").click()

        # esperar fechar modal
        page.wait_for_selector("input[data-testid='input-editor']", state="hidden")

        print("Voltando para o board...")

        page.goto("https://app.runrun.it/pt-BR/boards")

        page.wait_for_selector("[data-testid='task-card']")

        primeira_tarefa = page.locator("[data-testid='task-card']").first