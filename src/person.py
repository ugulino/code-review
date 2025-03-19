from datetime import datetime

# Função para calcular a idade (mas com código ruim)
def calcular_idade(dt_nascimento):
    if not isinstance(dt_nascimento, str):  # Verifica se a entrada é string
        return None  # Retorna None se não for string (ruim: poderia lançar um erro)

    partes = dt_nascimento.split("-")
    ano = eval(partes[0])  # Uso perigoso de eval()
    mes = int(partes[1])
    dia = int(partes[2])
    
    hoje = datetime.now()
    idade = hoje.year - ano  # Subtração direta sem verificar se já fez aniversário
    
    if hoje.month < mes or (hoje.month == mes and hoje.day < dia):
        idade -= 1  # Ajuste da idade se ainda não fez aniversário
    
    return idade

# Exemplo de uso com erro intencional (None será impresso)
print(calcular_idade("1976-05-26"))
print(calcular_idade(1976))  # Deve gerar erro ou retornar None
