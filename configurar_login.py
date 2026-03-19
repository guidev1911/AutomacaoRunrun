import keyring

SERVICE_NAME = "RunrunBot"

print("CONFIGURAÇÃO DO RUNRUN\n")

email = input("Email: ")
senha = input("Senha: ")

# salva no Windows Credential Manager
keyring.set_password(SERVICE_NAME, "email", email)
keyring.set_password(SERVICE_NAME, "senha", senha)

print("\nCredenciais salvas com segurança no Windows Credential Manager!")
