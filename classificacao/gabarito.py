import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

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

# Função para classificar o contrato com base nas palavras-chave
def classificar_contrato(texto):
    # Definindo os tipos de contrato com suas palavras-chave (somente as classificações fornecidas EXATAS)
    categorias = {
        "Licenciamento de: patente": ["licenciamento", "patente", "exploração", "INPI", "tecnologia", "registro", "propriedade intelectual", "exclusividade"],
        "Licenciamento de: programa de computador": ["licenciamento", "software", "programa de computador", "código-fonte", "direitos de uso", "desenvolvimento de software"],
        "Licenciamento de: marcas": ["licenciamento", "marca", "registro de marca", "direitos de uso", "marca registrada", "branding"],
        "Licenciamento de: cultivar": ["licenciamento", "cultivar", "sementes", "genética", "direitos de cultivar", "plantio", "biotecnologia"],
        "Venda de: patente": ["venda", "patente", "transferência de direitos", "compra de patente", "direitos de patente", "comercialização"],
        "Venda de: programa de computador": ["venda", "software", "programa de computador", "código-fonte", "transação", "licenciamento de software"],
        "Venda de: marcas": ["venda", "marca", "transferência de marca", "comercialização de marca", "registro de marca", "transação de direitos"],
        "Venda de: desenho industrial": ["venda", "desenho industrial", "design", "produto de design", "transferência de direitos", "design de produto"],
        "Venda de: cultivar": ["venda", "cultivar", "sementes", "genética", "direitos de cultivo", "semeadura", "propriedade intelectual"],
        "Cessão de uso": ["cessão", "uso", "autorização", "permissão de uso", "direitos de uso", "transferência temporária", "cedente"],
        "Partilhamento de titularidade": ["partilhamento", "titularidade", "co-titularidade", "direitos compartilhados", "patente compartilhada", "colaboração de titularidade"],
        "Encomenda tecnológica": ["encomenda", "tecnológica", "desenvolvimento", "contrato de encomenda", "inovação tecnológica", "produção tecnológica"],
        "Serviço técnico especializado": ["serviço técnico", "consultoria", "assistência técnica", "especialização", "suporte especializado", "consultoria técnica"],
        "Transferência de Know-how": ["transferência", "know-how", "tecnologia", "conhecimento técnico", "experiência", "transferência de conhecimento", "capacitação"],
        "Acordo de parceria": ["acordo de parceria", "pesquisa", "desenvolvimento", "inovação", "colaboração", "cooperativa", "joint venture", "parceria", "acordo de colaboração"]
    }
    
    # Classificação inicial como "Informações insuficientes"
    classificacao = "Informações insuficientes"

    # Melhorando a busca por padrões no texto
    texto = texto.lower()

    # Verificar se algum dos termos de cada categoria está presente no texto
    for categoria, palavras in categorias.items():
        for palavra in palavras:
            # Use uma expressão regular para verificar se a palavra ou expressão aparece no texto
            if re.search(r'\b' + re.escape(palavra) + r'\b', texto):
                classificacao = categoria
                break
        if classificacao != "Informações insuficientes":
            break

    return classificacao

# Função para salvar as classificações em um arquivo CSV ou Excel
def salvar_gabarito(links, output_path, formato='csv'):
    data = []  # Lista para armazenar as classificações

    for link in links:
        texto = extrair_texto(link)
        classificacao = classificar_contrato(texto)
        data.append([classificacao])  # Salvar apenas as classificações

    # Criar um DataFrame a partir dos dados
    df = pd.DataFrame(data, columns=["Classificacao_Verdadeira"])

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
file_path = "C:/AndroidStudio/apis/classificacao/linkss.csv"  # Substitua pelo caminho correto do seu arquivo CSV

# Caminho para salvar o arquivo de saída (CSV ou Excel)
output_path_csv = "Gabarito_Contratos_Classificacoes.csv"

# Ler os links do arquivo CSV
links = ler_links_do_csv(file_path)

# Gerar o gabarito e salvar em CSV
salvar_gabarito(links, output_path_csv, formato='csv')

print(f"Gabarito gerado e salvo em {output_path_csv}")

