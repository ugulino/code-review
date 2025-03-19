import os
import requests

# Configurar variáveis de ambiente
GITHUB_API = "https://api.github.com"
REPO_OWNER = "ugulino"
REPO_NAME = "code-review"
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise ValueError("O token do GitHub (GITHUB_TOKEN) não foi definido.")

# Aqui você pode configurar o DeepSeek (supondo que seja uma API ou biblioteca)
# Supondo que DeepSeek tenha um método 'buscar_semantico' para encontrar trechos de código relacionados.
from deepseek import DeepSeek

# Inicializa o DeepSeek (se necessário)
deepseek = DeepSeek(model="bert-base-uncased")

def obter_arquivos_pr(pr_numero):
    """Obtém os arquivos modificados no PR."""
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_numero}/files"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def enriquecer_comentario_com_deepseek(comentario, conteudo):
    """Enriquece o comentário com informações do DeepSeek para melhorar as sugestões."""
    
    # Aqui você pode buscar por trechos de código semânticamente relacionados a legibilidade, desempenho e segurança
    resultado_legibilidade = deepseek.buscar_semantico("melhorar legibilidade no código", conteudo)
    resultado_desempenho = deepseek.buscar_semantico("melhorar desempenho no código", conteudo)
    resultado_seguranca = deepseek.buscar_semantico("melhorar segurança no código", conteudo)

    if resultado_legibilidade:
        comentario += f" Sugestão: {resultado_legibilidade}"
    if resultado_desempenho:
        comentario += f" Sugestão: {resultado_desempenho}"
    if resultado_seguranca:
        comentario += f" Sugestão: {resultado_seguranca}"

    return comentario

def obter_commit_id(pr_numero):
    """Obtém o commit_id mais recente no PR."""
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_numero}/commits"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    commits = response.json()
    
    commit_id = commits[-1]["sha"]  # Retorna o SHA do último commit no PR    
    print(f"Commit ID recuperado: {commit_id}")
    return commit_id

def adicionar_comentario_pr(pr_numero, arquivo, position, comentario):
    """Adiciona um comentário na revisão do PR."""
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_numero}/comments"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    payload = {
        "body": comentario,
        "path": arquivo,
        "position": position,
        "commit_id": obter_commit_id(pr_numero)
    }

    print("Enviando comentário com os seguintes dados:")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {payload}")

    response = requests.post(url, headers=headers, json=payload)
    try:
        response.raise_for_status()
        print(f"Comentário adicionado com sucesso no arquivo '{arquivo}' na posição {position}.")
    except requests.exceptions.HTTPError as e:
        print(f"Erro ao adicionar comentário no PR: {e}\nResposta: {response.text}")
        raise

def processar_pr(pr_numero):
    """Processa um Pull Request e adiciona comentários com sugestões enriquecidas."""
    arquivos = obter_arquivos_pr(pr_numero)
    for arquivo in arquivos:
        caminho = arquivo["filename"]
        if caminho.endswith(".py"):  # Foco apenas em arquivos Python
            conteudo = arquivo.get("patch", "")
            if conteudo:
                print(f"Analisando arquivo: {caminho}")
                comentario = "Análise semântica do código: "
                comentario = enriquecer_comentario_com_deepseek(comentario, conteudo)
                position = arquivo.get("position", 1)  # Verifica se há uma posição válida
                adicionar_comentario_pr(pr_numero, caminho, position, comentario)

if __name__ == "__main__":
    pr_numero_env = os.getenv("PR_NUMBER")
    print(f"DEBUG: PR_NUMBER='{pr_numero_env}'")  # Para depuração
    if not pr_numero_env or not pr_numero_env.isdigit():
        raise ValueError("Número do PR inválido ou não definido corretamente.")
    
    pr_numero = int(pr_numero_env)
    processar_pr(pr_numero)
