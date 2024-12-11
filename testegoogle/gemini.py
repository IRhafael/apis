import google.auth
from google.auth.transport.requests import Request
import google.generativeai as genai
import pandas as pd
import os
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import logging
import time

# Configuração do logging
logging.basicConfig(level=logging.INFO, filename='processamento.log', filemode='w')

# Caminho para o arquivo JSON da conta de serviço (substitua com o caminho correto)
SERVICE_ACCOUNT_FILE = "C:/AndroidStudio/apis/testegoogle/geminipython-423823-215feef97ab5.json"

# Função para autenticar usando a conta de serviço
def authenticate_with_service_account():
    credentials, project = google.auth.load_credentials_from_file(SERVICE_ACCOUNT_FILE)
    
    # Se as credenciais precisarem ser renovadas, faça isso
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        
    return credentials

# Autentica e obtém as credenciais da conta de serviço
creds = authenticate_with_service_account()

# Configura a biblioteca Google Generative AI com as credenciais obtidas
genai.configure(credentials=creds)

# Tipos de contrato predefinidos
tipos_contrato = [
    "Licenciamento de: patente", "Licenciamento de: programa de computador", "Licenciamento de: marcas",
    "Licenciamento de: desenho industrial", "Licenciamento de: cultivar", "Venda de: patente",
    "Venda de: programa de computador", "Venda de: marcas", "Venda de: desenho industrial", "Venda de: cultivar",
    "Cessão de uso", "Partilhamento de titularidade", "Encomenda tecnológica", "Serviço técnico especializado",
    "Tranferência de Know-how", "Acordo de parceria"
]

# Função para analisar o texto do contrato usando a API Gemini
def analisar_contrato_com_gemini(texto):
    inicio = time.time()  # Registra o tempo inicial
    try:
        # Configure o modelo Gemini
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"""
        Você é um assistente especializado em classificação de contratos legais. 
        Sua tarefa é classificar o texto a seguir em uma das categorias: {', '.join(tipos_contrato)}.

        Diretrizes:
        1. Leia o texto cuidadosamente e procure palavras-chave relacionadas às categorias mencionadas.
        2. Se o texto for muito curto ou incompleto, use inferências baseadas nos termos e frases disponíveis.
        3. Se não for possível determinar com segurança a categoria, responda com 'Informações insuficientes'.
        4. Se houver indícios de múltiplas categorias, escolha a mais relevante com base no contexto geral.
        5. Não dê informações extras, somente classifique o tipo de contrato.
        
        Texto do contrato:
        {texto[:2000]}  # Limite de 2000 caracteres
        """)
        classificacao = response.text.strip()
        fim = time.time()  # Calcula o tempo gasto
        return classificacao, fim - inicio
    except Exception as e:
        return f"Erro: {str(e)}", 0

# Função para processar os links HTML
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
        
        # Corrigir barras extras e garantir que a URL comece com 'https://'
        link = link.replace('https:/', 'https://')  # Corrige URL mal formatada
        logging.info(f"Processando o link: {link}")

        try:
            # Baixar o conteúdo do link
            response = urllib.request.urlopen(link, timeout=10)
            soup = BeautifulSoup(response, 'html.parser')
            texto = soup.get_text(separator="\n").strip()

            # Limpeza básica do texto extraído
            texto = '\n'.join([linha.strip() for linha in texto.split("\n") if len(linha.strip()) > 10])

            if not texto.strip():
                logging.info(f"Texto insuficiente ou ilegível para o link {link}.")
                resultados.append({"Link": link, "Classificação": "Texto insuficiente ou ilegível", "Tempo de Resposta (s)": 0})
                continue

            # Classificar o contrato usando a API Gemini
            classificacao, tempo_resposta = analisar_contrato_com_gemini(texto)
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
arquivo_links = r'C:\AndroidStudio\apis\testegoogle\link2.csv'
processar_links(arquivo_links)