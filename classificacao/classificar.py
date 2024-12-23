import pandas as pd
from fuzzywuzzy import fuzz
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Função para ler o gabarito de classificação do arquivo CSV
def ler_gabarito(gabarito_path):
    df = pd.read_csv(gabarito_path, encoding='ISO-8859-1')  # Lê o arquivo CSV com a codificação adequada
    
    # Verificar se a coluna contém o separador ';' e dividir corretamente
    try:
        # Tentar separar a coluna em 'Link' e 'Classificacao_Verdadeira'
        df[['Link', 'Classificacao_Verdadeira']] = df.iloc[:, 0].str.split(';', expand=True)
    except ValueError as e:
        print(f"Erro ao dividir a coluna: {e}")
        print("Verifique se todos os dados estão no formato esperado (link;classificação).")
        return None

    # Remover espaços extras nas colunas
    df['Link'] = df['Link'].str.strip()
    df['Classificacao_Verdadeira'] = df['Classificacao_Verdadeira'].str.strip()

    # Padronizar para minúsculas para garantir que a comparação seja feita sem sensibilidade a maiúsculas/minúsculas
    df['Classificacao_Verdadeira'] = df['Classificacao_Verdadeira'].str.lower()

    return df

# Função para comparar as classificações
def comparar_classificacoes(df_classificacoes, df_gabarito):
    # Verificar as colunas presentes nos DataFrames
    print("Colunas do gabarito:", df_gabarito.columns)
    print("Colunas das classificações:", df_classificacoes.columns)
    
    # Garantir que as classificações preditas e reais estão corretamente alinhadas
    if df_classificacoes.shape[1] > 1 and df_gabarito.shape[1] > 1:
        # A primeira coluna é a de links e a segunda a de classificação
        y_true = df_gabarito['Classificacao_Verdadeira']  # Coluna com as classificações reais
        y_pred = df_classificacoes.iloc[:, 1].str.strip().str.lower()  # Coluna com as classificações preditas
        
        # Alinhar os dados por índice
        if len(df_gabarito) == len(df_classificacoes):
            y_true = df_gabarito['Classificacao_Verdadeira']
            y_pred = df_classificacoes.iloc[:, 1]
        else:
            print("Aviso: O número de links e classificações preditas não é o mesmo.")
            return None, None, None, None

        # Categorias predefinidas para comparação
        categorias_validas = [
            "licenciamento de: patente", "licenciamento de: programa de computador", "licenciamento de: marcas",
            "licenciamento de: desenho industrial", "licenciamento de: cultivar", "venda de: patente",
            "venda de: programa de computador", "venda de: marcas", "venda de: desenho industrial", "venda de: cultivar",
            "cessão de uso", "partilhamento de titularidade", "encomenda tecnológica", "serviço técnico especializado",
            "transferência de know-how", "acordo de parceria"
        ]
        
        # Verificar as primeiras classificações
        print("Primeiras classificações reais:\n", y_true[:5])
        print("Primeiras classificações preditas:\n", y_pred[:5])

        # Verificar se as classificações preditas estão dentro das categorias válidas
        y_pred_validas = [cat if cat in categorias_validas else "informações insuficientes" for cat in y_pred]
        y_true_validas = [cat if cat in categorias_validas else "informações insuficientes" for cat in y_true]
        
        # Verifique se as predições são válidas
        print("Primeiras classificações preditas após validação:\n", y_pred_validas[:5])
    
    # Calculando as métricas
    accuracy = accuracy_score(y_true_validas, y_pred_validas)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true_validas, y_pred_validas, average='weighted', zero_division=0)

    return accuracy, precision, recall, f1

# Caminho para o arquivo de classificações preditas (se for .xlsx)
classificacoes_path = "C:/AndroidStudio/apis/classificacao/resultados/resultadosGPT.xlsx"  # Substitua com o arquivo real de classificações preditas

# Caminho para o gabarito com as classificações reais (certifique-se de ter o arquivo como CSV)
gabarito_path = "C:/AndroidStudio/apis/classificacao/gabaritotemporario.xlsx"  # Substitua com o caminho real do gabarito

# Ler os arquivos
df_classificacoes = pd.read_excel(classificacoes_path)  # Usando pd.read_excel para arquivos .xlsx
df_gabarito = ler_gabarito(gabarito_path)

# Comparar as classificações e calcular as métricas
if df_gabarito is not None:
    accuracy, precision, recall, f1 = comparar_classificacoes(df_classificacoes, df_gabarito)

    # Exibir as métricas
    print(f"Acurácia: {accuracy:.4f}")
    print(f"Precisão: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")
else:
    print("Erro ao ler o gabarito, verifique o formato do arquivo.")

