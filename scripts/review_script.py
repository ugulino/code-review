import os
import requests
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Configurar variáveis de ambiente
GITHUB_API = "https://api.github.com"
REPO_OWNER = "ugulino"
REPO_NAME = "code-review"
TOKEN = os.getenv("GITHUB_TOKEN")

# Carregar o modelo CodeBERT
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModelForSequenceClassification.from_pretrained("microsoft/codebert-base", num_labels=2)

def obter_arquivos_pr(pr_numero):
    """Obtém os arquivos modificados no PR."""
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_numero}/files"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def analisar_codigo_com_codebert(conteudo):
    """Usa o CodeBERT para revisar o código."""
    inputs = tokenizer(conteudo, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    logits = outputs.logits
    classe_predita = logits.argmax().item()

    # Simulação: ajuste de acordo com o mapeamento real das classes
    if classe_predita == 0:
        return "Código parece adequado."
    elif classe_predita == 1:
        return "Revisão sugerida: Considere melhorar a legibilidade."
    else:
        return "Sem recomendações específicas."

def obter_commit_id(pr_numero):
    """Obtém o commit_id mais recente no PR."""
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_numero}/commits"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    commits = response.json()
    return commits[-1]["sha"]  # Retorna o SHA do último commit no PR    

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
    response = requests.post(url, headers=headers, json=payload)
    try:
        response.raise_for_status()
        print(f"Comentário adicionado com sucesso no arquivo '{arquivo}' na posição {position}.")
    except requests.exceptions.HTTPError as e:
        print(f"Erro ao adicionar comentário no PR: {e}\nResposta: {response.text}")
        raise

def processar_pr(pr_numero):
    """Processa um Pull Request, usa CodeBERT para revisão e adiciona comentários."""
    arquivos = obter_arquivos_pr(pr_numero)
    for arquivo in arquivos:
        caminho = arquivo["filename"]
        if caminho.endswith(".py"):  # Foco apenas em arquivos Python
            conteudo = arquivo.get("patch", "")
            print(f"Analisando arquivo: {caminho}")
            comentario = analisar_codigo_com_codebert(conteudo)
            adicionar_comentario_pr(pr_numero, caminho, 1, comentario)

if __name__ == "__main__":
    # Número do PR (pode ser passado como argumento)
    pr_numero = int(os.getenv("PR_NUMBER", 1))
    processar_pr(pr_numero)
