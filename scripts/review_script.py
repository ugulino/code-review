import os
import requests
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Configurar variáveis de ambiente
GITHUB_API = "https://api.github.com"
REPO_OWNER = "ugulino"
REPO_NAME = "code-review"
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise ValueError("GITHUB_TOKEN não foi encontrado. Certifique-se de que está configurado.")

# Carregar o modelo GraphCodeBERT
tokenizer = AutoTokenizer.from_pretrained("microsoft/graphcodebert-base")
model = AutoModelForSequenceClassification.from_pretrained("microsoft/graphcodebert-base")

def obter_arquivos_pr(pr_numero):
    """Obtém os arquivos modificados no PR."""
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_numero}/files"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def gerar_revisao_com_graphcodebert(conteudo):
    """Usa o GraphCodeBERT para revisar o código."""
    inputs = tokenizer(conteudo, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    logits = outputs.logits
    prediction = torch.argmax(logits, dim=1).item()
    
    # Simulação: Substituir pelo mapeamento real de classes e comentários
    if prediction == 0:
        return "Código parece adequado, sem problemas detectados."
    elif prediction == 1:
        return "Revisão sugerida: Considere melhorar a legibilidade do código."
    else:
        return "Não foi possível gerar uma revisão precisa."

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
    """Processa um Pull Request, usa GraphCodeBERT para revisão e adiciona comentários."""
    arquivos = obter_arquivos_pr(pr_numero)
    for arquivo in arquivos:
        caminho = arquivo["filename"]
        if caminho == "person.py":  # Foco apenas no arquivo relevante
            conteudo = arquivo.get("patch", "")
            print(f"Analisando arquivo: {caminho}")
            comentario = gerar_revisao_com_graphcodebert(conteudo)
            adicionar_comentario_pr(pr_numero, caminho, 1, comentario)

if __name__ == "__main__":
    # Número do PR (pode ser passado como argumento)
    pr_numero = int(os.getenv("PR_NUMBER", 1))
    processar_pr(pr_numero)
