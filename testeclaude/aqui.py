import requests

api_key = "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"  # Substitua pelo seu token real

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "prompt": "Teste de autenticação"
}

try:
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=data
    )
    response.raise_for_status()
    print("Autenticação bem-sucedida. Resposta:", response.json())
except requests.exceptions.HTTPError as err:
    print(f"Erro na requisição: {err}")
except Exception as e:
    print(f"Outro erro ocorreu: {e}")


