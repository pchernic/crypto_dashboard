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

Execute os comandos abaixo no terminal para clonar, configurar o ambiente e rodar o app:

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
python -m venv venv
source venv/bin/activate  # no Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Série temporal 
![image](https://github.com/user-attachments/assets/835b8436-6b4b-4012-89de-e736ce8c3eb4)


### Comparação entre Criptos

![image](https://github.com/user-attachments/assets/e9b82751-35ff-4459-8e50-686fddf2ecc8)


