import openai
import os
import PyPDF2
import docx
import re
import validators
import urllib.request
from bs4 import BeautifulSoup
import time
import pandas as pd

# Configuração da chave da API da OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY', 'sk-proj-M94NhKYdeMRfwHHuhvNYT3BlbkFJlnJ2QaPcYwUkzzUwx7WT')

# Tipos de contrato predefinidos
tipos_contrato = [
    "Licenciamento de: patente", "Licenciamento de: programa de computador", "Licenciamento de: marcas",
    "Licenciamento de: desenho industrial", "Licenciamento de: cultivar", "Venda de: patente",
    "Venda de: programa de computador", "Venda de: marcas", "Venda de: desenho industrial", "Venda de: cultivar",
    "Cessão de uso", "Partilhamento de titularidade", "Encomenda tecnológica", "Serviço técnico especializado",
    "Know-how", "Acordo de parceria"
]

# Função para analisar o texto do contrato usando a OpenAI
def analisar_contrato_com_openai(texto):
    inicio = time.time()  # Inicia o cronômetro
    prompt = f"""
    Classifique o seguinte contrato em uma das categorias: {', '.join(tipos_contrato)}.
    Responda apenas com a categoria. Texto do contrato:
    {texto[:2000]}  # Limita o texto para evitar excesso de tokens
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Ou "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "Você é um assistente que classifica contratos."},
                {"role": "user", "content": prompt}
            ]
        )
        classificacao = response['choices'][0]['message']['content'].strip()
        fim = time.time()  # Finaliza o cronômetro
        return classificacao, fim - inicio
    except Exception as e:
        return f"Erro: {str(e)}", 0

# Função para processar os links
def processar_links(arquivo_links):
    # Ler o arquivo com os links
    try:
        with open(arquivo_links, 'r', encoding='utf-8') as file:
            links = file.readlines()
    except FileNotFoundError:
        print(f"Erro: O arquivo {arquivo_links} não foi encontrado.")
        return

    resultados = []

    # Processar cada link
    for link in links:
        link = link.strip()
        if not validators.url(link):
            print(f"Link inválido: {link}")
            resultados.append({"Link": link, "Classificação": "Link inválido", "Tempo de Resposta (s)": 0})
            continue

        try:
            # Baixar o conteúdo do link
            response = urllib.request.urlopen(link)
            content_type = response.headers.get_content_type()

            if content_type == 'application/pdf':
                # Ler PDFs
                with open('/tmp/temp.pdf', 'wb') as f:
                    f.write(response.read())
                with open('/tmp/temp.pdf', 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    texto = ''.join(page.extract_text() for page in reader.pages)
            elif content_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                # Ler arquivos Word
                with open('/tmp/temp.docx', 'wb') as f:
                    f.write(response.read())
                doc = docx.Document('/tmp/temp.docx')
                texto = '\n'.join([para.text for para in doc.paragraphs])
            else:
                # Tentar ler como HTML
                soup = BeautifulSoup(response, 'html.parser')
                texto = soup.get_text()

            # Classificar o contrato usando a OpenAI
            classificacao, tempo_resposta = analisar_contrato_com_openai(texto)
            resultados.append({"Link": link, "Classificação": classificacao, "Tempo de Resposta (s)": tempo_resposta})
            print(f"Resultado para o link {link}: {classificacao}")
        except Exception as e:
            print(f"Erro ao processar o link {link}: {e}")
            resultados.append({"Link": link, "Classificação": f"Erro: {e}", "Tempo de Resposta (s)": 0})

    # Salvar resultados em um arquivo Excel
    df = pd.DataFrame(resultados)
    output_file = "classificacao_contratos.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Resultados salvos em {output_file}")

# Caminho do arquivo contendo os 200 links
arquivo_links = r'C:\AndroidStudio\apis\testegpt\CHATGPT\extratos_200_links.csv'
processar_links(arquivo_links)


