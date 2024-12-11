import os
import time
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Configuração do logging
logging.basicConfig(level=logging.INFO, filename='processamento.log', filemode='w')

# Configuração da chave da API do Claude
CLAUDE_API_KEY = "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"  # Substitua com o token de acesso da API do Claude

# Tipos de contrato predefinidos
tipos_contrato = [
    "Licenciamento de: patente", "Licenciamento de: programa de computador", "Licenciamento de: marcas",
    "Licenciamento de: desenho industrial", "Licenciamento de: cultivar", "Venda de: patente",
    "Venda de: programa de computador", "Venda de: marcas", "Venda de: desenho industrial", "Venda de: cultivar",
    "Cessão de uso", "Partilhamento de titularidade", "Encomenda tecnológica", "Serviço técnico especializado",
    "Transferência de Know-how", "Acordo de parceria"
]

# Função para analisar o texto do contrato usando a API do Claude
def analisar_contrato_com_claude(texto):
    inicio = time.time()  # Registra o tempo inicial

    prompt = f"""
    Você é um assistente especializado em classificação de contratos legais. 
    Sua tarefa é classificar o texto a seguir em uma das categorias: {', '.join(tipos_contrato)}.

    Diretrizes:
    1. Leia o texto cuidadosamente e procure palavras-chave relacionadas às categorias mencionadas.
    2. Se o texto for muito curto ou incompleto, use inferências baseadas nos termos e frases disponíveis.
    3. Se não for possível determinar com segurança a categoria, responda com 'Informações insuficientes'.
    4. Se houver indícios de múltiplas categorias, escolha a mais relevante com base no contexto geral.
    Texto do contrato:
    {texto[:2000]}  # Limite de 2000 caracteres para evitar excesso de tokens.
    """

    claude_url = "https://api.anthropic.com/v1/messages"  # Endpoint correto
    headers = {
        'x-api-key': CLAUDE_API_KEY,
        'Content-Type': 'application/json',
    }

    data = {
        "model": "claude-3-haiku-20240307",  # Modelo específico que você deseja usar
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,  # Limite de tokens que você pode usar
        "anthropic_version": "2023-06-01"
    }

try:
    # Enviando a requisição POST
    claude_url = "https://api.anthropic.com/v1/messages"  # Defina a variável antes
    response = requests.post(claude_url, json=data, headers=headers)
    response.raise_for_status()  # Levanta um erro se a requisição falhar
    
    # Resposta correta
    response_data = response.json()
    classificacao = response_data['content'][0]['text'].strip()
    print(f"Classificação: {classificacao}")

except requests.exceptions.RequestException as e:
    logging.error(f"Erro na requisição: {e}")
    logging.error(f"Detalhes do erro: {response.text if response else 'Sem resposta'}")
# Função para processar os links HTML
def processar_links(arquivo_links):
    try:
        with open(arquivo_links, 'r', encoding='utf-8') as file:
            links = file.readlines()
    except FileNotFoundError:
        print(f"Erro: O arquivo {arquivo_links} não foi encontrado.")
        return

    resultados = []

    for link in links:
        link = link.strip()
        try:
            response = requests.get(link, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            texto = soup.get_text(separator="\n").strip()

            texto = '\n'.join([linha.strip() for linha in texto.split("\n") if len(linha.strip()) > 10])

            if not texto.strip():
                logging.info(f"Texto insuficiente ou ilegível para o link {link}.")
                resultados.append({"Link": link, "Classificação": "Texto insuficiente ou ilegível", "Tempo de Resposta (s)": 0})
                continue

            # Classificar o contrato usando a API do Claude
            classificacao, tempo_resposta = analisar_contrato_com_claude(texto)
            resultados.append({"Link": link, "Classificação": classificacao, "Tempo de Resposta (s)": tempo_resposta})
            logging.info(f"Resultado para o link {link}: {classificacao}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao processar o link {link}: {e}")
            resultados.append({"Link": link, "Classificação": f"Erro: {str(e)}", "Tempo de Resposta (s)": 0})

    df = pd.DataFrame(resultados)
    output_file = "classificacao_contratos_claude.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Resultados salvos em {output_file}")

# Caminho do arquivo contendo os links
arquivo_links = r'C:\AndroidStudio\apis\testeclaude\links03.csv'
processar_links(arquivo_links)