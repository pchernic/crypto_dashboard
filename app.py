from dash import Dash, dcc, html, Input, Output
import requests
import requests.exceptions
import plotly.graph_objs as go
from datetime import datetime
from functools import lru_cache

app = Dash(__name__)
server = app.server

# Cores
BG_COLOR = "#0d1117"
CARD_COLOR = "#161b22"
TEXT_COLOR = "#c9d1d9"
ACCENT_COLOR = "#58a6ff"
ERROR_COLOR = "#f85149"

# ----- Funções com CACHE -----

@lru_cache(maxsize=64)
def get_coin_data(coin_id="bitcoin", days="30"):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {"vs_currency": "usd", "days": days}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        prices = data["prices"]
        return [p[0] for p in prices], [p[1] for p in prices]
    except requests.exceptions.RequestException as e:
        raise Exception("Erro ao buscar histórico da moeda") from e

@lru_cache(maxsize=64)
def get_coin_info(coin_id="bitcoin"):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception("Erro ao buscar dados da moeda") from e

def get_top_movers(days="7", limit=10):
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 250,
            "page": 1,
            "price_change_percentage": f"{days}d"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        key = f"price_change_percentage_{days}d_in_currency"
        gainers = sorted([c for c in data if c.get(key)], key=lambda x: x[key], reverse=True)[:limit]
        losers = sorted([c for c in data if c.get(key)], key=lambda x: x[key])[:limit]
        return gainers, losers
    except requests.exceptions.RequestException as e:
        raise Exception("Erro ao buscar top movers") from e

# ----- Layout -----

app.layout = html.Div(style={'backgroundColor': BG_COLOR, 'padding': '30px', 'fontFamily': 'Helvetica, sans-serif'}, children=[

    html.H1("💰 Crypto Dashboard", style={'textAlign': 'center', 'color': TEXT_COLOR}),

    html.Div([
        dcc.Dropdown(
            id='coin-input',
            options=[{'label': label, 'value': value} for label, value in [
                ('Bitcoin (BTC)', 'bitcoin'), ('Ethereum (ETH)', 'ethereum'),
                ('Solana (SOL)', 'solana'), ('Cardano (ADA)', 'cardano'),
                ('Dogecoin (DOGE)', 'dogecoin'), ('Avalanche (AVAX)', 'avalanche'),
                ('Polkadot (DOT)', 'polkadot'), ('Chainlink (LINK)', 'chainlink'),
                ('Shiba Inu (SHIB)', 'shiba-inu'), ('Toncoin (TON)', 'ton'),
            ]],
            value='bitcoin',
            placeholder='Escolha uma cripto...',
            style={'width': '300px', 'backgroundColor': CARD_COLOR, 'color': TEXT_COLOR}
        ),
        dcc.Dropdown(
            id='days-dropdown',
            options=[{'label': f'{d} Dias', 'value': str(d)} for d in [7, 30, 90]],
            value='30',
            style={'width': '150px', 'marginLeft': '20px', 'backgroundColor': CARD_COLOR, 'color': TEXT_COLOR}
        )
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'marginBottom': '30px'}),

    dcc.Loading(
        type='circle',
        color=ACCENT_COLOR,
        children=[
            html.Div(id='kpi-cards', style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px', 'marginBottom': '40px'}),
            dcc.Graph(id='price-chart')
        ]
    ),

    html.H2("📊 Comparação de Criptos", style={'color': ACCENT_COLOR, 'marginTop': '60px'}),

    html.Div([
        dcc.Dropdown(id='coin-compare-1',
                     options=[{'label': l, 'value': v} for l, v in [
                         ('Bitcoin (BTC)', 'bitcoin'), ('Ethereum (ETH)', 'ethereum'),
                         ('Solana (SOL)', 'solana'), ('Cardano (ADA)', 'cardano'),
                         ('Dogecoin (DOGE)', 'dogecoin'), ('Avalanche (AVAX)', 'avalanche'),
                         ('Polkadot (DOT)', 'polkadot'), ('Chainlink (LINK)', 'chainlink'),
                         ('Shiba Inu (SHIB)', 'shiba-inu'), ('Toncoin (TON)', 'ton')
                     ]],
                     value='bitcoin',
                     placeholder="Cripto 1",
                     style={'width': '250px', 'backgroundColor': CARD_COLOR, 'color': TEXT_COLOR}),
        dcc.Dropdown(id='coin-compare-2',
                     options=[{'label': l, 'value': v} for l, v in [
                         ('Bitcoin (BTC)', 'bitcoin'), ('Ethereum (ETH)', 'ethereum'),
                         ('Solana (SOL)', 'solana'), ('Cardano (ADA)', 'cardano'),
                         ('Dogecoin (DOGE)', 'dogecoin'), ('Avalanche (AVAX)', 'avalanche'),
                         ('Polkadot (DOT)', 'polkadot'), ('Chainlink (LINK)', 'chainlink'),
                         ('Shiba Inu (SHIB)', 'shiba-inu'), ('Toncoin (TON)', 'ton')
                     ]],
                     value='ethereum',
                     placeholder="Cripto 2",
                     style={'width': '250px', 'marginLeft': '20px', 'backgroundColor': CARD_COLOR, 'color': TEXT_COLOR}),
        dcc.Dropdown(id='compare-days',
                     options=[{'label': f'{d} dias', 'value': str(d)} for d in [7, 30, 90]],
                     value='30',
                     style={'width': '150px', 'marginLeft': '20px', 'backgroundColor': CARD_COLOR, 'color': TEXT_COLOR})
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'marginBottom': '20px'}),

    dcc.Graph(id='compare-chart'),

    html.H2("📈 Top Movers", style={'color': ACCENT_COLOR, 'marginTop': '60px'}),

    dcc.Dropdown(
        id="mover-period",
        options=[{"label": "Últimos 7 dias", "value": "7"}, {"label": "Últimos 30 dias", "value": "30"}],
        value="7",
        style={'width': '200px', 'marginBottom': '20px', 'backgroundColor': CARD_COLOR, 'color': TEXT_COLOR}
    ),

    html.Div(id="top-movers", style={'display': 'flex', 'gap': '40px', 'flexWrap': 'wrap'})
])

# ----- Callbacks -----

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
        current_price = info['market_data']['current_price']['usd']
        market_cap    = info['market_data']['market_cap']['usd']
        change_24h    = info['market_data']['price_change_percentage_24h']
        supply        = info['market_data']['circulating_supply']
        dates         = [datetime.fromtimestamp(ts/1000) for ts in timestamps]

        def kpi(label, value, color=TEXT_COLOR):
            return html.Div([
                html.Div(label, style={'color': ACCENT_COLOR}),
                html.Div(value, style={'fontSize': '20px', 'fontWeight': 'bold', 'color': color})
            ], style={'padding': '15px', 'backgroundColor': CARD_COLOR, 'borderRadius': '6px', 'flex': '1', 'textAlign': 'center', 'minWidth': '200px'})

        kpis = [
            kpi("Current Price",       f"${current_price:,.2f}"),
            kpi("Market Cap",          f"${market_cap/1e9:.2f} B"),
            kpi("24h Change",          f"{change_24h:+.2f}%", "#16c784" if change_24h >= 0 else ERROR_COLOR),
            kpi("Circulating Supply",  f"{supply:,.0f}")
        ]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=prices, mode='lines', line=dict(color=ACCENT_COLOR)))
        fig.update_layout(
            plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR,
            font=dict(color=TEXT_COLOR), margin=dict(l=40, r=40, t=40, b=20),
            height=600, xaxis_title="Date", yaxis_title="Price (USD)"
        )
        return fig, kpis

    except Exception as e:
        return go.Figure(layout=dict(title="Erro ao carregar gráfico")), [
            html.Div(f"Erro: {str(e)}", style={'color': ERROR_COLOR})
        ]

@app.callback(
    Output('compare-chart', 'figure'),
    Input('coin-compare-1', 'value'),
    Input('coin-compare-2', 'value'),
    Input('compare-days', 'value')
)
def update_compare_chart(coin1, coin2, days):
    try:
        ts1, px1 = get_coin_data(coin1, days)
        ts2, px2 = get_coin_data(coin2, days)
        if not px1 or not px2:
            return go.Figure(layout=dict(title="Dados insuficientes"))

        base1 = px1[0] or 1
        base2 = px2[0] or 1
        pct1 = [(p / base1 - 1) * 100 for p in px1]
        pct2 = [(p / base2 - 1) * 100 for p in px2]
        dates1 = [datetime.fromtimestamp(ts / 1000) for ts in ts1]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates1, y=pct1, mode='lines', name=coin1.upper(), line=dict(color=ACCENT_COLOR)))
        fig.add_trace(go.Scatter(x=dates1, y=pct2, mode='lines', name=coin2.upper(), line=dict(color="#16c784")))
        fig.update_layout(
            plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR,
            font=dict(color=TEXT_COLOR), margin=dict(l=40, r=40, t=40, b=20),
            height=500, xaxis_title="Data", yaxis_title="Variação (%) desde o início"
        )
        return fig
    except Exception as e:
        print("Erro na comparação:", e)
        return go.Figure(layout=dict(title="Erro na comparação"))

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
                    html.Td(f"{i+1}.", style={'padding': '6px 10px', 'borderBottom': '1px solid #2c313a'}),
                    html.Td(coin["name"], style={'padding': '6px 10px', 'borderBottom': '1px solid #2c313a'}),
                    html.Td(f"{pct:.2f}%", style={'color': color, 'padding': '6px 10px', 'textAlign': 'right', 'borderBottom': '1px solid #2c313a'})
                ]))
            return html.Div([
                html.H4(title, style={'color': color, 'marginBottom': '10px'}),
                html.Table(rows, style={'color': TEXT_COLOR, 'backgroundColor': CARD_COLOR, 'borderCollapse': 'collapse',
                                        'width': '100%', 'border': f'1px solid {ACCENT_COLOR}', 'borderRadius': '5px'})
            ], style={'flex': '1', 'minWidth': '300px'})

        return [
            make_table("📈 Gainers", gainers, "#16c784"),
            make_table("📉 Losers",  losers, ERROR_COLOR)
        ]

    except Exception as e:
        return [html.Div(f"Erro: {str(e)}", style={'color': ERROR_COLOR})]

# ----- Run -----

if __name__ == '__main__':
    print("🚀 Iniciando o dashboard...")
    app.run(debug=True)
