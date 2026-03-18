import json
from playwright.sync_api import sync_playwright

# carregar config
with open("config.json") as f:
    config = json.load(f)

print("Digite os títulos das tarefas (uma por linha).")
print("Quando terminar, pressione ENTER duas vezes.\n")

# receber várias tarefas
tarefas = []
while True:
    linha = input()
    if linha == "":
        break
    tarefas.append(linha)

print(f"\n{len(tarefas)} tarefas serão criadas.")

print("Abrindo navegador...")

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://app.runrun.it/pt-BR/user_session/new")

    # LOGIN
    page.wait_for_selector("input[type='email']")
    page.fill("input[type='email']", config["email"])
    page.fill("input[type='password']", config["senha"])
    page.click("button[type='submit']")

    print("Login realizado!")

    page.wait_for_timeout(8000)

    # pegar primeira tarefa do backlog
    primeira_tarefa = page.locator("[data-testid='task-card']").first

    for titulo_tarefa in tarefas:

        print(f"\nClonando tarefa: {titulo_tarefa}")

        # abrir menu dos 3 pontinhos
        primeira_tarefa.locator("i.fa-ellipsis-h").click()

        page.wait_for_timeout(1500)

        # clicar em clonar
        page.locator("i.fa-clone").click()

        print("Alterando título...")

        # esperar campo de título
        page.wait_for_selector("input[value*='cópia']")

        campo_titulo = page.locator("input[value*='cópia']").first

        campo_titulo.click()

        # limpar texto
        campo_titulo.press("Control+A")
        campo_titulo.press("Backspace")

        # digitar novo titulo
        campo_titulo.type(titulo_tarefa)

        # clicar no botão final Clonar
        page.wait_for_selector("button:has-text('Clonar')")
        page.get_by_role("button", name="Clonar").click()

        page.wait_for_timeout(4000)

        print("Tarefa criada!")

    print("\nTodas as tarefas foram criadas!")

    page.wait_for_timeout(5000)

    browser.close()