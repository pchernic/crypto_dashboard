# 💰 Crypto Dashboard

Este é um dashboard interativo construído com [Dash](https://dash.plotly.com/) e [Plotly](https://plotly.com/python/) que permite:

- 📊 Visualizar o preço histórico de uma criptomoeda
- 🧾 Acompanhar KPIs como preço atual, market cap, supply e variação de 24h
- 📈 Comparar duas criptos com base no percentual de valorização no período
- 🚀 Ver os maiores ganhadores e perdedores (Top Movers)

Os dados são fornecidos pela API do [CoinGecko](https://www.coingecko.com/en/api).

---

## ⚙️ Tecnologias utilizadas

- Python 3.10+
- Dash
- Plotly
- Requests
- Functools (`lru_cache` para caching local)

---

## ▶️ Como executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio

2. Crie e ative um ambiente virtual:
    python -m venv venv
    source venv/bin/activate  # no Windows: venv\Scripts\activate

3.Instale as dependências:
pip install -r requirements.txt

4. Execute o aplicativo:
python app.py

📌 To-do
 Adicionar exportação para CSV

 Deploy no Render/Heroku/Streamlit Cloud

 Página separada por criptomoeda

 Gráficos de volume de negociação

Conecte-se comigo: linkedin.com/in/paulochernicharo