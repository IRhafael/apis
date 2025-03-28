
# 📑 Sistema de Classificação Automática de Contratos de Inovação

Pipeline para classificação de extratos contratuais do DOU usando APIs de IA (ChatGPT, LLaMA e Mistral), desenvolvido para o TCC em Análise e Desenvolvimento de Sistemas pelo Instituto Federal do Piaui.


📂 Estrutura do Repositório

APIS/
├── dados/
│   ├── links04.csv                 # 200 URLs de contratos (input)
│   └── extratos_200_links.csv      # Textos extraídos
├── resultados/
│   ├── resultadosGPT.xlsx          # Exemplo de saída 
│   ├── resultadosLLAMA.xlsx        # Saída LLaMA 
│   └── resultadosMistral.xlsx      # Saída Mistral
├── scripts/
│   ├── api_gpt.py                  # Integração OpenAI
│   ├── api_llama.py                # Integração Meta
│   └── api_mistral.py              # Integração Mistral AI
└── processamento.log               # Logs detalhados

🛠 Como Reproduzir
Pré-requisitos

Python 3.10+
Arquivo .env com chaves de API:
OPENAI_KEY=sk-...
LLAMA_KEY=...
MISTRAL_KEY=...

- Passo a Passo -

1.Preparação:
git clone https://github.com/IRhafael/apis.git
cd APIS
pip install -r requirements.txt
2.Execução:
python scripts/api_gpt.py --input dados/links04.csv #caminho do arquivo com os links
--output resultadosa/resultadosGPT.xlsx #caminho do arquivo com os resultados

3.Saída Esperada (exemplo):
   URL	 |     Classificação
--------------------------------
[link1]	 |   "Acordo de Parceria"	
