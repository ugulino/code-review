

## Pré-requisitos

- Python 3.8 ou superior
- Conta no GitHub com um token de acesso configurado
- Chave de API válida para o DeepSeek

## Instalação

1. Clone o repositório:
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd code-review
    ```

2. Crie um ambiente virtual e ative-o:
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows use `venv\Scripts\activate`
    ```

3. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## Configuração

Certifique-se de configurar as seguintes variáveis de ambiente:

- `GITHUB_TOKEN`: Token de acesso do GitHub com permissões para comentar em PRs.
- `DEEPSEEK_API_KEY`: Chave de API para o DeepSeek.
- `GITHUB_EVENT_PATH`: Caminho para o arquivo de evento do GitHub Actions.
- `GITHUB_REPOSITORY`: Nome do repositório no formato `usuario/repo`.

No Windows, você pode configurar as variáveis de ambiente no terminal:
```bash
set GITHUB_TOKEN=<SEU_TOKEN>
set DEEPSEEK_API_KEY=<SUA_CHAVE>
set GITHUB_EVENT_PATH=<CAMINHO_DO_ARQUIVO>
set GITHUB_REPOSITORY=<USUARIO/REPO>
