import os
import requests

# Configurar variáveis de ambiente
GITHUB_API = "https://api.github.com"
REPO_OWNER = "ugulino"  # Substitua pelo nome do proprietário do repositório
REPO_NAME = "code-review"  # Substitua pelo nome do repositório
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise ValueError("GITHUB_TOKEN não foi encontrado. Certifique-se de que está configurado.")

def obter_arquivos_pr(pr_numero):
    """Obtém os arquivos modificados no PR."""
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_numero}/files"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Erro ao obter arquivos do PR: {e}\nResposta: {response.text}")
        raise
    return response.json()

def adicionar_comentario_pr(pr_numero, arquivo, linha, comentario):
    """Adiciona um comentário no PR."""
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_numero}/comments"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    payload = {
        "body": comentario,
        "path": arquivo,
        "side": "RIGHT",
        "line": linha
    }
    response = requests.post(url, headers=headers, json=payload)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Erro ao adicionar comentário no PR: {e}\nResposta: {response.text}")
        raise

def revisar_codigo(arquivo_conteudo):
    """Simula a revisão de código e gera comentários."""
    comentarios = []
    if "def " in arquivo_conteudo:
        comentarios.append("Considere adicionar docstrings para melhor documentação.")
    return comentarios

def processar_pr(pr_numero):
    """Processa um Pull Request e adiciona comentários baseados em análise de código."""
    try:
        arquivos = obter_arquivos_pr(pr_numero)
        for arquivo in arquivos:
            caminho = arquivo["filename"]
            conteudo = arquivo.get("patch", "")
            comentarios = revisar_codigo(conteudo)
            for comentario in comentarios:
                adicionar_comentario_pr(pr_numero, caminho, 1, comentario)  # Aqui assumimos a linha 1 como exemplo
    except Exception as e:
        print(f"Erro ao processar o PR {pr_numero}: {e}")
        raise

if __name__ == "__main__":
    # Número do PR (pode ser passado como argumento)
    pr_numero = int(os.getenv("PR_NUMBER", 1))
    processar_pr(pr_numero)
