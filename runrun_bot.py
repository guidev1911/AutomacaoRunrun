from playwright.sync_api import sync_playwright
import keyring
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import traceback
import os
from PIL import ImageGrab
import tempfile

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

def colar_imagem():
    global imagem_temp

    img = ImageGrab.grabclipboard()

    if img is None:
        messagebox.showwarning("Erro", "Nenhuma imagem encontrada na área de transferência!")
        return

    # criar arquivo único
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    temp_path = temp_file.name
    temp_file.close()

    img.save(temp_path, "PNG")

    imagem_temp = temp_path
    label_imagem.config(text="📋 Imagem colada do print")

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

def limpar_tarefas():
    if not tarefas:
        return

    confirmar = messagebox.askyesno(
        "Confirmar",
        "Deseja remover TODAS as tarefas?"
    )

    if not confirmar:
        return

    tarefas.clear()
    lista.delete(0, tk.END)

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

# ---------------- TEMPO ----------------
                campo_tempo = page.locator("input[data-testid='input-editor']").first
                campo_tempo.wait_for()

                campo_tempo.click()
                campo_tempo.press("Control+A")
                campo_tempo.press("Backspace")

                campo_tempo.type("00:10", delay=50)


                campo_tempo.press("Tab")

                page.wait_for_timeout(300)

                page.get_by_test_id("modal-wrapper").get_by_role("button", name="Adicionar").click()

                log("⏳ Aguardando tempo ser aplicado...")

                page.wait_for_selector("span[role='button']:has-text('00h10')", timeout=5000)

                log("✅ Tempo aplicado com sucesso")
                
# ---------------- FECHAR MODAL ----------------
                page.locator("[data-testid='close-modal-button']").click()
                page.wait_for_timeout(500)

# ---------------- FINALIZAR TAREFA ----------------
                log("⏳ Aguardando botão de entrega...")

                botao_entregar = page.locator("[data-onboarding='taskshow-deliver-button']")

                botao_entregar.wait_for()

                page.wait_for_timeout(1500)

                log("🚀 Tentando entregar tarefa...")

                try:
                    botao_entregar.click()
                except:
                    page.wait_for_timeout(1000)
                    botao_entregar.click()

                page.wait_for_timeout(2000)

                log("✅ Tarefa entregue!")

# ---------------- VOLTAR ----------------
                page.goto("https://app.runrun.it/pt-BR/boards")
                page.wait_for_selector("[data-testid='task-card']")

        log("🎉 Processo finalizado com sucesso!")

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
janela.geometry("900x750")  
janela.configure(bg="#eef1f5")
janela.bind("<Control-v>", lambda e: colar_imagem())

frame = tk.Frame(janela, bg="white", padx=20, pady=20)
frame.pack(fill="both", expand=True, padx=20, pady=20)

tk.Label(frame, text="Automação de Tarefas no Runrun.it", font=("Segoe UI", 16, "bold"), bg="white").pack()

tk.Label(frame, text="Digite o título da tarefa", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w")

entry_titulo = tk.Entry(frame, font=("Segoe UI", 11))
entry_titulo.pack(fill="x", pady=10, ipady=5)

# -------- BLOCO DE IMAGEM --------
frame_imagem = tk.Frame(frame, bg="#f8f9fb", bd=1, relief="solid")
frame_imagem.pack(fill="x", pady=10)

tk.Label(
    frame_imagem,
    text="Print da OS (imagem da descrição)",
    bg="#f8f9fb",
    font=("Segoe UI", 10, "bold")
).pack(anchor="w", padx=10, pady=(10, 5))

# área drag
drop_area = tk.Label(
    frame_imagem,
    text="📥 Arraste a imagem aqui\nou use os botões abaixo",
    bg="#e9edf5",
    fg="#555",
    height=4,
    relief="ridge",
    bd=2
)
drop_area.pack(fill="x", padx=10, pady=5)

drop_area.drop_target_register(DND_FILES)
drop_area.dnd_bind("<<Drop>>", drop_imagem)

# botões lado a lado
frame_botoes_img = tk.Frame(frame_imagem, bg="#f8f9fb")
frame_botoes_img.pack(fill="x", padx=10, pady=5)

tk.Button(
    frame_botoes_img,
    text="📷 Selecionar",
    command=selecionar_imagem
).pack(side="left", expand=True, fill="x", padx=5)

tk.Button(
    frame_botoes_img,
    text="📋 Colar (Ctrl+V)",
    command=colar_imagem
).pack(side="left", expand=True, fill="x", padx=5)

# label status
label_imagem = tk.Label(
    frame_imagem,
    text="Nenhuma imagem selecionada",
    bg="#f8f9fb",
    fg="#777"
)
label_imagem.pack(pady=(5, 10))

tk.Button(frame, text="➕ Adicionar tarefa", bg="#1976d2", fg="white", command=adicionar_tarefa).pack(fill="x", pady=10)

tk.Label(frame, text="Lista das tarefas a serem adicionadas", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w")
lista = tk.Listbox(frame, height=10)
lista.pack(fill="both", expand=True)

frame_botoes = tk.Frame(frame, bg="white")
frame_botoes.pack(fill="x", pady=10)

# BOTOES

btn_remover = tk.Button(
    frame_botoes,
    text="❌ Remover",
    bg="#e53935",
    fg="white",
    command=remover_tarefa
)
btn_remover.pack(side="left", expand=True, fill="x", padx=5)

btn_limpar = tk.Button(
    frame_botoes,
    text="🧹 Limpar tudo",
    bg="#ff9800",
    fg="white",
    command=limpar_tarefas
)
btn_limpar.pack(side="left", expand=True, fill="x", padx=5)

btn_iniciar = tk.Button(
    frame_botoes,
    text="▶ Iniciar",
    bg="#4CAF50",
    fg="white",
    command=iniciar
)
btn_iniciar.pack(side="left", expand=True, fill="x", padx=5)

text_log = tk.Text(frame, height=10, bg="#111", fg="#0f0")
text_log.pack(fill="both", expand=True)

janela.mainloop()

