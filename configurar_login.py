import customtkinter as ctk
import keyring

SERVICE_NAME_RUNRUN = "RunrunBot"
SERVICE_NAME_DETRAN = "BOT_DETRAN"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


def salvar():
    email = entry_email.get()
    senha = entry_senha.get()
    usuario_intr = entry_intr_user.get()
    senha_intr = entry_intr_pass.get()
    usuario_portal = entry_portal_user.get()
    senha_portal = entry_portal_pass.get()

    saved = []

    if email and senha:
        keyring.set_password(SERVICE_NAME_RUNRUN, "email", email)
        keyring.set_password(SERVICE_NAME_RUNRUN, "senha", senha)
        saved.append("Runrun")

    keyring.set_password(SERVICE_NAME_DETRAN, "usuario_intr", usuario_intr)
    keyring.set_password(SERVICE_NAME_DETRAN, "senha_intr", senha_intr)
    keyring.set_password(SERVICE_NAME_DETRAN, "usuario_portal", usuario_portal)
    keyring.set_password(SERVICE_NAME_DETRAN, "senha_portal", senha_portal)
    saved.append("DETRAN")

    if saved:
        message = "✔ Credenciais do " + " e ".join(saved) + " salvas com sucesso!"
        status.configure(
            text=message,
            text_color="#7CFC00"
        )
    else:
        status.configure(
            text="⚠️ Preencha pelo menos um conjunto de credenciais.",
            text_color="#F59E0B"
        )


def limpar_credenciais():
    entry_email.delete(0, "end")
    entry_senha.delete(0, "end")
    entry_intr_user.delete(0, "end")
    entry_intr_pass.delete(0, "end")
    entry_portal_user.delete(0, "end")
    entry_portal_pass.delete(0, "end")

    status.configure(
        text="Campos limpos.",
        text_color="#FBBF24"
    )


janela = ctk.CTk()
janela.title("Configurar Credenciais - Bot DETRAN")
# Ajuste leve: diminuir um pouco a altura para ficar mais equilibrada
janela.geometry("560x780")
janela.minsize(540, 740)
janela.resizable(False, False)
janela.configure(fg_color="#0f172a")

main_frame = ctk.CTkFrame(
    janela,
    corner_radius=24,
    fg_color="#111827",
    border_width=1,
    border_color="#334155"
)
main_frame.pack(fill="both", expand=True, padx=18, pady=18)
main_frame.grid_columnconfigure(0, weight=1)

header = ctk.CTkFrame(
    main_frame,
    fg_color="transparent"
)
header.grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 6))

ctk.CTkLabel(
    header,
    text="Configurar Credenciais",
    font=("Segoe UI", 22, "bold"),
    text_color="#F8FAFC"
).pack(anchor="w")

ctk.CTkLabel(
    header,
    text="Informe os logins do Runrun e do Bot DETRAN.",
    font=("Segoe UI", 12),
    text_color="#94A3B8"
).pack(anchor="w", pady=(3, 0))

fields_frame = ctk.CTkFrame(
    main_frame,
    fg_color="transparent"
)
fields_frame.grid(row=1, column=0, sticky="ew", padx=22, pady=(4, 0))
fields_frame.grid_columnconfigure(0, weight=1)

ctk.CTkLabel(
    fields_frame,
    text="Login Runrun",
    font=("Segoe UI", 15, "bold"),
    anchor="w"
).grid(row=0, column=0, sticky="w", pady=(4, 6))

ctk.CTkLabel(
    fields_frame,
    text="Email",
    font=("Segoe UI", 13, "bold"),
    anchor="w"
).grid(row=1, column=0, sticky="w", pady=(4, 3))

entry_email = ctk.CTkEntry(
    fields_frame,
    height=28,
    placeholder_text="Digite o email do Runrun"
)
entry_email.grid(row=2, column=0, sticky="ew", pady=(0, 8))

ctk.CTkLabel(
    fields_frame,
    text="Senha",
    font=("Segoe UI", 13, "bold"),
    anchor="w"
).grid(row=3, column=0, sticky="w", pady=(4, 3))

entry_senha = ctk.CTkEntry(
    fields_frame,
    height=28,
    show="*",
    placeholder_text="Digite a senha do Runrun"
)
entry_senha.grid(row=4, column=0, sticky="ew", pady=(0, 12))

ctk.CTkLabel(
    fields_frame,
    text="Finalizar OS no sistema",
    font=("Segoe UI", 15, "bold"),
    anchor="w"
).grid(row=5, column=0, sticky="w", pady=(8, 6))

ctk.CTkLabel(
    fields_frame,
    text="Usuário Intranet",
    font=("Segoe UI", 13, "bold"),
    anchor="w"
).grid(row=6, column=0, sticky="w", pady=(4, 3))

entry_intr_user = ctk.CTkEntry(
    fields_frame,
    height=28,
    placeholder_text="Digite o usuário da intranet"
)
entry_intr_user.grid(row=7, column=0, sticky="ew", pady=(0, 8))

ctk.CTkLabel(
    fields_frame,
    text="Senha Intranet",
    font=("Segoe UI", 13, "bold"),
    anchor="w"
).grid(row=8, column=0, sticky="w", pady=(4, 3))

entry_intr_pass = ctk.CTkEntry(
    fields_frame,
    height=28,
    show="*",
    placeholder_text="Digite a senha da intranet"
)
entry_intr_pass.grid(row=9, column=0, sticky="ew", pady=(0, 8))

ctk.CTkLabel(
    fields_frame,
    text="Usuário Portal",
    font=("Segoe UI", 13, "bold"),
    anchor="w"
).grid(row=10, column=0, sticky="w", pady=(4, 3))

entry_portal_user = ctk.CTkEntry(
    fields_frame,
    height=28,
    placeholder_text="Digite o usuário do portal"
)
entry_portal_user.grid(row=11, column=0, sticky="ew", pady=(0, 8))

ctk.CTkLabel(
    fields_frame,
    text="Senha Portal",
    font=("Segoe UI", 13, "bold"),
    anchor="w"
).grid(row=12, column=0, sticky="w", pady=(4, 3))

entry_portal_pass = ctk.CTkEntry(
    fields_frame,
    height=28,
    show="*",
    placeholder_text="Digite a senha do portal"
)
entry_portal_pass.grid(row=13, column=0, sticky="ew", pady=(0, 4))

saved_email = keyring.get_password(SERVICE_NAME_RUNRUN, "email")
saved_senha = keyring.get_password(SERVICE_NAME_RUNRUN, "senha")
saved_usuario_intr = keyring.get_password(SERVICE_NAME_DETRAN, "usuario_intr")
saved_senha_intr = keyring.get_password(SERVICE_NAME_DETRAN, "senha_intr")
saved_usuario_portal = keyring.get_password(SERVICE_NAME_DETRAN, "usuario_portal")
saved_senha_portal = keyring.get_password(SERVICE_NAME_DETRAN, "senha_portal")

if saved_email:
    entry_email.insert(0, saved_email)

if saved_senha:
    entry_senha.insert(0, saved_senha)

if saved_usuario_intr:
    entry_intr_user.insert(0, saved_usuario_intr)

if saved_senha_intr:
    entry_intr_pass.insert(0, saved_senha_intr)

if saved_usuario_portal:
    entry_portal_user.insert(0, saved_usuario_portal)

if saved_senha_portal:
    entry_portal_pass.insert(0, saved_senha_portal)

buttons_frame = ctk.CTkFrame(
    main_frame,
    fg_color="transparent"
)
buttons_frame.grid(row=2, column=0, sticky="w", padx=22, pady=(8, 0))

btn_salvar = ctk.CTkButton(
    buttons_frame,
    text="Salvar Credenciais",
    width=200,
    height=40,
    corner_radius=12,
    command=salvar
)
btn_salvar.pack(side="left", padx=(0, 12))

btn_limpar = ctk.CTkButton(
    buttons_frame,
    text="Limpar",
    width=120,
    height=40,
    corner_radius=12,
    fg_color="#475569",
    hover_color="#334155",
    command=limpar_credenciais
)
btn_limpar.pack(side="left")

status = ctk.CTkLabel(
    main_frame,
    text="",
    font=("Segoe UI", 12),
    wraplength=520,
    text_color="#E2E8F0"
)
status.grid(row=3, column=0, sticky="w", padx=22, pady=(8, 12))

janela.mainloop()
