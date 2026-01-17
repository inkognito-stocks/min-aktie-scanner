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

    # Periodval - Snabbknappar eller anpassat datumintervall
    date_mode = st.radio(
        "Välj tidsintervall:",
        ["Snabbknappar", "Anpassat datumintervall"],
        horizontal=True
    )

    # Initiera session state för vald period
    if 'selected_period' not in st.session_state:
        st.session_state.selected_period = "1y"

    if date_mode == "Snabbknappar":
        # Rullgardin för olika perioder
        period_options = {
            "1 mån": "1mo",
            "3 månader": "3mo",
            "6 månader": "6mo",
            "12 månader": "12mo",
            "3 år": "3y",
            "5 år": "5y"
        }
        
        # Hitta valt label baserat på nuvarande period
        default_index = 0
        current_label = None
        for idx, (label, value) in enumerate(period_options.items()):
            if value == st.session_state.selected_period:
                default_index = idx
                current_label = label
                break
        
        # Om ingen matchning, använd första alternativet
        if current_label is None:
            current_label = list(period_options.keys())[0]
            default_index = 0
        
        selected_label = st.selectbox(
            "Välj tidsperiod:",
            options=list(period_options.keys()),
            index=default_index,
            key="period_selectbox"
        )
        
        st.session_state.selected_period = period_options[selected_label]
        period = st.session_state.selected_period
        start_date = None
        end_date = None
    else:
        # Anpassat datumintervall med kalender
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Startdatum",
                value=datetime.now() - timedelta(days=365),
                max_value=datetime.now().date()
            )
        with col2:
            end_date = st.date_input(
                "Slutdatum",
                value=datetime.now().date(),
                max_value=datetime.now().date()
            )
        
        if start_date >= end_date:
            st.error("Startdatum måste vara tidigare än slutdatum!")
            st.stop()
        
        period = None

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
                if period:
                    # Fördefinierade perioder - hantera 3 månader och 3 år separat
                    if period == "3mo":
                        start = datetime.now() - timedelta(days=3*30)
                        end = datetime.now()
                        data = yf.Ticker(ticker).history(start=start, end=end)
                    elif period == "3y":
                        start = datetime.now() - timedelta(days=3*365)
                        end = datetime.now()
                        data = yf.Ticker(ticker).history(start=start, end=end)
                    else:
                        data = yf.Ticker(ticker).history(period=period)
                else:
                    # Anpassat datumintervall
                    data = yf.Ticker(ticker).history(start=start_date, end=end_date)
            except Exception as e:
                st.error(f"Kunde inte hämta data för {ticker}: {str(e)}")
                continue

            if data is None or data.empty:
                st.warning(f"Inga data för {ticker}")
                continue

            # Prisgraf
            st.line_chart(data['Close'], width='stretch')

            # Volymgraf med staplar
            st.bar_chart(data['Volume'], width='stretch')

            # Statistik
            last_close = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2] if len(data) > 1 else last_close
            pct_change = ((last_close - prev_close) / prev_close) * 100

            latest_volume = data['Volume'].iloc[-1]
            prev_volume = data['Volume'].iloc[-2] if len(data) > 1 else latest_volume

            # Visa siffror
            st.metric(
                label="Pris & Utveckling",
                value=f"{last_close:.2f} {'SEK' if '.ST' in ticker else 'CAD'}",
                delta=f"{pct_change:.2f} %"
            )
            
            # Volymjämförelse med färgkodning
            if len(data) > 1:
                volume_change = latest_volume - prev_volume
                volume_change_pct = ((latest_volume - prev_volume) / prev_volume * 100) if prev_volume > 0 else 0
                
                # Färgkoda "Volym idag" baserat på jämförelse
                if volume_change > 0:
                    st.markdown(f"<span style='color: #00aa00; font-weight: bold; font-size: 1.4em;'>Volym idag: {latest_volume:,.0f} st</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color: #000000; font-size: 1.3em;'>Gårdagens volym: {prev_volume:,.0f} st | <span style='color: #00aa00; font-weight: bold;'>↑ {volume_change_pct:.1f}%</span></span>", unsafe_allow_html=True)
                elif volume_change < 0:
                    st.markdown(f"<span style='color: #ff0000; font-weight: bold; font-size: 1.4em;'>Volym idag: {latest_volume:,.0f} st</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color: #000000; font-size: 1.3em;'>Gårdagens volym: {prev_volume:,.0f} st | <span style='color: #ff0000; font-weight: bold;'>↓ {abs(volume_change_pct):.1f}%</span></span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color: #000000; font-weight: bold; font-size: 1.4em;'>Volym idag: {latest_volume:,.0f} st</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color: #000000; font-size: 1.3em;'>Gårdagens volym: {prev_volume:,.0f} st | → 0%</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color: #000000; font-weight: bold; font-size: 1.4em;'>Volym idag: {latest_volume:,.0f} st</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color: #000000; font-size: 1.3em;'>Gårdagens volym: N/A</span>", unsafe_allow_html=True)
            
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
                        hide_index=True,
                        width='stretch'
                    )
                else:
                    st.write("Inga aktier upp > 3% idag.")

            with col_loss:
                st.error(f"📉 Förlorare ({len(losers)} st)")
                if not losers.empty:
                    st.dataframe(
                        losers,
                        column_config={"Länk": st.column_config.LinkColumn("Nyheter")},
                        hide_index=True,
                        width='stretch'
                    )
                else:
                    st.write("Inga aktier ner > 3% idag.")
        else:
            st.warning("Hittade ingen data för listan.")
