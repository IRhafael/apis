import openai
import urllib.request
from bs4 import BeautifulSoup
import time
import pandas as pd
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO, filename='processamento.log', filemode='w')

# Configuração da chave da API da OpenAI
openai.api_key = "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"

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

# Função para analisar o texto do contrato usando a OpenAI
def analisar_contrato_com_openai(texto):
    inicio = time.time()  # Registra o tempo inicial
    prompt = f"""
    Você é um assistente especializado em classificação de contratos legais. 
    Sua tarefa é classificar o texto a seguir em uma das categorias: {', '.join(tipos_contrato.keys())}.

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
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "Você é um assistente especializado em análise de contratos legais."},
                      {"role": "user", "content": prompt}]
        )
        classificacao = response['choices'][0]['message']['content'].strip()
        fim = time.time()  # Calcula o tempo gasto
        return classificacao, fim - inicio
    except Exception as e:
        return f"Erro: {str(e)}", 0

# Função para processar os links HTML com controle de taxa de requisições
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

            # Aguardar 1 segundo entre as requisições para evitar exceder o limite
            time.sleep(1)

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
arquivo_links = r'C:\AndroidStudio/apis/testegpt/extratos_200_links.csv'
processar_links(arquivo_links)
