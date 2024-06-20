import openai
import PyPDF2
import docx
import os
import pandas as pd
import re
import validators
import urllib.request
import mimetypes
from bs4 import BeautifulSoup

# Substitua 'sua-chave-api-aqui' pela sua chave da API da OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY', 'sk-proj-M94NhKYdeMRfwHHuhvNYT3BlbkFJlnJ2QaPcYwUkzzUwx7WT')

def analisar_patente(descricao):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em análise de patentes."},
                {"role": "user", "content": f"Analise a seguinte descrição de patente e forneça um resumo detalhado: {descricao}"}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message['content'].strip()
    except openai.error.OpenAIError as e:
        if "quota" in str(e):
            return "Erro: Você excedeu sua quota atual. Verifique seu plano e detalhes de faturamento."
        elif "invalid_api_key" in str(e):
            return "Erro: Chave da API inválida. Verifique se você inseriu a chave correta."
        elif "rate_limit" in str(e):
            return "Erro: Limite de taxa atingido. Tente novamente mais tarde."
        else:
            return f"Ocorreu um erro: {e}"

def extrair_informacoes(texto):
    cnpjs = re.findall(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', texto)
    numeros_patente = re.findall(r'\b[0-9]{7}\b', texto)
    autores_colaboradores = re.findall(r'\b[A-Z][a-z]+\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)?\b', texto)

    return {
        "CNPJs": cnpjs,
        "Números de Patente": numeros_patente,
        "Autores e Colaboradores": autores_colaboradores
    }

def ler_documento_txt(nome_do_arquivo):
    with open(nome_do_arquivo, 'r', encoding='utf-8') as file:
        return file.read()

def ler_documento_pdf(nome_do_arquivo):
    with open(nome_do_arquivo, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text()
        return texto

def ler_documento_word(nome_do_arquivo):
    doc = docx.Document(nome_do_arquivo)
    texto = ""
    for paragraph in doc.paragraphs:
        texto += paragraph.text + "\n"
    return texto

def ler_documento_excel(nome_do_arquivo):
    df = pd.read_excel(nome_do_arquivo)
    return df.to_string(index=False)

def ler_documento_html(url):
    with urllib.request.urlopen(url) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        texto = soup.get_text()
        return texto

def ler_documento(nome_do_arquivo):
    tipo_mime, _ = mimetypes.guess_type(nome_do_arquivo)
    if tipo_mime == 'text/plain':
        return ler_documento_txt(nome_do_arquivo)
    elif tipo_mime == 'application/pdf':
        return ler_documento_pdf(nome_do_arquivo)
    elif tipo_mime in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
        return ler_documento_word(nome_do_arquivo)
    elif tipo_mime in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
        return ler_documento_excel(nome_do_arquivo)
    else:
        raise ValueError("Formato de arquivo não suportado. Use .txt, .pdf, .docx, .xls ou .xlsx")

if __name__ == "__main__":
    entrada = input("Por favor, insira o caminho do arquivo ou o link da planilha: ").strip()

    if validators.url(entrada):
        # Verifica se a entrada é um URL válido
        try:
            with urllib.request.urlopen(entrada) as response:
                tipo_mime = response.info().get_content_type()
                if 'html' in tipo_mime:
                    descricao_documento = ler_documento_html(entrada)
                else:
                    extensao = mimetypes.guess_extension(tipo_mime)
                    if not extensao:
                        raise ValueError("Não foi possível determinar a extensão do arquivo.")
                    nome_temp = f'temp_file{extensao}'
                    with open(nome_temp, 'wb') as out_file:
                        out_file.write(response.read())
                    descricao_documento = ler_documento(nome_temp)
                    os.remove(nome_temp)  # Remove o arquivo temporário após a leitura
        except Exception as e:
            print(f"Erro ao baixar ou ler o arquivo da URL: {e}")
            exit(1)
    else:
        # Verifica o tipo de arquivo e lê o conteúdo
        if not os.path.isfile(entrada):
            print("Erro: Caminho do arquivo inválido.")
            exit(1)

        try:
            descricao_documento = ler_documento(entrada)
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            exit(1)

    # Extrair informações específicas
    informacoes = extrair_informacoes(descricao_documento)

    # Analisar o conteúdo do documento
    resumo = analisar_patente(descricao_documento)

    # Mostrar as informações extraídas e o resumo gerado
    print("Informações extraídas do documento:")
    print(f"CNPJs: {informacoes['CNPJs']}")
    print(f"Números de Patente: {informacoes['Números de Patente']}")
    print(f"Autores e Colaboradores: {informacoes['Autores e Colaboradores']}")

    print("\nResumo do documento:")
    print(resumo)






