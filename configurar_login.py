import keyring
import tkinter as tk
from tkinter import messagebox

SERVICE_NAME = "RunrunBot"

def salvar():
    email = entry_email.get()
    senha = entry_senha.get()

    if not email or not senha:
        messagebox.showwarning("Atenção", "Preencha email e senha!")
        return

    keyring.set_password(SERVICE_NAME, "email", email)
    keyring.set_password(SERVICE_NAME, "senha", senha)

    messagebox.showinfo("Sucesso", "Credenciais salvas!\nA automação já pode ser executada.")


def limpar_credenciais():
    confirmar = messagebox.askyesno(
        "Confirmar",
        "Deseja realmente remover as credenciais salvas?"
    )

    if not confirmar:
        return

    try:
        keyring.delete_password(SERVICE_NAME, "email")
        keyring.delete_password(SERVICE_NAME, "senha")
    except:
        pass

    entry_email.delete(0, tk.END)
    entry_senha.delete(0, tk.END)

    messagebox.showinfo("Removido", "Credenciais apagadas com sucesso!")


# ------------------ JANELA ------------------
janela = tk.Tk()
janela.title("Runrun Bot - Configuração")
janela.geometry("420x360")
janela.resizable(False, False)
janela.configure(bg="#eef1f5")

# ------------------ CARD ------------------
frame = tk.Frame(janela, bg="white", padx=25, pady=25)
frame.place(relx=0.5, rely=0.5, anchor="center")

# ------------------ TÍTULO ------------------
tk.Label(
    frame,
    text="⚙️ Configurar Runrun Bot",
    font=("Segoe UI", 16, "bold"),
    bg="white",
    fg="#333"
).pack(pady=(0, 10))

# ------------------ DESCRIÇÃO ------------------
tk.Label(
    frame,
    text="Informe seu email e senha do Runrun.\n"
         "Esses dados serão usados para executar a automação automaticamente.\n"
         "Você pode alterar ou remover quando quiser.",
    font=("Segoe UI", 9),
    bg="white",
    fg="#666",
    justify="center"
).pack(pady=(0, 15))

# ------------------ EMAIL ------------------
tk.Label(frame, text="Email", bg="white", fg="#333", font=("Segoe UI", 9, "bold")).pack(anchor="w")
entry_email = tk.Entry(frame, font=("Segoe UI", 10), bd=1, relief="solid")
entry_email.pack(fill="x", pady=(5, 15), ipady=5)

# preencher automaticamente se existir
email_salvo = keyring.get_password(SERVICE_NAME, "email")
if email_salvo:
    entry_email.insert(0, email_salvo)

# ------------------ SENHA ------------------
tk.Label(frame, text="Senha", bg="white", fg="#333", font=("Segoe UI", 9, "bold")).pack(anchor="w")
entry_senha = tk.Entry(frame, show="*", font=("Segoe UI", 10), bd=1, relief="solid")
entry_senha.pack(fill="x", pady=(5, 20), ipady=5)

# ------------------ BOTÕES ------------------
btn_salvar = tk.Button(
    frame,
    text="Salvar e Ativar Automação",
    font=("Segoe UI", 10, "bold"),
    bg="#4CAF50",
    fg="white",
    activebackground="#43a047",
    activeforeground="white",
    bd=0,
    cursor="hand2",
    command=salvar
)
btn_salvar.pack(fill="x", ipady=8)

btn_limpar = tk.Button(
    frame,
    text="🗑️ Limpar credenciais",
    font=("Segoe UI", 9),
    bg="#e53935",
    fg="white",
    activebackground="#d32f2f",
    activeforeground="white",
    bd=0,
    cursor="hand2",
    command=limpar_credenciais
)
btn_limpar.pack(fill="x", pady=(10, 0), ipady=6)

# ------------------ RODAR ------------------
janela.mainloop()