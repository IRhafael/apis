import requests
from bs4 import BeautifulSoup
import pandas as pd

# Função para extrair o texto do contrato a partir de um link
def extrair_texto(link):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            texto = soup.get_text()  # Captura o texto completo da página
            return texto
        else:
            return "Erro ao acessar o link"
    except Exception as e:
        return f"Erro: {e}"

# Função para classificar o contrato
def classificar_contrato(texto):
    # Palavras-chave para cada categoria
    categorias = {
        "Licenciamento de: patente": ["patente", "licenciamento", "exploração"],
        "Licenciamento de: programa de computador": ["programa de computador", "software", "licenciamento"],
        "Licenciamento de: marcas": ["marcas", "licenciamento"],
        "Licenciamento de: desenho industrial": ["desenho industrial", "licenciamento"],
        "Licenciamento de: cultivar": ["cultivar", "licenciamento"],
        "Venda de: patente": ["venda", "patente"],
        "Venda de: programa de computador": ["venda", "programa de computador", "software"],
        "Venda de: marcas": ["venda", "marcas"],
        "Venda de: desenho industrial": ["venda", "desenho industrial"],
        "Venda de: cultivar": ["venda", "cultivar"],
        "Cessão de uso": ["cessão", "uso"],
        "Partilhamento de titularidade": ["partilhamento", "titularidade"],
        "Encomenda tecnológica": ["encomenda", "tecnológica"],
        "Serviço técnico especializado": ["serviço técnico", "especializado"],
        "Transferência de Know-how": ["transferência", "know-how"],
        "Acordo de parceria": ["acordo", "parceria"]
    }
    
    # Classificação inicial como "Informações insuficientes"
    classificacao = "Informações insuficientes"
    
    # Verificar presença das palavras-chave nas categorias
    for categoria, palavras in categorias.items():
        if any(palavra.lower() in texto.lower() for palavra in palavras):
            classificacao = categoria
            break
    
    return classificacao

# Função para salvar as classificações em um arquivo CSV ou Excel
def salvar_gabarito(links, output_path, formato='csv'):
    data = []  # Lista para armazenar os dados dos links e suas classificações

    for link in links:
        texto = extrair_texto(link)
        classificacao = classificar_contrato(texto)
        data.append([link, classificacao])

    # Criar um DataFrame a partir dos dados
    df = pd.DataFrame(data, columns=["Link", "Classificacao_Verdadeira"])

    # Salvar o DataFrame no formato desejado
    if formato == 'csv':
        df.to_csv(output_path, index=False)
    elif formato == 'xlsx':
        df.to_excel(output_path, index=False)

# Função para ler o arquivo CSV e extrair os links
def ler_links_do_csv(file_path):
    df = pd.read_csv(file_path)  # Lê o arquivo CSV
    return df.iloc[:, 0].tolist()  # Considerando que os links estão na primeira coluna

# Caminho do arquivo CSV contendo os links
file_path = "C:/AndroidStudio/apis/classificações/linkss.csv"  # Substitua pelo caminho correto do seu arquivo CSV

# Caminho para salvar o arquivo de saída (CSV ou Excel)
output_path_csv = "Gabarito_Contratos.csv"
output_path_xlsx = "Gabarito_Contratos.xlsx"

# Ler os links do arquivo CSV
links = ler_links_do_csv(file_path)

# Gerar o gabarito e salvar em CSV
salvar_gabarito(links, output_path_csv, formato='csv')

# Gerar o gabarito e salvar em Excel (opcional)
salvar_gabarito(links, output_path_xlsx, formato='xlsx')

print(f"Gabarito gerado e salvo em {output_path_csv} e {output_path_xlsx}")


