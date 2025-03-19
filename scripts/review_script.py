import os
import requests
import json
from deepseek import DeepSeek


# Configurações da API
GITHUB_API = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Validação de variáveis de ambiente
if not TOKEN:
    raise ValueError("GitHub Token não configurado")
if not DEEPSEEK_API_KEY:
    raise ValueError("DeepSeek API Key não configurada")

# Inicializa o cliente do DeepSeek
deepseek = DeepSeek(api_key=DEEPSEEK_API_KEY)

def obter_pr_number():
    """Obtém o número do PR do contexto do GitHub Actions"""
    event_path = os.getenv("GITHUB_EVENT_PATH")
    with open(event_path) as f:
        event_data = json.load(f)
    return event_data["pull_request"]["number"]

def obter_arquivos_pr(pr_numero):
    """Obtém os arquivos modificados no PR com conteúdo completo"""
    repo = os.getenv("GITHUB_REPOSITORY")
    url = f"{GITHUB_API}/repos/{repo}/pulls/{pr_numero}/files"
    headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    arquivos = []
    for file in response.json():
        if file["filename"].endswith(".py"):
            # Obtém o conteúdo completo do arquivo
            content_response = requests.get(file["contents_url"], headers=headers)
            if content_response.status_code == 200:
                content = content_response.json()["content"]
                # Decodifica conteúdo base64
                file_content = base64.b64decode(content).decode("utf-8")
                arquivos.append({
                    "filename": file["filename"],
                    "content": file_content,
                    "sha": file["sha"]
                })
    return arquivos

def analisar_codigo_deepseek(codigo):
    """Envia código para análise pelo DeepSeek"""
    prompt = f"""Faça uma análise detalhada deste código Python considerando:
    1. Boas práticas e padrões PEP8
    2. Possíveis vulnerabilidades de segurança
    3. Oportunidades de otimização de desempenho
    4. Sugestões para melhorar legibilidade
    5. Identificação de code smells
    
    Retorne os resultados em formato markdown com seções para cada categoria.
    
    Código:
    {codigo}
    """
    
    try:
        response = deepseek.chat(
            messages=[{"role": "user", "content": prompt}],
            model="deepseek-coder-33b-instruct",
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro na análise do DeepSeek: {e}")
        return "Não foi possível analisar o código devido a um erro interno."

def criar_comentario_github(pr_numero, arquivo, analise):
    """Cria um comentário no GitHub com os resultados da análise"""
    repo = os.getenv("GITHUB_REPOSITORY")
    url = f"{GITHUB_API}/repos/{repo}/pulls/{pr_numero}/comments"
    headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    payload = {
        "body": f"**Análise DeepSeek**\n\n{analise}",
        "path": arquivo["filename"],
        "commit_id": arquivo["sha"],
        "line": 1  # Comentário geral no arquivo
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"Comentário adicionado em {arquivo['filename']}")
    else:
        print(f"Erro ao comentar: {response.status_code} {response.text}")

def processar_pr():
    """Processa o PR e adiciona comentários"""
    pr_numero = obter_pr_number()
    arquivos = obter_arquivos_pr(pr_numero)
    
    for arquivo in arquivos:
        print(f"Analisando: {arquivo['filename']}")
        analise = analisar_codigo_deepseek(arquivo["content"])
        criar_comentario_github(pr_numero, arquivo, analise)

if __name__ == "__main__":
    processar_pr()