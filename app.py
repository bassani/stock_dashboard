import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid


def build_sidebar():
    st.image("images/logo-250-100-transparente.png")
    ticker_list = pd.read_csv("tickers_ibra.csv", index_col=0)
    tickers = st.multiselect(label="Selecione as Empresas", options=ticker_list, placeholder='Códigos', default=['TAEE11', 'ROMI3', 'WEGE3', 'CMIG4', 'BRSR6', 'ISAE4', 'BBDC3', 'CSMG3', 'POMO4', 'BRAP4', 'CMIN3', 'MRFG3', 'CSNA3', 'PETR4', 'LEVE3', 'BBAS3', 'KLBN11'])
    tickers = [t+".SA" for t in tickers]
    start_date = st.date_input("De", format="DD/MM/YYYY", value=datetime(2025,4,2))
    end_date = st.date_input("Até", format="DD/MM/YYYY", value="today")

    if tickers:
        prices = yf.download(tickers, start=start_date, end=end_date)["Close"]
        if len(tickers) == 1:
            #prices = prices.to_frame()
            prices.columns = [tickers[0].rstrip(".SA")]
                    
        prices.columns = prices.columns.str.rstrip(".SA")
        prices['IBOV'] = yf.download("^BVSP", start=start_date, end=end_date)["Close"]
        return tickers, prices
    return None, None

def build_main(tickers, prices):
    weights = np.ones(len(tickers))/len(tickers)
    prices['portfolio'] = prices.drop("IBOV", axis=1) @ weights
    norm_prices = 100 * prices / prices.iloc[0]
    returns = prices.pct_change()[1:]
    vols = returns.std()*np.sqrt(252)
    rets = (norm_prices.iloc[-1] - 100) / 100

    mygrid = grid(5 ,5 ,5 ,5 ,5 , 5, vertical_align="top")
    for t in prices.columns:
        c = mygrid.container(border=True)
        c.subheader(t, divider="red")
        colA, colB, colC = c.columns(3)
        if t == "portfolio":
            colA.image("images/pie-chart-dollar-svgrepo-com.svg")
        elif t == "IBOV":
            colA.image("images/pie-chart-svgrepo-com.svg")
        else:
            colA.image(f'https://raw.githubusercontent.com/thefintz/icones-b3/main/icones/{t}.png', width=85)
        colB.metric(label="retorno", value=f"{rets[t]:.0%}")
        colC.metric(label="volatilidade", value=f"{vols[t]:.0%}")
        style_metric_cards(background_color='rgba(255,255,255,0)')
    
    col1, col2 = st.columns(2, gap='large')
    with col1:
        st.subheader("Desempenho Relativo")
        fig_line = px.line(norm_prices, labels={'value': '%', 'variable': 'Ativo'},
                           hover_data={'value': ':.2f'},
                           )
        fig_line.update_traces(mode="markers+lines", hovertemplate="%{y:.2f}%")
        fig_line.update_layout(height=600, hovermode="x unified")
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.subheader("Risco-Retorno")
        fig = px.scatter(
            x=vols,
            y=rets,
            text=vols.index,
            color=rets/vols,
            color_continuous_scale=px.colors.sequential.Bluered_r
        )
        fig.update_traces(
            textfont_color='white', 
            marker=dict(size=45),
            textfont_size=10,                  
        )
        fig.layout.yaxis.title = 'Retorno Total'
        fig.layout.xaxis.title = 'Volatilidade (anualizada)'
        fig.layout.height = 600
        fig.layout.xaxis.tickformat = ".0%"
        fig.layout.yaxis.tickformat = ".0%"        
        fig.layout.coloraxis.colorbar.title = 'Sharpe'
        st.plotly_chart(fig, use_container_width=True)

        
st.set_page_config(layout="wide")

with st.sidebar:
    tickers, prices = build_sidebar()

st.title('Python para Investidores')
if tickers:
    build_main(tickers, prices)