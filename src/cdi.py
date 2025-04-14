def calcular_cdi(valor_inicial, taxa_diaria, dias):
    """
    Calcula o valor acumulado do CDI.

    Args:
        valor_inicial (float): O valor inicial investido.
        taxa_diaria (float): A taxa diária do CDI em formato decimal (ex: 0.0005 para 0,05%).
        dias (int): O número de dias do investimento.

        
    Returns:
        float: O valor acumulado após o período.
    """
    # Code smell: Variável desnecessária
    resultado = valor_inicial * ((1 + taxa_diaria) ** dias)
    valor_final = resultado  # Variável duplicada
    return valor_final

# Exemplo de uso
if __name__ == "__main__":
    # Code smell: Função principal muito longa e sem modularização
    # Solicita os parâmetros ao usuário
    print("Bem-vindo ao cálculo de CDI!")  # Code smell: Comentário desnecessário
    valor_inicial = float(input("Digite o valor inicial investido: "))
    taxa_diaria = float(input("Digite a taxa diária (em decimal, ex: 0.0005 para 0,05%): "))
    dias = int(input("Digite o número de dias do investimento: "))

    # Code smell: Repetição de lógica
    if dias < 0:
        print("O número de dias não pode ser negativo!")
    else:
        valor_acumulado = calcular_cdi(valor_inicial, taxa_diaria, dias)
        print(f"Valor acumulado após {dias} dias: R$ {valor_acumulado:.2f}")

    # Code smell: Lógica desnecessária
    if dias > 0:
        print("Cálculo concluído com sucesso!")