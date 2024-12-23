import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Função para ler o gabarito de classificação do arquivo CSV
def ler_gabarito(gabarito_path):
    df = pd.read_csv(gabarito_path, encoding='ISO-8859-1')  # Especificando a codificação para evitar problemas
    # Separar a coluna em duas partes: links e classificações
    df[['Link', 'Classificacao_Verdadeira']] = df.iloc[:, 0].str.split(';', expand=True)
    return df

# Função para comparar as classificações
def comparar_classificacoes(df_classificacoes, df_gabarito):
    # Verificar as colunas presentes nos DataFrames
    print("Colunas do gabarito:", df_gabarito.columns)
    print("Colunas das classificações:", df_classificacoes.columns)
    
    # Ajuste para garantir que a primeira coluna seja de links e a segunda de classificação
    if df_classificacoes.shape[1] > 1 and df_gabarito.shape[1] > 1:
        # A primeira coluna é a de links e a segunda a de classificação
        y_true = df_gabarito['Classificacao_Verdadeira']  # Coluna com as classificações reais (segunda coluna)
        y_pred = df_classificacoes.iloc[:, 1]  # Coluna com as classificações preditas (segunda coluna)
    else:
        raise ValueError("O arquivo não contém as colunas esperadas ou está no formato incorreto.")
    
    # Calculando as métricas
    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)

    return accuracy, precision, recall, f1

# Caminho para o arquivo de classificações preditas (se for .xlsx)
classificacoes_path = "C:/AndroidStudio/apis/classificações/resultadosGPT.xlsx"  # Substitua com o arquivo real de classificações preditas

# Caminho para o gabarito com as classificações reais (certifique-se de ter o arquivo como CSV)
gabarito_path = "C:/AndroidStudio/apis/classificações/gabaritotemporario.xlsx"  # Substitua com o caminho real do gabarito

# Ler os arquivos
df_classificacoes = pd.read_excel(classificacoes_path)  # Usando pd.read_excel para arquivos .xlsx
df_gabarito = ler_gabarito(gabarito_path)

# Comparar as classificações e calcular as métricas
accuracy, precision, recall, f1 = comparar_classificacoes(df_classificacoes, df_gabarito)

# Exibir as métricas
print(f"Acurácia: {accuracy:.4f}")
print(f"Precisão: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1-Score: {f1:.4f}")
