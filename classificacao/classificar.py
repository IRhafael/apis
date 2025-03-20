import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Dicionário de categorias válidas com palavras-chave
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

def ler_gabarito(gabarito_path):
    """
    Lê o arquivo de gabarito contendo as classificações reais.
    """
    df = pd.read_csv(gabarito_path, encoding='ISO-8859-1')
    df[['Link', 'Classificacao_Verdadeira']] = df.iloc[:, 0].str.split(';', expand=True)
    df['Classificacao_Verdadeira'] = df['Classificacao_Verdadeira'].str.strip().str.lower()
    return df

def mapear_categoria(predicao):
    """
    Mapeia a classificação predita para a categoria correta com base no dicionário de palavras-chave.
    """
    for categoria, palavras_chave in tipos_contrato.items():
        if any(palavra in predicao.lower() for palavra in palavras_chave):
            return categoria
    return "informações insuficientes"

def comparar_classificacoes(df_classificacoes, df_gabarito):
    """
    Compara as classificações preditas com o gabarito e calcula métricas de desempenho.
    """
    if len(df_gabarito) != len(df_classificacoes):
        print("Erro: O número de registros no gabarito e nas classificações não corresponde.")
        return None, None, None, None

    y_true = df_gabarito['Classificacao_Verdadeira'].tolist()
    y_pred = df_classificacoes.iloc[:, 1].str.strip().str.lower().tolist()

    # Mapear classificações preditas para categorias válidas
    y_pred_mapeadas = [mapear_categoria(predicao) for predicao in y_pred]

    # Garantir que as classificações reais também estejam padronizadas
    y_true_mapeadas = [mapear_categoria(real) for real in y_true]

    # Calculando as métricas
    accuracy = accuracy_score(y_true_mapeadas, y_pred_mapeadas)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true_mapeadas, y_pred_mapeadas, average='weighted', zero_division=0)
    return accuracy, precision, recall, f1

# Caminhos dos arquivos
classificacoes_path = "C:/AndroidStudio/apis/classificacao/resultados/resultadosmistral.xlsx"
gabarito_path = "C:/AndroidStudio/apis/classificacao/gabarito.csv"

# Ler os arquivos
df_classificacoes = pd.read_excel(classificacoes_path)
df_gabarito = ler_gabarito(gabarito_path)

# Comparar classificações
if df_gabarito is not None:
    accuracy, precision, recall, f1 = comparar_classificacoes(df_classificacoes, df_gabarito)
    print(f"Acurácia: {accuracy:.4f}")
    print(f"Precisão: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")
else:
    print("Erro ao carregar o gabarito.")


