import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Função para ler o gabarito de classificação do arquivo CSV
def ler_gabarito(gabarito_path):
    df = pd.read_csv(gabarito_path, encoding='ISO-8859-1')  # Especificando a codificação para evitar problemas
    return df

# Função para comparar as classificações
def comparar_classificacoes(df_classificacoes, df_gabarito):
    # Comparando a classificação gerada com a verdadeira
    y_true = df_gabarito['Classificacao_Verdadeira']  # Coluna com as classificações reais
    y_pred = df_classificacoes['Classificacao_Predita']  # Coluna com as classificações preditas

    # Calculando as métricas
    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted')

    return accuracy, precision, recall, f1

# Caminho para o arquivo de classificações preditas (se for .xlsx)
classificacoes_path = "C:/AndroidStudio/apis/classificações/resultadosGPT.xlsx"  # Substitua com o arquivo real de classificações preditas

# Caminho para o gabarito com as classificações reais (certifique-se de ter o arquivo como CSV)
gabarito_path = "C:/AndroidStudio/apis/classificações/Gabarito_Contratos.docx"  # Substitua com o caminho real do gabarito

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

