import openai
import os
import PyPDF2
import docx
import urllib.request
from bs4 import BeautifulSoup
import time
import pandas as pd
from pdf2image import convert_from_path
import pytesseract
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO, filename='processamento.log', filemode='w')

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
    inicio = time.time()  # Registra o tempo inicial
    prompt = f"""
    Classifique o seguinte contrato em uma das categorias: {', '.join(tipos_contrato)}.
    Se não houver informações suficientes, responda com 'Informações insuficientes'.
    Texto do contrato:
    {texto[:2000]}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um assistente que classifica contratos."},
                {"role": "user", "content": prompt}
            ]
        )
        classificacao = response['choices'][0]['message']['content'].strip()
        fim = time.time()  # Calcula o tempo gasto
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
        try:
            # Baixar o conteúdo do link
            response = urllib.request.urlopen(link, timeout=10)
            content_type = response.headers.get_content_type()

            if content_type == 'application/pdf':
                # Ler PDFs
                with open('/tmp/temp.pdf', 'wb') as f:
                    f.write(response.read())
                with open('/tmp/temp.pdf', 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    texto = ''.join(page.extract_text() for page in reader.pages)

                # Usar OCR se necessário
                if not texto.strip():
                    pages = convert_from_path('/tmp/temp.pdf', 500)
                    texto = ''.join(pytesseract.image_to_string(page) for page in pages)

            elif content_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                # Ler arquivos Word
                with open('/tmp/temp.docx', 'wb') as f:
                    f.write(response.read())
                doc = docx.Document('/tmp/temp.docx')
                texto = '\n'.join([para.text for para in doc.paragraphs])
            else:
                # Tentar ler como HTML
                soup = BeautifulSoup(response, 'html.parser')
                texto = soup.get_text(separator="\n").strip()

            # Limpeza básica do texto extraído
            texto = '\n'.join([linha.strip() for linha in texto.split("\n") if len(linha.strip()) > 10])

            if not texto.strip():
                logging.info(f"Texto insuficiente ou ilegível para o link {link}.")
                resultados.append({"Link": link, "Classificação": "Texto insuficiente ou ilegível", "Tempo de Resposta (s)": 0})
                continue

            # Classificar o contrato usando a OpenAI
            classificacao, tempo_resposta = analisar_contrato_com_openai(texto)
            resultados.append({"Link": link, "Classificação": classificacao, "Tempo de Resposta (s)": tempo_resposta})
            logging.info(f"Resultado para o link {link}: {classificacao}")

        except urllib.error.HTTPError as e:
            logging.error(f"Erro HTTP ao processar o link {link}: {e}")
            resultados.append({"Link": link, "Classificação": f"Erro HTTP: {e.code}", "Tempo de Resposta (s)": 0})
        except Exception as e:
            logging.error(f"Erro ao processar o link {link}: {e}")
            resultados.append({"Link": link, "Classificação": f"Erro: {str(e)}", "Tempo de Resposta (s)": 0})

    # Salvar resultados em um arquivo Excel
    df = pd.DataFrame(resultados)
    output_file = "classificacao_contratos.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Resultados salvos em {output_file}")

# Caminho do arquivo contendo os links
arquivo_links = r'C:\AndroidStudio\apis\testegpt\CHATGPT\extratos_200_links.csv'
processar_links(arquivo_links)