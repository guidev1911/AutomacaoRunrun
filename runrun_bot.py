import json
from playwright.sync_api import sync_playwright


with open("config.json") as f:
    config = json.load(f)

titulo = input("Titulo da tarefa: ")
print_file = input("Caminho do print: ")

print("Abrindo navegador...")

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://app.runrun.it")

    page.wait_for_timeout(3000)

    page.fill("#user_email", config["email"])
    page.fill("#user_password", config["senha"])

    page.click("button[type=submit]")

    print("Login realizado!")

    page.wait_for_timeout(5000)