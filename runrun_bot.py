from playwright.sync_api import sync_playwright
import keyring
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import traceback
import os

SERVICE_NAME = "RunrunBot"

tarefas = []
imagem_temp = None

# ------------------ LOG ------------------
def log(msg):
    text_log.insert(tk.END, msg + "\n")
    text_log.see(tk.END)

# ------------------ IMAGEM ------------------
def selecionar_imagem():
    global imagem_temp

    path = filedialog.askopenfilename(
        title="Selecionar imagem",
        filetypes=[("Imagens", "*.png *.jpg *.jpeg")]
    )

    if path:
        imagem_temp = path
        label_imagem.config(text=f"📷 {os.path.basename(path)}")


def drop_imagem(event):
    global imagem_temp

    path = event.data.strip().replace("{", "").replace("}", "")

    if path.lower().endswith((".png", ".jpg", ".jpeg")):
        imagem_temp = path
        label_imagem.config(text=f"📷 {os.path.basename(path)}")
    else:
        messagebox.showwarning("Erro", "Arquivo inválido!")

# ------------------ ADICIONAR ------------------
def adicionar_tarefa():
    global imagem_temp

    titulo = entry_titulo.get().strip()

    if not titulo:
        messagebox.showwarning("Atenção", "Informe o título da tarefa!")
        return

    if not imagem_temp:
        messagebox.showwarning("Atenção", "Adicione o print da OS!")
        return

    tarefas.append({
        "titulo": titulo,
        "imagem": imagem_temp
    })

    atualizar_lista()

    entry_titulo.delete(0, tk.END)
    label_imagem.config(text="Nenhuma imagem selecionada")
    imagem_temp = None


def atualizar_lista():
    lista.delete(0, tk.END)

    for i, t in enumerate(tarefas, start=1):
        lista.insert(tk.END, f"{i}. {t['titulo']}  |  {os.path.basename(t['imagem'])}")

# ------------------ REMOVER ------------------
def remover_tarefa():
    selecionado = lista.curselection()

    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione uma tarefa para remover!")
        return

    index = selecionado[0]

    tarefas.pop(index)
    atualizar_lista()

# ------------------ BOT ------------------
def executar_bot():
    try:
        if not tarefas:
            messagebox.showwarning("Atenção", "Adicione pelo menos uma tarefa!")
            return

        email = keyring.get_password(SERVICE_NAME, "email")
        senha = keyring.get_password(SERVICE_NAME, "senha")

        if not email or not senha:
            messagebox.showerror("Erro", "Credenciais não encontradas!")
            return

        log("🚀 Iniciando automação...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, channel="chrome")
            page = browser.new_page()

            page.goto("https://app.runrun.it/pt-BR/user_session/new")

            page.fill("input[type='email']", email)
            page.fill("input[type='password']", senha)
            page.click("button[type='submit']")

            page.wait_for_selector("[data-testid='task-card']")
            log("✅ Login realizado")

            for t in tarefas:
                titulo = t["titulo"]
                imagem = t["imagem"]

                log(f"📌 Criando: {titulo}")

                primeira = page.locator("[data-testid='task-card']").first
                primeira.locator("i.fa-ellipsis-h").click()
                page.locator("i.fa-clone").click()

                campo = page.locator("input[value*='cópia']").first
                campo.wait_for()

                campo.click()
                campo.press("Control+A")
                campo.press("Backspace")
                campo.type(titulo)

                page.get_by_role("button", name="Clonar").click()

                page.get_by_text(titulo, exact=True).first.wait_for()
                page.get_by_text(titulo, exact=True).first.click()

                page.wait_for_selector("button.ql-image")

                with page.expect_file_chooser() as fc_info:
                    page.click("button.ql-image")

                fc_info.value.set_files(imagem)

                page.wait_for_timeout(1500)

                page.wait_for_selector("span[role='button']:has-text('00h00')")
                page.locator("span[role='button']:has-text('00h00')").click()

                secao = page.locator("div:has-text('Tempo investido')")
                botao_plus = secao.locator("button:has(i.fa-plus)").first

                botao_plus.wait_for()
                botao_plus.click()

                campo_tempo = page.locator("input[data-testid='input-editor']").first
                campo_tempo.wait_for()

                campo_tempo.click()
                campo_tempo.press("Control+A")
                campo_tempo.press("Backspace")
                campo_tempo.type("00:10")

                page.get_by_test_id("modal-wrapper").get_by_role("button", name="Adicionar").click()

                page.wait_for_selector("input[data-testid='input-editor']", state="hidden")

                page.goto("https://app.runrun.it/pt-BR/boards")
                page.wait_for_selector("[data-testid='task-card']")

        log("🎉 Processo finalizado com sucesso!")

        # 🔥 LIMPAR LISTA
        tarefas.clear()
        lista.delete(0, tk.END)

    except Exception as e:
        log("❌ ERRO")
        log(str(e))
        traceback.print_exc()

# thread
def iniciar():
    threading.Thread(target=executar_bot).start()

# ------------------ UI ------------------
janela = TkinterDnD.Tk()
janela.title("Runrun Bot - Automação")
janela.geometry("900x750")  # 🔥 maior
janela.configure(bg="#eef1f5")

frame = tk.Frame(janela, bg="white", padx=20, pady=20)
frame.pack(fill="both", expand=True, padx=20, pady=20)

tk.Label(frame, text="🚀 Automação de Tarefas no Runrun", font=("Segoe UI", 16, "bold"), bg="white").pack()

entry_titulo = tk.Entry(frame, font=("Segoe UI", 11))
entry_titulo.pack(fill="x", pady=10, ipady=5)

drop_area = tk.Label(frame, text="Arraste a imagem aqui OU use o botão abaixo", bg="#ddd", height=4)
drop_area.pack(fill="x", pady=10)

drop_area.drop_target_register(DND_FILES)
drop_area.dnd_bind("<<Drop>>", drop_imagem)

tk.Button(frame, text="📷 Selecionar imagem", command=selecionar_imagem).pack()

label_imagem = tk.Label(frame, text="Nenhuma imagem selecionada", bg="white")
label_imagem.pack(pady=5)

tk.Button(frame, text="➕ Adicionar tarefa", bg="#1976d2", fg="white", command=adicionar_tarefa).pack(fill="x", pady=10)

lista = tk.Listbox(frame, height=10)
lista.pack(fill="both", expand=True)

# 🔥 BOTÃO REMOVER
tk.Button(frame, text="❌ Remover tarefa selecionada", bg="#e53935", fg="white", command=remover_tarefa).pack(fill="x", pady=5)

tk.Button(frame, text="▶ Iniciar automação", bg="#4CAF50", fg="white", command=iniciar).pack(fill="x", pady=10)

text_log = tk.Text(frame, height=10, bg="#111", fg="#0f0")
text_log.pack(fill="both", expand=True)

janela.mainloop()