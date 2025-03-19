import os
import requests
import json
import base64  # Adicionado import faltante
from deepseek import DeepSeekAPI  # Import corrigido

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

def obter_commit_id(pr_numero):
    """Obtém o SHA do último commit do PR"""
    repo = os.getenv("GITHUB_REPOSITORY")
    url = f"{GITHUB_API}/repos/{repo}/pulls/{pr_numero}/commits"
    headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()[-1]["sha"]  # Último commit

def obter_arquivos_pr(pr_numero):
    """Obtém os arquivos modificados no PR com conteúdo completo"""
    repo = os.getenv("GITHUB_REPOSITORY")
    url = f"{GITHUB_API}/repos/{repo}/pulls/{pr_numero}/files"
    headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    arquivos = []
    for file in response.json():
        if file["filename"].endswith(".py") and file["status"] != "removed":
            content_response = requests.get(file["contents_url"], headers=headers)
            if content_response.status_code == 200:
                try:
                    content = content_response.json()["content"]
                    file_content = base64.b64decode(content).decode("utf-8")
                    arquivos.append({
                        "filename": file["filename"],
                        "content": file_content,
                        "sha": obter_commit_id(pr_numero)  # Usa o SHA do commit
                    })
                except KeyError:
                    continue
    return arquivos

def analisar_codigo_deepseek(codigo):
    """Envia código para análise pelo DeepSeek"""
    prompt = f"""Analise este código Python seguindo estas diretrizes:
    1. PEP8 e boas práticas
    2. Vulnerabilidades de segurança
    3. Otimizações de desempenho
    4. Legibilidade e manutenibilidade
    5. Code smells
    
    Formato de resposta:
    - Seção para cada tópico
    - Itens em bullet points
    - Sugestões concretas
    
    Código:
    {codigo}
    """
    
    try:
        response = deepseek.chat(
            messages=[{"role": "user", "content": prompt}],
            model="deepseek-coder-33b-instruct",
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro na análise: {str(e)[:200]}")
        return "**Erro na análise**\nNão foi possível obter sugestões para este arquivo."

def criar_comentario_github(pr_numero, arquivo, analise):
    """Cria um comentário no GitHub com os resultados da análise"""
    repo = os.getenv("GITHUB_REPOSITORY")
    url = f"{GITHUB_API}/repos/{repo}/pulls/{pr_numero}/reviews"
    headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    payload = {
        "body": f"**Análise DeepSeek**\n{analise}",
        "event": "COMMENT",
        "comments": [{
            "path": arquivo["filename"],
            "body": analise,
            "line": 1
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"Análise postada em {arquivo['filename']}")
    except requests.exceptions.RequestException as e:
        print(f"Falha ao postar comentário: {str(e)[:200]}")

def processar_pr():
    """Processa o PR e adiciona comentários"""
    try:
        pr_numero = obter_pr_number()
        arquivos = obter_arquivos_pr(pr_numero)
        
        for arquivo in arquivos:
            print(f"Analisando: {arquivo['filename']}")
            analise = analisar_codigo_deepseek(arquivo["content"])
            criar_comentario_github(pr_numero, arquivo, analise)
            
    except Exception as e:
        print(f"Erro crítico: {str(e)}")
        raise

if __name__ == "__main__":
    processar_pr()