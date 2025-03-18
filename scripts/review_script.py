import os
import requests

# Configurar variáveis de ambiente
GITHUB_API = "https://api.github.com"
REPO_OWNER = "ugulino"
REPO_NAME = "code-review"
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise ValueError("GITHUB_TOKEN não foi encontrado. Certifique-se de que está configurado.")

def obter_arquivos_pr(pr_numero):
    """Obtém os arquivos modificados no PR."""
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_numero}/files"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def obter_commit_id(pr_numero):
    """Obtém o commit_id mais recente no PR."""
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_numero}/commits"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    commits = response.json()
    return commits[-1]["sha"]  # Obtém o último commit (mais recente)

def adicionar_comentario_pr(pr_numero, arquivo, position, comentario):
    """Adiciona um comentário na revisão do PR."""
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_numero}/comments"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    commit_id = obter_commit_id(pr_numero)
    payload = {
        "body": comentario,
        "path": arquivo,
        "position": position,
        "commit_id": commit_id
    }
    response = requests.post(url, headers=headers, json=payload)
    try:
        response.raise_for_status()
        print(f"Comentário adicionado com sucesso no arquivo '{arquivo}' na posição {position}.")
    except requests.exceptions.HTTPError as e:
        print(f"Erro ao adicionar comentário no PR: {e}\nResposta: {response.text}")
        raise

def revisar_codigo(arquivo_conteudo):
    """Simula a revisão de código e gera comentários."""
    comentarios = []
    for i, linha in enumerate(arquivo_conteudo.splitlines(), start=1):
        if "def " in linha:
            comentarios.append((i, "Considere adicionar docstrings para melhor documentação."))
    return comentarios

def processar_pr(pr_numero):
    """Processa um Pull Request e adiciona comentários baseados em análise de código."""
    arquivos = obter_arquivos_pr(pr_numero)
    for arquivo in arquivos:
        caminho = arquivo["filename"]
        conteudo = arquivo.get("patch", "")
        print(f"Analisando arquivo: {caminho}")
        comentarios = revisar_codigo(conteudo)
        for position, comentario in comentarios:
            adicionar_comentario_pr(pr_numero, caminho, position, comentario)

if __name__ == "__main__":
    # Número do PR (pode ser passado como argumento)
    pr_numero = int(os.getenv("PR_NUMBER", 1))
    processar_pr(pr_numero)
