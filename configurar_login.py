import keyring
import tkinter as tk
from tkinter import messagebox

SERVICE_NAME = "RunrunBot"

def salvar():
    email = entry_email.get()
    senha = entry_senha.get()

    if not email or not senha:
        messagebox.showwarning("Aviso", "Preencha email e senha!")
        return

    # salva no Windows Credential Manager
    keyring.set_password(SERVICE_NAME, "email", email)
    keyring.set_password(SERVICE_NAME, "senha", senha)

    messagebox.showinfo("Sucesso", "Credenciais salvas com sucesso!")
    janela.destroy()

# janela principal
janela = tk.Tk()
janela.title("Configurar Runrun Bot")
janela.geometry("350x220")
janela.resizable(False, False)

# estilo
janela.configure(bg="#f4f6f9")

frame = tk.Frame(janela, bg="white", padx=20, pady=20)
frame.pack(padx=20, pady=20, fill="both", expand=True)

# título
tk.Label(frame, text="Configuração do Runrun", font=("Arial", 14, "bold"), bg="white").pack(pady=(0, 10))

# email
tk.Label(frame, text="Email", bg="white").pack(anchor="w")
entry_email = tk.Entry(frame, width=30)
entry_email.pack(pady=(0, 10))

# senha
tk.Label(frame, text="Senha", bg="white").pack(anchor="w")
entry_senha = tk.Entry(frame, show="*", width=30)
entry_senha.pack(pady=(0, 15))

# botão
btn_salvar = tk.Button(frame, text="Salvar", bg="#4CAF50", fg="white", width=20, command=salvar)
btn_salvar.pack()

janela.mainloop()