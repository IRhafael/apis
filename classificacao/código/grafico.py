import matplotlib.pyplot as plt

# Dados das métricas
results = {
    "MISTRAL": [0.4774, 0.4645, 0.4774, 0.4102],
    "LLAMA": [0.4372, 0.6119, 0.4372, 0.4651],
    "CHATGPT": [0.4874, 0.4732, 0.4874, 0.4467]
}
metrics = ["Acurácia", "Precisão", "Recall", "F1-Score"]

# Gerar gráficos para cada API
for model, values in results.items():
    plt.figure(figsize=(8, 5))
    plt.bar(metrics, values, color='skyblue', edgecolor='black', alpha=0.8)
    plt.ylim(0, 1)
    plt.title(f"Desempenho das Métricas - {model}", fontsize=14)
    plt.ylabel("Pontuação", fontsize=12)
    plt.xlabel("Métricas", fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()
