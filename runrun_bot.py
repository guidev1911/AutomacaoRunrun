import json
from playwright.sync_api import sync_playwright

with open("config.json") as f:
    config = json.load(f)

print("Abrindo navegador...")

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(
        "https://app.runrun.it/pt-BR/user_session/new",
        wait_until="domcontentloaded"
    )

    # esperar o campo de email aparecer
    page.wait_for_selector("input[type='email']", timeout=60000)

    # preencher login
    page.fill("input[type='email']", config["email"])
    page.fill("input[type='password']", config["senha"])

    # clicar no botão entrar
    page.click("button[type='submit']")

    print("Login enviado!")

    page.wait_for_timeout(8000)