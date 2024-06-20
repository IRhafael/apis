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

def analisar_documento(link_documento):
    texto = baixar_documento(link_documento)
    resposta_api = enviar_solicitacao_palm(texto)
    informacoes = extrair_informacoes(resposta_api)
    return informacoes

def baixar_documento(link_documento):
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
    # Este trecho de código envia o texto para a API e obtém a resposta
    # Aqui, você deve implementar a lógica para enviar o texto para a API e receber a resposta
    # Substitua o código abaixo pela sua implementação real
    resposta_da_api = {
        "Partes envolvidas": ["Universidade Federal de Minas Gerais (UFMG)", "Laboratório Bio-Vet Ltda."],
        "Objeto do contrato": "Licenciamento, a título oneroso, com exclusividade, pela UFMG à LICENCIADA, dos direitos para uso, desenvolvimento, produção, exploração comercial, prestação de serviços e/ou obtenção de qualquer vantagem econômica relacionada à TECNOLOGIA intitulada \"COMPOSIÇÃO VACINAL INATIVADA POLIVALENTE PARA CONTROLE DE INFECÇÕES POR STREPTOCOCCUS AGALACTIAE EM TILÁPIA DO NILO E USOS\", depositada junto ao Instituto Nacional da Propriedade Industrial - INPI sob o número BR1020230217028, em 18/10/2023, registrado perante o Ministério da Ministério da Agricultura e Pecuária (MAPA) sob o nº 10.561/2023.",
        "Valor do contrato": "Não informado",
        "Vigência do contrato": "16/02/2024",
        "Modalidade de licitação": "Não informado",
        "Número do processo": "23072.266279/2023-49",
        "Data de assinatura": "16/02/2024"
    }
    return resposta_da_api

def extrair_informacoes(resposta_api):
    informacoes = {}
    informacoes["Partes envolvidas"] = resposta_api.get("Partes envolvidas")
    informacoes["Objeto do contrato"] = resposta_api.get("Objeto do contrato")
    informacoes["Valor do contrato"] = resposta_api.get("Valor do contrato")
    informacoes["Vigência do contrato"] = resposta_api.get("Vigência do contrato")
    informacoes["Modalidade de licitação"] = resposta_api.get("Modalidade de licitação")
    informacoes["Número do processo"] = resposta_api.get("Número do processo")
    return informacoes

if __name__ == "__main__":
    link_documento = input("Digite o link do documento: ")
    informacoes = analisar_documento(link_documento)
    print(informacoes)




