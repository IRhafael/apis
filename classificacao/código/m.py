import pandas as pd

def verificar_e_corrigir_dados(caminho_arquivo, caminho_saida):
    try:
        # Determinar o formato do arquivo com base na extensão
        if caminho_arquivo.endswith('.xlsx'):
            # Ler arquivo Excel
            df = pd.read_excel(caminho_arquivo, engine='openpyxl')
        elif caminho_arquivo.endswith('.csv'):
            # Ler arquivo CSV
            df = pd.read_csv(caminho_arquivo, encoding='ISO-8859-1')
        else:
            raise ValueError("Formato de arquivo não suportado. Use .csv ou .xlsx")
        
        # Verificar se há apenas uma coluna que precisa ser separada
        if df.shape[1] == 1:
            print("Arquivo contém uma única coluna, tentando dividir em 'Link' e 'Classificacao_Verdadeira'.")
            # Separar a coluna em 'Link' e 'Classificacao_Verdadeira' com base no delimitador ";"
            df[['Link', 'Classificacao_Verdadeira']] = df.iloc[:, 0].str.split(';', expand=True)
        else:
            print("Arquivo já contém múltiplas colunas.")
        
        # Remover espaços em branco extras
        df['Link'] = df['Link'].str.strip()
        df['Classificacao_Verdadeira'] = df['Classificacao_Verdadeira'].str.strip()
        
        # Salvar o arquivo corrigido como CSV
        df.to_csv(caminho_saida, index=False, encoding='utf-8')
        print(f"Arquivo corrigido salvo em: {caminho_saida}")
        
        return df
    
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        return None

# Caminho do arquivo original
caminho_arquivo = "C:/AndroidStudio/apis/classificacao/gabaritotemporario.xlsx"

# Caminho para salvar o arquivo corrigido
caminho_saida = "C:/AndroidStudio/apis/classificacao/gabaritocorrigido.csv"

# Chamar a função
df_corrigido = verificar_e_corrigir_dados(caminho_arquivo, caminho_saida)

# Exibir as primeiras linhas do arquivo corrigido (se corrigido com sucesso)
if df_corrigido is not None:
    print(df_corrigido.head())

