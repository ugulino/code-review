from datetime import datetime

# Função para calcular a idade
def calcular_idade(data_nascimento):
    # Código "sujo" com práticas ruins
    hoje = datetime.now()
    idade = hoje.year - int(data_nascimento.split("-")[0])
    if hoje.month < int(data_nascimento.split("-")[1]) or (hoje.month == int(data_nascimento.split("-")[1]) and hoje.day < int(data_nascimento.split("-")[2])):
        idade -= 1
    return idade

# Exemplo de uso
print(calcular_idade("1990-05-15"))
