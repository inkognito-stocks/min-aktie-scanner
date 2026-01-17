import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Importera dina listor från den andra filen
# (Om denna rad blir röd i Cursor, ignorera det så länge filen scanner_tickers.py finns i mappen)
try:
    from scanner_tickers import sweden_tickers, canada_tickers
except ImportError:
    st.error("Hittade inte filen 'scanner_tickers.py'. Se till att den ligger i samma mapp.")
    sweden_tickers = []
    canada_tickers = []

# Sidinställningar (Bredd)
st.set_page_config(layout="wide", page_title="Aktie Dashboard")

# --- SIDOMENY ---
st.sidebar.title("Navigering")
page = st.sidebar.radio("Gå till:", ["Mina Innehav", "Market Scanner"])

# ==========================================
# SIDA 1: MINA INNEHAV (Advenica & Mogotes)
# ==========================================
if page == "Mina Innehav":
    st.title("Mina Innehav: Advenica & Mogotes")

    # Ange de aktier vi vill spåra
    TICKERS = {
        "Advenica (ADVE.ST)": "ADVE.ST",
        "Mogotes Metals (MOG.V)": "MOG.V"
    }

    # Periodval
    col_per, _ = st.columns([1, 3])
    with col_per:
        period_val = st.selectbox(
            "Välj tidsperiod:",
            options=[("1 mån", "1mo"), ("6 månader", "6mo"), ("1 år", "1y"), ("5 år", "5y")],
            format_func=lambda v: v[0]
        )
    period = period_val[1]

    # Skapa kolumner för att visa bolagen bredvid varandra
    col1, col2 = st.columns(2)

    # Loopa igenom bolagen men placera dem i varsin kolumn
    for i, (name, ticker) in enumerate(TICKERS.items()):
        # Välj kolumn baserat på ordning (0 = vänster, 1 = höger)
        current_col = col1 if i == 0 else col2

        with current_col:
            st.subheader(f"📈 {name}")

            # Hämta data med felhantering
            try:
                data = yf.Ticker(ticker).history(period=period)
            except Exception as e:
                st.error(f"Kunde inte hämta data för {ticker}: {str(e)}")
                continue

            if data is None or data.empty:
                st.warning(f"Inga data för {ticker}")
                continue

            # Graf
            st.line_chart(data['Close'], use_container_width=True)

            # Statistik
            last_close = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2] if len(data) > 1 else last_close
            pct_change = ((last_close - prev_close) / prev_close) * 100

            latest_volume = data['Volume'].iloc[-1]

            # Visa siffror
            st.metric(
                label="Pris & Utveckling",
                value=f"{last_close:.2f} {'SEK' if '.ST' in ticker else 'CAD'}",
                delta=f"{pct_change:.2f} %"
            )
            st.caption(f"Volym idag: {latest_volume:,.0f} st")
            st.divider()

# ==========================================
# SIDA 2: MARKET SCANNER
# ==========================================
elif page == "Market Scanner":
    st.title("🔎 Market Scanner")
    st.markdown("Hittar aktier som rört sig mer än **3%** idag.")

    # Knapp för att starta scanningen
    if st.button("Starta Scanning (Detta tar några sekunder)"):

        # 1. Slå ihop listorna
        all_tickers = sweden_tickers + canada_tickers

        # 2. Hämta data i "Batch" (mycket snabbare)
        with st.spinner(f"Hämtar data för {len(all_tickers)} aktier..."):
            try:
                # Vi hämtar 5 dagars data för att kunna räkna ut snittvolym
                batch_data = yf.download(all_tickers, period="5d", group_by='ticker', progress=False)
            except Exception as e:
                st.error(f"Kunde inte hämta data: {e}")
                st.stop()

        # 3. Analysera datan
        results = []

        for ticker in all_tickers:
            try:
                # Hantera hur yfinance returnerar datan (ibland MultiIndex, ibland inte)
                if len(all_tickers) > 1:
                    df = batch_data[ticker]
                else:
                    df = batch_data

                # Måste ha minst 2 dagars data
                if len(df) < 2:
                    continue

                # Hämta värden
                close = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2]
                change_pct = ((close - prev_close) / prev_close) * 100

                # Volymanalys (Relativ Volym)
                vol_today = df['Volume'].iloc[-1]
                vol_avg = df['Volume'].mean()
                r_vol = vol_today / vol_avg if vol_avg > 0 else 0

                # Länk till nyheter (Google)
                news_link = f"https://www.google.com/search?q={ticker}+stock+news"

                results.append({
                    "Ticker": ticker,
                    "Pris": close,
                    "Utveckling (%)": round(change_pct, 2),
                    "RVol (xNormalt)": round(r_vol, 1),
                    "Länk": news_link
                })

            except KeyError:
                continue  # Hoppa över om data saknas för tickern

        # 4. Skapa DataFrame och filtrera
        if results:
            df_results = pd.DataFrame(results)

            # Filtrera Vinnare och Förlorare (Gräns 3%)
            winners = df_results[df_results["Utveckling (%)"] > 0.5].sort_values("Utveckling (%)", ascending=False)
            losers = df_results[df_results["Utveckling (%)"] < -0.5].sort_values("Utveckling (%)", ascending=True)

            # --- VISA RESULTAT ---
            col_win, col_loss = st.columns(2)

            with col_win:
                st.success(f"🚀 Vinnare ({len(winners)} st)")
                if not winners.empty:
                    st.dataframe(
                        winners,
                        column_config={"Länk": st.column_config.LinkColumn("Nyheter")},
                        hide_index=True
                    )
                else:
                    st.write("Inga aktier upp > 3% idag.")

            with col_loss:
                st.error(f"📉 Förlorare ({len(losers)} st)")
                if not losers.empty:
                    st.dataframe(
                        losers,
                        column_config={"Länk": st.column_config.LinkColumn("Nyheter")},
                        hide_index=True
                    )
                else:
                    st.write("Inga aktier ner > 3% idag.")
        else:
            st.warning("Hittade ingen data för listan.")
