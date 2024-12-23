import time
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from llamaapi import LlamaAPI

# Configuração do logging
logging.basicConfig(level=logging.INFO, filename='processamento.log', filemode='w')

# Configuração da chave da API do Llama
LLAMA_API_KEY = "LA-17fd50dacb4a45288ea892d6769a6ddd89340018688447fda07038790a29b5f6"  # Substitua com o seu token de API

# Inicialização do SDK
llama = LlamaAPI(LLAMA_API_KEY)

# Tipos de contrato predefinidos
tipos_contrato = {
    "Licenciamento de: patente": ["licenciamento", "patente", "exploração", "INPI", "tecnologia", "registro", "propriedade intelectual", "exclusividade"],
    "Licenciamento de: programa de computador": ["licenciamento", "software", "programa de computador", "código-fonte", "direitos de uso", "desenvolvimento de software"],
    "Licenciamento de: marcas": ["licenciamento", "marca", "registro de marca", "direitos de uso", "marca registrada", "branding"],
    "Licenciamento de: desenho industrial": ["licenciamento", "desenho industrial", "design", "inovação", "propriedade intelectual", "design industrial"],
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

# Função para analisar o texto do contrato usando a API do Llama
def analisar_contrato_com_llama(texto):
    inicio = time.time()  # Registra o tempo inicial

    prompt = f"""
    Você é um assistente especializado em classificação de contratos legais. 
    Sua tarefa é classificar o texto a seguir em uma das categorias: {', '.join(tipos_contrato)}.

    Diretrizes:
    1. Leia o texto cuidadosamente e procure palavras-chave relacionadas às categorias mencionadas.
    2. Se o texto for muito curto ou incompleto, use inferências baseadas nos termos e frases disponíveis.
    3. Se não for possível determinar com segurança a categoria, responda com 'Informações insuficientes'.
    4. Se houver indícios de múltiplas categorias, escolha a mais relevante com base no contexto geral.
    5. Não dê informações extras, somente classifique o tipo de contrato.
    6. 
    Texto do contrato:
    {texto[:2000]}  # Limite de 2000 caracteres para evitar excesso de tokens.
    """

    api_request_json = {
        "model": "llama3.1-70b",  # Substitua com o modelo correto
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }

    try:
        response = llama.run(api_request_json)

        # Convertendo a resposta para um dicionário
        response_dict = response.json()

        # Verifique o que está retornando na resposta
        print("Resposta da API:", response_dict)

        # Ajuste conforme a estrutura da resposta da API
        classificacao = response_dict['choices'][0]['message']['content']
        fim = time.time()  # Calcula o tempo gasto
        return classificacao, fim - inicio
    except Exception as e:
        return f"Erro: {str(e)}", 0

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

            # Classificar o contrato usando a API do Llama
            classificacao, tempo_resposta = analisar_contrato_com_llama(texto)
            resultados.append({"Link": link, "Classificação": classificacao, "Tempo de Resposta (s)": tempo_resposta})
            logging.info(f"Resultado para o link {link}: {classificacao}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao processar o link {link}: {e}")
            resultados.append({"Link": link, "Classificação": f"Erro: {str(e)}", "Tempo de Resposta (s)": 0})

    df = pd.DataFrame(resultados)
    output_file = "classificacao_contratos_llama.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Resultados salvos em {output_file}")

# Caminho do arquivo contendo os links
arquivo_links = r'C:\AndroidStudio\apis\testellama\links.csv'
processar_links(arquivo_links)

