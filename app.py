from dash import Dash, dcc, html, Input, Output
import requests
import plotly.graph_objs as go
from datetime import datetime

app = Dash(__name__)
server = app.server

# Cores e estilo centralizado
COLORS = {
    "bg": "#0d1117",
    "card": "#1c1f26",
    "text": "#c9d1d9",
    "accent": "#58a6ff",
    "error": "#f85149",
    "gain": "#16c784",
    "border": "#2c313a"
}

STYLES = {
    "card": {
        'padding': '15px',
        'backgroundColor': COLORS["card"],
        'borderRadius': '6px',
        'flex': '1',
        'textAlign': 'center',
        'minWidth': '200px'
    },
    "tableCell": {
        'padding': '6px 10px',
        'borderBottom': f'1px solid {COLORS["border"]}'
    }
}

# =================== Funcoes de API ===================
def get_coin_data(coin_id="bitcoin", days="30"):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "prices" not in data or not data["prices"]:
            raise ValueError(f"Campo 'prices' ausente ou vazio na resposta para '{coin_id}'")

        prices = data["prices"]
        return [p[0] for p in prices], [p[1] for p in prices]

    except Exception as e:
        print(f"[Erro get_coin_data] {coin_id}: {e}")
        raise Exception(f"Erro ao buscar historico da moeda '{coin_id}': {e}")

def get_coin_info(coin_id="bitcoin"):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "market_data" not in data:
            raise ValueError(f"'market_data' nao encontrado para '{coin_id}'")

        return data

    except Exception as e:
        print(f"[Erro get_coin_info] {coin_id}: {e}")
        raise Exception(f"Erro ao buscar dados da moeda '{coin_id}': {e}")

def get_top_movers(days="7", limit=10):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1,
        "price_change_percentage": f"{days}d"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        key = f"price_change_percentage_{days}d_in_currency"
        if not data or not isinstance(data, list):
            raise ValueError("Resposta invalida da API")

        gainers = sorted([c for c in data if c.get(key)], key=lambda x: x[key], reverse=True)[:limit]
        losers = sorted([c for c in data if c.get(key)], key=lambda x: x[key])[:limit]
        return gainers, losers

    except Exception as e:
        print(f"[Erro get_top_movers]: {e}")
        raise Exception(f"Erro ao buscar top movers: {e}")

# =================== Layout ===================
app.layout = html.Div(style={
    'backgroundColor': COLORS["bg"],
    'padding': '30px',
    'fontFamily': 'Helvetica, sans-serif'
}, children=[
    html.H1("\U0001F4B0 Crypto Dashboard", style={'textAlign': 'center', 'color': COLORS["text"]}),

    html.Div([
        dcc.Dropdown(
            id='coin-input',
            options=[
                {'label': 'Bitcoin (BTC)', 'value': 'bitcoin'},
                {'label': 'Ethereum (ETH)', 'value': 'ethereum'},
                {'label': 'Solana (SOL)', 'value': 'solana'},
                {'label': 'Cardano (ADA)', 'value': 'cardano'},
                {'label': 'Dogecoin (DOGE)', 'value': 'dogecoin'},
                {'label': 'Toncoin (TON)', 'value': 'ton'}
            ],
            value='bitcoin',
            searchable=True,
            placeholder='Escolha uma cripto...',
            style={
                'width': '300px',
                'backgroundColor': COLORS["card"],
                'color': COLORS["text"]
            }
        ),
        dcc.Dropdown(
            id='days-dropdown',
            options=[{'label': f'{d} Dias', 'value': str(d)} for d in [7, 30, 90]],
            value='30',
            style={
                'width': '150px',
                'marginLeft': '20px',
                'backgroundColor': COLORS["card"],
                'color': COLORS["text"]
            }
        )
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'marginBottom': '30px'}),

    dcc.Loading(
        type='circle',
        color=COLORS["accent"],
        children=[
            html.Div(id='kpi-cards', style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'gap': '20px',
                'marginBottom': '40px'
            }),
            dcc.Graph(id='price-chart')
        ]
    ),

    html.H2("\U0001F4C8 Top Movers", style={'color': COLORS["accent"], 'marginTop': '60px'}),

    dcc.Dropdown(
        id="mover-period",
        options=[
            {"label": "\u00daltimos 7 dias", "value": "7"},
            {"label": "\u00daltimos 30 dias", "value": "30"}
        ],
        value="7",
        style={
            'width': '200px',
            'marginBottom': '20px',
            'backgroundColor': COLORS["card"],
            'color': COLORS["text"]
        }
    ),

    html.Div(id="top-movers", style={
        'display': 'flex',
        'gap': '40px',
        'flexWrap': 'wrap'
    })
])

# =================== Callbacks ===================
@app.callback(
    Output('price-chart', 'figure'),
    Output('kpi-cards', 'children'),
    Input('coin-input', 'value'),
    Input('days-dropdown', 'value')
)
def update_dashboard(coin, days):
    try:
        timestamps, prices = get_coin_data(coin, days)
        info = get_coin_info(coin)

        market = info["market_data"]
        dates = [datetime.fromtimestamp(ts / 1000) for ts in timestamps]

        def kpi(label, value, color=COLORS["text"]):
            return html.Div([
                html.Div(label, style={'color': COLORS["accent"]}),
                html.Div(value, style={'fontSize': '20px', 'fontWeight': 'bold', 'color': color})
            ], style=STYLES["card"])

        kpis = [
            kpi("Current Price", f"${market['current_price']['usd']:,.2f}"),
            kpi("Market Cap", f"${market['market_cap']['usd'] / 1e9:.2f} B"),
            kpi("24h Change", f"{market['price_change_percentage_24h']:+.2f}%",
                COLORS["gain"] if market['price_change_percentage_24h'] >= 0 else COLORS["error"]),
            kpi("Circulating Supply", f"{market['circulating_supply']:,.0f}")
        ]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=prices, mode='lines', line=dict(color=COLORS["accent"])))
        fig.update_layout(
            plot_bgcolor=COLORS["bg"],
            paper_bgcolor=COLORS["bg"],
            font=dict(color=COLORS["text"]),
            margin=dict(l=40, r=40, t=40, b=20),
            height=600,
            xaxis_title="Date",
            yaxis_title="Price (USD)"
        )
        return fig, kpis

    except Exception as e:
        return go.Figure(), [html.Div(f"Erro ao carregar dados: {str(e)}", style={'color': COLORS["error"]})]

@app.callback(
    Output("top-movers", "children"),
    Input("mover-period", "value")
)
def update_top_movers(days):
    try:
        gainers, losers = get_top_movers(days)

        def make_table(title, coins, color):
            rows = []
            for i, coin in enumerate(coins):
                pct = coin[f"price_change_percentage_{days}d_in_currency"]
                rows.append(html.Tr([
                    html.Td(f"{i+1}.", style=STYLES["tableCell"]),
                    html.Td(coin["name"], style=STYLES["tableCell"]),
                    html.Td(f"{pct:.2f}%", style={
                        **STYLES["tableCell"],
                        'color': color,
                        'textAlign': 'right'
                    })
                ]))
            return html.Div([
                html.H4(title, style={'color': color, 'marginBottom': '10px'}),
                html.Table(rows, style={
                    'color': COLORS["text"],
                    'backgroundColor': COLORS["card"],
                    'borderCollapse': 'collapse',
                    'width': '100%',
                    'border': f'1px solid {COLORS["accent"]}',
                    'borderRadius': '5px'
                })
            ], style={'flex': '1', 'minWidth': '300px'})

        return [
            make_table("\U0001F4C8 Gainers", gainers, COLORS["gain"]),
            make_table("\U0001F4C9 Losers", losers, COLORS["error"])
        ]

    except Exception as e:
        return [html.Div(f"Erro: {str(e)}", style={'color': COLORS["error"]})]

if __name__ == '__main__':
    print("\U0001F680 Iniciando o dashboard...")
    app.run(debug=True)
