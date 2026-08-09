import os


tarefas = []


def add_task(titulo, imagem):
    tarefas.append({
        "titulo": titulo,
        "imagem": imagem
    })


def remove_task(index):
    if 0 <= index < len(tarefas):
        tarefas.pop(index)


def clear_tasks():
    tarefas.clear()


def has_tasks():
    return bool(tarefas)


def get_tasks():
    return tarefas


def format_tasks():
    if not tarefas:
        return ["Nenhuma tarefa adicionada."]

    linhas = []
    for i, tarefa in enumerate(tarefas, start=1):
        nome_imagem = tarefa["imagem"].split(os.sep)[-1] if isinstance(tarefa["imagem"], str) else tarefa["imagem"]
        linhas.append(
            f"{i}.  {tarefa['titulo']}\n"
            f"    📷 {nome_imagem}\n"
        )
    return linhas
