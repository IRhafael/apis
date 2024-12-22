from anthropic import Anthropic, CompletionRequest

# Inicializar o cliente Anthropic com a chave da API
client = Anthropic(api_key="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")

# Criar a requisição de completude
request = CompletionRequest(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, world"}]
)

# Enviar a requisição e obter a resposta
response = client.create_completion(request)

# Verificar e imprimir a resposta
if response:
    print("Resposta da API:", response['completion'])
else:
    print("Erro na solicitação")



