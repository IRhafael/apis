import os
import re
import requests
from google.cloud import storage
import json

# Credenciais Google Cloud (ajuste conforme necessário)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "geminipython-423823-1f125a7736f8.json"
storage_client = storage.Client()

# Nome do seu bucket no Google Cloud Storage
bucket_name = "geminipro1"  # Substitua pelo nome correto

# Substitua 'YOUR_API_KEY' pela sua chave de API do Google Cloud
API_KEY = 'AIzaSyC_Q5wOhvo240V4PmnJGcHCzc9X_PRCfZg'

def analisar_documento(link_documento):
    """
    Função principal para analisar o documento a partir de um link.
    Baixa o documento, envia para a API e extrai informações relevantes.
    """
    texto = baixar_documento(link_documento)
    resposta_api = enviar_solicitacao_palm(texto)
    informacoes = extrair_informacoes(resposta_api)
    return informacoes

def baixar_documento(link_documento):
    """
    Baixa o documento do link fornecido e o carrega para o Google Cloud Storage.
    Extrai o texto conforme o tipo de documento.
    """
    try:
        response = requests.get(link_documento)
        response.raise_for_status()
        file_name = link_documento.split("/")[-1]

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.upload_from_string(response.content)

        content_type = response.headers.get('Content-Type')
        if 'pdf' in content_type:
            return extrair_texto_pdf(response.content)
        elif 'html' in content_type:
            return response.text  # Retornar o texto HTML diretamente
        elif 'word' in content_type or 'docx' in content_type:
            return extrair_texto_docx(response.content)
        elif 'json' in content_type:
            return extrair_texto_json(response.json())
        else:
            raise Exception("Tipo de documento não suportado")

    except Exception as e:
        raise Exception(f"Erro ao baixar ou processar o documento: {e}")

def extrair_texto_pdf(content):
    # Implemente a extração de texto de PDF aqui
    pass

def extrair_texto_docx(content):
    # Implemente a extração de texto de DOCX aqui
    pass

def extrair_texto_json(data):
    return json.dumps(data, indent=4)

def enviar_solicitacao_palm(texto):
    """
 Classifique o extrato de contrato em algum desses tipos: Licenciamento de: patente, programa de computador, marcas, desenho industrial ou cultivar,
 venda de: patente, programa de computador, marcas, desenho industrial ou cultivar,
 cessão de uso, partilhamento de titularidade, encomenda tecnológica, serviço técnico especializado,
 know-how, acordo de parceria.
 caso não classifique em nenhum desses tipos coloque o tipo outros.
 após classificar o tipo de extrato identifique as partes envolvidas com seus respectivos cnpjs,
 o objeto do contrato,o prazo de validade e a data da assinatura.
 caso encontre um numero de patente ou um programa de computador ou uma marca ou um desenho industrial ou uma cultivar ou alguma descrição da tecnologia, 
 printe no terminal.
    """
    url = f"https://language.googleapis.com/v1/documents:analyzeEntities?key={API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    # Instruções específicas para a API sobre como ela deve funcionar
    payload = {
        "document": {
            "type": "PLAIN_TEXT",
            "content": texto
        },
        "encodingType": "UTF8"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro ao enviar solicitação para a API: {e}")

def extrair_informacoes(resposta_api):
    """
    Extrai informações específicas da resposta da API, como partes envolvidas, CNPJs e números de patente.
    """
    informacoes = {
        "Tipo de Extrato": "Outros",
        "Partes envolvidas": [],
        "CNPJs": [],
        "Objeto do Contrato": "",
        "Prazo de Validade": "",
        "Data de Assinatura": "",
        "Números de Patente": [],
        "Programas de Computador": [],
        "Marcas": [],
        "Desenhos Industriais": [],
        "Cultivares": [],
        "Descrição da Tecnologia": ""
    }

    # Extraindo entidades relevantes da resposta da API
    entities = resposta_api.get('entities', [])

    for entity in entities:
        entity_type = entity.get('type', '')
        entity_name = entity.get('name', '')

        # Filtrando entidades relevantes
        if entity_type == 'ORGANIZATION':
            # Adicionar apenas organizações que são relevantes para partes envolvidas
            if 'Federal' in entity_name or 'Laboratório' in entity_name:
                informacoes["Partes envolvidas"].append(entity_name)
        elif entity_type == 'OTHER':
            # Tratar outros tipos de entidades, como CNPJ e números de patente
            if re.match(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', entity_name):  # Verificar CNPJ
                informacoes["CNPJs"].append(entity_name)
            elif re.match(r'[A-Z]{2}\d{8}', entity_name):  # Verificar número de patente
                informacoes["Números de Patente"].append(entity_name)

    # Aqui você pode adicionar lógica adicional para classificar o tipo de extrato e
    # extrair outras informações específicas com base no texto e nas entidades extraídas.

    return informacoes

if __name__ == "__main__":
    link_documento = input("Digite o link do documento: ")
    informacoes = analisar_documento(link_documento)
    print(json.dumps(informacoes, indent=4))
