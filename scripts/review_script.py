import os
import requests
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Configurar variáveis de ambiente
GITHUB_API = "https://api.github.com"
REPO_OWNER = "ugulino"
REPO_NAME = "code-review"
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise ValueError("O token do GitHub (GITHUB_TOKEN) não foi definido.")

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
    """Usa o CodeBERT para revisar o código, fornecendo contexto adicional."""
    prompt = (
        "Revise o seguinte código Python e forneça sugestões claras para melhorar a legibilidade, "
        "desempenho e segurança. Use exemplos e referências a boas práticas:\n\n"
        f"{conteudo}"
    )
    
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)
    logits = outputs.logits
    classe_predita = logits.argmax().item()

    if classe_predita == 0:
        return "Código adequado. Sem problemas detectados."
    elif classe_predita == 1:
        return "Sugestão de melhoria: verifique a legibilidade e a estrutura do código."
    else:
        return "Revisão necessária: possíveis problemas de desempenho ou segurança."

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

def enriquecer_comentario(comentario, conteudo):
    """Melhora os comentários do CodeBERT tornando-os mais específicos."""
    
    if "legibilidade" in comentario:
        comentario += " Considere renomear variáveis para tornar o código mais intuitivo."
    
    if "desempenho" in comentario:
        comentario += " Verifique se há loops ou operações custosas que podem ser otimizadas."
    
    if "segurança" in comentario:
        comentario += " Evite o uso de eval(), exec() ou manipulação insegura de entrada do usuário."
    
    return comentario

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
    """Processa um Pull Request, usa CodeBERT para revisão e adiciona comentários."""
    arquivos = obter_arquivos_pr(pr_numero)
    for arquivo in arquivos:
        caminho = arquivo["filename"]
        if caminho.endswith(".py"):  # Foco apenas em arquivos Python
            conteudo = arquivo.get("patch", "")
            if conteudo:
                print(f"Analisando arquivo: {caminho}")
                comentario = analisar_codigo_com_codebert(conteudo)
                position = arquivo.get("position", 1)  # Verifica se há uma posição válida
                comentario = analisar_codigo_com_codebert(conteudo)
                comentario = enriquecer_comentario(comentario, conteudo)
                adicionar_comentario_pr(pr_numero, caminho, position, comentario)

if __name__ == "__main__":
    pr_numero_env = os.getenv("PR_NUMBER")
    print(f"DEBUG: PR_NUMBER='{pr_numero_env}'")  # Para depuração
    if not pr_numero_env or not pr_numero_env.isdigit():
        raise ValueError("Número do PR inválido ou não definido corretamente.")
    
    pr_numero = int(pr_numero_env)
    processar_pr(pr_numero)
