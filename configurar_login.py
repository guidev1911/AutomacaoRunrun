import json

print("CONFIGURAÇÃO DO RUNRUN")

email = input("Email: ")
senha = input("Senha: ")

config = {
    "email": email,
    "senha": senha
}

with open("config.json", "w") as f:
    json.dump(config, f, indent=4)

print("Login salvo com sucesso!")