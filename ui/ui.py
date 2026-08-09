import os
import threading
import tempfile
import traceback
from tkinter import messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import ImageGrab, Image, ImageTk
import customtkinter as ctk

from config.constants import (
    BG_COLOR,
    BORDER_COLOR,
    CARD_COLOR,
    INPUT_BORDER,
    INPUT_COLOR,
    BLUE,
    BLUE_HOVER,
    RED,
    RED_HOVER,
    ORANGE,
    ORANGE_HOVER,
    GREEN,
    GREEN_HOVER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    IMAGE_FILETYPES,
)
from core.task_manager import add_task, clear_tasks, get_tasks, has_tasks, remove_task
from core.browser_automation import executar_bot


imagem_temp = None
preview_image = None
text_log = None
label_imagem = None
preview_label = None
lista = None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


def log(msg):
    text_log.configure(state="normal")
    text_log.insert("end", msg + "\n")
    text_log.see("end")
    text_log.configure(state="disabled")


def selecionar_imagem():
    global imagem_temp

    path = filedialog.askopenfilename(
        title="Selecionar imagem",
        filetypes=IMAGE_FILETYPES
    )

    if not path:
        return

    imagem_temp = path
    label_imagem.configure(text=f"📷 {os.path.basename(path)}")
    mostrar_preview(path)


def drop_imagem(event):
    global imagem_temp

    path = event.data.strip()
    if path.startswith("{") and path.endswith("}"):
        path = path[1:-1]

    if not path.lower().endswith((".png", ".jpg", ".jpeg")):
        messagebox.showwarning(
            "Arquivo inválido",
            "Selecione uma imagem PNG, JPG ou JPEG."
        )
        return

    imagem_temp = path
    label_imagem.configure(text=f"📷 {os.path.basename(path)}")
    mostrar_preview(path)


def colar_imagem():
    global imagem_temp

    img = ImageGrab.grabclipboard()
    if img is None:
        messagebox.showwarning(
            "Nenhuma imagem",
            "Nenhuma imagem encontrada na área de transferência!"
        )
        return

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    temp_path = temp_file.name
    temp_file.close()

    img.save(temp_path, "PNG")
    imagem_temp = temp_path

    label_imagem.configure(text="📋 Imagem colada do print")
    mostrar_preview(temp_path)


def mostrar_preview(caminho):
    global preview_image

    try:
        img = Image.open(caminho)
        img = img.copy()

        largura_max = 500
        altura_max = 280
        img.thumbnail((largura_max, altura_max), Image.Resampling.LANCZOS)

        preview_image = ImageTk.PhotoImage(img, master=preview_label)
        preview_label.configure(image=preview_image, text="")
    except Exception as e:
        print(f"Erro ao carregar preview: {e}")
        preview_image = None
        preview_label.configure(image="", text="Erro ao carregar preview")


def atualizar_lista():
    lista.configure(state="normal")
    lista.delete("1.0", "end")

    if not has_tasks():
        lista.insert("end", "Nenhuma tarefa adicionada.")
    else:
        for i, tarefa in enumerate(get_tasks(), start=1):
            nome_imagem = os.path.basename(tarefa["imagem"])
            lista.insert(
                "end",
                f"{i}.  {tarefa['titulo']}\n"
                f"    📷 {nome_imagem}\n\n"
            )

    lista.configure(state="disabled")


def adicionar_tarefa():
    global imagem_temp

    titulo = entry_titulo.get().strip()
    if not titulo:
        messagebox.showwarning("Atenção", "Informe o título da tarefa!")
        return

    if not imagem_temp:
        messagebox.showwarning("Atenção", "Adicione o print da OS!")
        return

    add_task(titulo, imagem_temp)
    atualizar_lista()
    entry_titulo.delete(0, "end")
    limpar_anexo()


def limpar_anexo():
    global imagem_temp, preview_image

    imagem_temp = None
    preview_image = None
    label_imagem.configure(text="Nenhuma imagem selecionada")
    preview_label.configure(image="", text="Nenhum preview")


def remover_tarefa():
    selecionado = lista.tag_ranges("sel")
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione uma tarefa para remover!")
        return

    linha = int(lista.index(selecionado[0]).split(".")[0])
    index = linha - 1
    remove_task(index)
    atualizar_lista()


def limpar_tarefas():
    if not has_tasks():
        return

    confirmar = messagebox.askyesno("Confirmar", "Deseja remover TODAS as tarefas?")
    if not confirmar:
        return

    clear_tasks()
    atualizar_lista()


def iniciar():
    threading.Thread(target=executar_bot_thread, daemon=True).start()


def executar_bot_thread():
    try:
        if not has_tasks():
            messagebox.showwarning("Atenção", "Adicione pelo menos uma tarefa!")
            return

        executar_bot(get_tasks(), log)
        clear_tasks()
        atualizar_lista()
    except Exception as e:
        log("❌ ERRO")
        log(str(e))
        log(traceback.format_exc())


def run_app():
    global label_imagem, preview_label, lista, text_log, entry_titulo

    janela = TkinterDnD.Tk()
    janela.title("Runrun Bot - Automação")
    janela.geometry("900x850")
    janela.minsize(850, 750)
    janela.configure(bg=BG_COLOR)
    janela.bind("<Control-v>", lambda e: colar_imagem())

    main_frame = ctk.CTkFrame(janela, corner_radius=24, fg_color=CARD_COLOR, border_width=1, border_color=BORDER_COLOR)
    main_frame.pack(fill="both", expand=True, padx=18, pady=18)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(4, weight=1)
    main_frame.grid_rowconfigure(6, weight=1)

    header = ctk.CTkFrame(main_frame, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))

    ctk.CTkLabel(header, text="Automação de Tarefas", font=("Segoe UI", 22, "bold"), text_color=TEXT_PRIMARY).pack(anchor="w")
    ctk.CTkLabel(header, text="Crie e finalize tarefas automaticamente no Runrun.it.", font=("Segoe UI", 12), text_color=TEXT_SECONDARY).pack(anchor="w", pady=(3, 0))

    titulo_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    titulo_frame.grid(row=1, column=0, sticky="ew", padx=24, pady=(5, 8))
    titulo_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(titulo_frame, text="Título da tarefa", font=("Segoe UI", 13, "bold"), text_color=TEXT_PRIMARY).grid(row=0, column=0, sticky="w", pady=(0, 5))

    entry_titulo = ctk.CTkEntry(titulo_frame, height=36, corner_radius=10, placeholder_text="Digite o título da tarefa", fg_color=INPUT_COLOR, border_color=INPUT_BORDER)
    entry_titulo.grid(row=1, column=0, sticky="ew")

    imagem_frame = ctk.CTkFrame(main_frame, corner_radius=16, fg_color="#0F1A2B", border_width=1, border_color=BORDER_COLOR)
    imagem_frame.grid(row=2, column=0, sticky="ew", padx=24, pady=8)
    imagem_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(imagem_frame, text="Print da OS", font=("Segoe UI", 15, "bold"), text_color=TEXT_PRIMARY).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 2))
    ctk.CTkLabel(imagem_frame, text="Adicione a imagem que será inserida na descrição da tarefa.", font=("Segoe UI", 11), text_color=TEXT_SECONDARY).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 10))

    drop_area = ctk.CTkLabel(imagem_frame, text="📥\nArraste a imagem aqui\nou utilize uma das opções abaixo", height=85, corner_radius=12, fg_color="#1E293B", text_color=TEXT_SECONDARY, font=("Segoe UI", 12))
    drop_area.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 10))
    drop_area.drop_target_register(DND_FILES)
    drop_area.dnd_bind("<<Drop>>", drop_imagem)

    botoes_imagem = ctk.CTkFrame(imagem_frame, fg_color="transparent")
    botoes_imagem.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 8))
    botoes_imagem.grid_columnconfigure(0, weight=1)
    botoes_imagem.grid_columnconfigure(1, weight=1)

    ctk.CTkButton(botoes_imagem, text="📷  Selecionar imagem", height=34, corner_radius=9, fg_color="#334155", hover_color="#475569", command=selecionar_imagem).grid(row=0, column=0, sticky="ew", padx=(0, 5))
    ctk.CTkButton(botoes_imagem, text="📋  Colar (Ctrl+V)", height=34, corner_radius=9, fg_color="#334155", hover_color="#475569", command=colar_imagem).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    label_imagem = ctk.CTkLabel(imagem_frame, text="Nenhuma imagem selecionada", font=("Segoe UI", 11), text_color=TEXT_SECONDARY)
    label_imagem.grid(row=4, column=0, pady=(0, 8))

    preview_label = ctk.CTkLabel(imagem_frame, text="Nenhum preview", width=500, height=100, fg_color="#0B1220", corner_radius=10, text_color="#64748B")
    preview_label.grid(row=5, column=0, padx=16, pady=(0, 14))

    ctk.CTkButton(main_frame, text="➕  Adicionar tarefa", height=40, corner_radius=10, font=("Segoe UI", 13, "bold"), fg_color=BLUE, hover_color=BLUE_HOVER, command=adicionar_tarefa).grid(row=3, column=0, sticky="ew", padx=24, pady=(8, 12))

    lista_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    lista_frame.grid(row=4, column=0, sticky="nsew", padx=24, pady=(0, 8))
    lista_frame.grid_columnconfigure(0, weight=1)
    lista_frame.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(lista_frame, text="Tarefas adicionadas", font=("Segoe UI", 15, "bold"), text_color=TEXT_PRIMARY).grid(row=0, column=0, sticky="w", pady=(0, 6))

    lista = ctk.CTkTextbox(lista_frame, height=130, corner_radius=10, fg_color="#0B1220", border_width=1, border_color=BORDER_COLOR, font=("Segoe UI", 12))
    lista.grid(row=1, column=0, sticky="nsew")
    lista.configure(state="disabled")
    atualizar_lista()

    botoes_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    botoes_frame.grid(row=5, column=0, sticky="ew", padx=24, pady=(4, 10))
    botoes_frame.grid_columnconfigure(0, weight=1)
    botoes_frame.grid_columnconfigure(1, weight=1)
    botoes_frame.grid_columnconfigure(2, weight=2)

    ctk.CTkButton(botoes_frame, text="❌  Remover", height=38, corner_radius=10, fg_color=RED, hover_color=RED_HOVER, command=remover_tarefa).grid(row=0, column=0, sticky="ew", padx=(0, 5))
    ctk.CTkButton(botoes_frame, text="🧹  Limpar tudo", height=38, corner_radius=10, fg_color=ORANGE, hover_color=ORANGE_HOVER, command=limpar_tarefas).grid(row=0, column=1, sticky="ew", padx=5)
    ctk.CTkButton(botoes_frame, text="▶  Iniciar automação", height=38, corner_radius=10, font=("Segoe UI", 13, "bold"), fg_color=GREEN, hover_color=GREEN_HOVER, command=iniciar).grid(row=0, column=2, sticky="ew", padx=(5, 0))

    log_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    log_frame.grid(row=6, column=0, sticky="nsew", padx=24, pady=(0, 20))
    log_frame.grid_columnconfigure(0, weight=1)
    log_frame.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(log_frame, text="Log da automação", font=("Segoe UI", 15, "bold"), text_color=TEXT_PRIMARY).grid(row=0, column=0, sticky="w", pady=(0, 6))

    text_log = ctk.CTkTextbox(log_frame, height=120, corner_radius=10, fg_color="#080D16", border_width=1, border_color=BORDER_COLOR, font=("Consolas", 11), text_color="#CBD5E1")
    text_log.grid(row=1, column=0, sticky="nsew")
    text_log.configure(state="disabled")

    janela.mainloop()
