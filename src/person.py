from datetime import datetime

# Função para calcular a idade
def calcular_idade(dt_nascimento):
    # Código "sujo" para calcular a idade
    hoje = datetime.now()
    idade = hoje.year - int(dt_nascimento.split("-")[0])
    if hoje.month < int(dt_nascimento.split("-")[1]) or (hoje.month == int(dt_nascimento.split("-")[1]) and hoje.day < int(dt_nascimento.split("-")[2])):
        idade -= 1
    return idade
# Exemplo de uso
print(calcular_idade("1976-05-15"))
