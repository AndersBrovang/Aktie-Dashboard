import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Aktie EDA", layout="wide")
st.title("Aktie-EDA Dashboard", anchor=False)

st.sidebar.header("Indstillinger")
aktie_symbol = st.sidebar.text_input("Aktie:", "NOVO-B.CO")
periode = st.sidebar.selectbox("Tidsperiode:", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)

@st.cache_data
def hent_og_bearbejd_data(symbol, period):
    aktie = yf.Ticker(symbol)
    df = aktie.history(period=period)
    
    if df.empty:
        return df
        
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['Dagligt_Afkast_%'] = df['Close'].pct_change() * 100
    
    return df.reset_index()

data = hent_og_bearbejd_data(aktie_symbol, periode)

if not data.empty:
    st.subheader(f"Overblik for {aktie_symbol.upper()}", anchor=False)
    nyeste_pris = data['Close'].iloc[-1]
    gaarsdagens_pris = data['Close'].iloc[-2]
    pct_aendring = ((nyeste_pris - gaarsdagens_pris) / gaarsdagens_pris) * 100
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Nuværende Pris", f"{nyeste_pris:.2f}", f"{pct_aendring:.2f}%")
    col2.metric("Højeste i perioden", f"{data['High'].max():.2f}")
    col3.metric("Gns. Handelsvolumen", f"{int(data['Volume'].mean()):,}")
    
    st.divider()

    tab1, tab2, tab3 = st.tabs(["Teknisk Analyse", "Volatilitet (Risiko)", "Rå Data & Download"])
    
    with tab1:
        fig_pris = go.Figure()

        fig_pris.add_trace(go.Candlestick(x=data['Date'],
                open=data['Open'], high=data['High'],
                low=data['Low'], close=data['Close'], name='Pris'))
        
        fig_pris.add_trace(go.Scatter(x=data['Date'], y=data['SMA_20'], mode='lines', name='20-dages gns.', line=dict(color='orange')))
        
        fig_pris.update_layout(height=500, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_pris, use_container_width=True)

    with tab2:
        fig_hist = px.histogram(data, x='Dagligt_Afkast_%', nbins=50, color_discrete_sequence=['#00b4d8'])
        fig_hist.add_vline(x=0, line_dash="dash", line_color="black") 
        st.plotly_chart(fig_hist, use_container_width=True)

    with tab3:
        st.dataframe(data)
        
        csv = data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data som CSV",
            data=csv,
            file_name=f'{aktie_symbol}_data.csv',
            mime='text/csv',
        )

else:
    st.error("Kunne ikke finde data. Tjek at symbolet er korrekt.")