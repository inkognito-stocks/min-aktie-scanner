import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import feedparser   # NYTT: För att hämta nyheter
import urllib.parse # NYTT: För att skapa sök-länkar

# --- FUNKTIONER ---

# 1. Räkna ut RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/window, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/window, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 2. Hämta nyheter (Google News RSS) - NY FUNKTION
def fetch_company_news(company_name):
    # Skapa en säker sökterm
    query = urllib.parse.quote(company_name)
    # URL till Google News RSS sökning (Svenska nyheter)
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=sv&gl=SE&ceid=SE:sv"
    
    try:
        feed = feedparser.parse(rss_url)
        return feed.entries[:5]  # Hämta de 5 senaste nyheterna
    except Exception:
        return []

# Importera dina listor från den andra filen
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
# UPPDATERAT: La till "Nyheter" i menyn
page = st.sidebar.radio("Gå till:", ["Mina Innehav", "Market Scanner", "Nyheter"])

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

    # Initiera session state för vald period (12 månader som standard)
    if 'selected_period' not in st.session_state:
        st.session_state.selected_period = "12mo"

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

    # Välj graftyp för prisgrafen (Candlestick som standard)
    chart_type = st.selectbox(
        "Välj graftyp:",
        ["Linje", "Candlestick", "Area"],
        index=1,  # Candlestick som standard
        key="chart_type_selectbox"
    )

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

            # --- RSI BERÄKNING ---
            # Vi behöver minst 14 dagar för att räkna RSI korrekt
            rsi_value = None
            rsi_text = "Inväntar data..."
            rsi_color = "off"
            
            if len(data) >= 14:
                data['RSI'] = calculate_rsi(data)
                rsi_value = data['RSI'].iloc[-1]
                
                # Tolka RSI-värdet
                if rsi_value < 30:
                    rsi_text = "🟢 KÖPLÄGE (Översåld)"
                    rsi_delta_color = "normal" # Grön i Streamlit
                elif rsi_value > 70:
                    rsi_text = "🔴 VARNING (Överköpt)"
                    rsi_delta_color = "inverse" # Röd i Streamlit
                else:
                    rsi_text = "⚪ NEUTRAL"
                    rsi_delta_color = "off" # Grå

            # Prisgraf baserat på vald typ
            if chart_type == "Linje":
                st.line_chart(data['Close'], width='stretch')
            elif chart_type == "Candlestick":
                # Skapa candlestick-graf med Plotly
                fig = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.03,
                    row_heights=[0.7, 0.3],
                    subplot_titles=(f'{name} - Pris', 'Volym')
                )
                
                # Candlestick
                fig.add_trace(
                    go.Candlestick(
                        x=data.index,
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'],
                        name='Pris'
                    ),
                    row=1, col=1
                )
                
                # Volym
                colors = ['red' if data['Close'].iloc[i] < data['Open'].iloc[i] else 'green' 
                          for i in range(len(data))]
                fig.add_trace(
                    go.Bar(
                        x=data.index,
                        y=data['Volume'],
                        name='Volym',
                        marker_color=colors
                    ),
                    row=2, col=1
                )
                
                fig.update_layout(
                    height=600,
                    showlegend=False,
                    xaxis_rangeslider_visible=False,
                    template='plotly_white'
                )
                
                fig.update_xaxes(title_text="Datum", row=2, col=1)
                fig.update_yaxes(title_text="Pris", row=1, col=1)
                fig.update_yaxes(title_text="Volym", row=2, col=1)
                
                st.plotly_chart(fig, use_container_width=True)
            elif chart_type == "Area":
                st.area_chart(data['Close'], width='stretch')

            # Volymgraf med staplar (visas bara om inte candlestick används)
            if chart_type != "Candlestick":
                st.bar_chart(data['Volume'], width='stretch')

            # Statistik
            last_close = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2] if len(data) > 1 else last_close
            pct_change = ((last_close - prev_close) / prev_close) * 100

            latest_volume = data['Volume'].iloc[-1]
            prev_volume = data['Volume'].iloc[-2] if len(data) > 1 else latest_volume
            
            # Beräkna volymvärde (volym * pris)
            currency = 'SEK' if '.ST' in ticker else 'CAD'
            latest_volume_value = latest_volume * last_close
            prev_volume_value = prev_volume * prev_close if len(data) > 1 else latest_volume_value

            # Visa siffror i kolumner (Pris & RSI)
            m_col1, m_col2 = st.columns(2)
            
            # CSS för att minska avståndet mellan rubrik och metric
            st.markdown("""
                <style>
                div[data-testid='stMetricValue'] {
                    margin-top: -15px !important;
                }
                </style>
            """, unsafe_allow_html=True)
            
            with m_col1:
                st.markdown("<h3 style='font-weight: bold; font-size: 1.2em; margin-bottom: 0; margin-top: 0; padding-bottom: 0; line-height: 1.2;'>Pris & Utveckling</h3>", unsafe_allow_html=True)
                # Färgkoda kursen baserat på utveckling
                currency_symbol = 'SEK' if '.ST' in ticker else 'CAD'
                if pct_change > 0:
                    price_color = '#00aa00'  # Grön vid uppgång
                    delta_color = '#00aa00'
                    delta_symbol = '↑'
                elif pct_change < 0:
                    price_color = '#ff0000'  # Röd vid nedgång
                    delta_color = '#ff0000'
                    delta_symbol = '↓'
                else:
                    price_color = '#000000'  # Svart vid ingen förändring
                    delta_color = '#000000'
                    delta_symbol = '→'
                
                st.markdown(
                    f"<div style='font-size: 2rem; font-weight: 600; color: {price_color}; margin-top: -15px;'>{last_close:.2f} {currency_symbol}</div>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div style='font-size: 0.875rem; color: {delta_color}; font-weight: 500;'>{delta_symbol} {abs(pct_change):.2f} %</div>",
                    unsafe_allow_html=True
                )
            
            with m_col2:
                st.markdown("<h3 style='font-weight: bold; font-size: 1.2em; margin-bottom: 0; margin-top: 0; padding-bottom: 0; line-height: 1.2;'>RSI Indikator</h3>", unsafe_allow_html=True)
                if rsi_value:
                    # Färgkoda RSI-värdet baserat på nivå
                    if rsi_value < 30:
                        rsi_display_color = '#00aa00'  # Grön - översåld (köpläge)
                    elif rsi_value > 70:
                        rsi_display_color = '#ff0000'  # Röd - överköpt (varning)
                    else:
                        rsi_display_color = '#000000'  # Svart - neutral
                    
                    st.markdown(
                        f"<div style='font-size: 2rem; font-weight: 600; color: {rsi_display_color}; margin-top: -15px;'>{rsi_value:.1f}</div>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<div style='font-size: 0.875rem; color: {rsi_display_color}; font-weight: 500;'>{rsi_text}</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        "<div style='font-size: 2rem; font-weight: 600; color: #000000; margin-top: -15px;'>N/A</div>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        "<div style='font-size: 0.875rem; color: #000000; font-weight: 500;'>För lite data</div>",
                        unsafe_allow_html=True
                    )
            
            # Volymjämförelse med färgkodning
            if len(data) > 1:
                volume_change = latest_volume - prev_volume
                volume_change_pct = ((latest_volume - prev_volume) / prev_volume * 100) if prev_volume > 0 else 0
                
                # Färgkoda "Volym idag" baserat på jämförelse
                if volume_change > 0:
                    st.markdown(f"<span style='color: #00aa00; font-weight: bold; font-size: 1.4em;'>Volym idag: {latest_volume:,.0f} st ({latest_volume_value:,.0f} {currency})</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color: #00aa00; font-size: 1.3em;'>Gårdagens volym: {prev_volume:,.0f} st ({prev_volume_value:,.0f} {currency}) | <span style='font-weight: bold;'>↑ {volume_change_pct:.1f}%</span></span>", unsafe_allow_html=True)
                elif volume_change < 0:
                    st.markdown(f"<span style='color: #ff0000; font-weight: bold; font-size: 1.4em;'>Volym idag: {latest_volume:,.0f} st ({latest_volume_value:,.0f} {currency})</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color: #ff0000; font-size: 1.3em;'>Gårdagens volym: {prev_volume:,.0f} st ({prev_volume_value:,.0f} {currency}) | <span style='font-weight: bold;'>↓ {abs(volume_change_pct):.1f}%</span></span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color: #000000; font-weight: bold; font-size: 1.4em;'>Volym idag: {latest_volume:,.0f} st ({latest_volume_value:,.0f} {currency})</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color: #000000; font-size: 1.3em;'>Gårdagens volym: {prev_volume:,.0f} st ({prev_volume_value:,.0f} {currency}) | → 0%</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color: #000000; font-weight: bold; font-size: 1.4em;'>Volym idag: {latest_volume:,.0f} st ({latest_volume_value:,.0f} {currency})</span>", unsafe_allow_html=True)
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

# ==========================================
# SIDA 3: NYHETER (NY SIDA)
# ==========================================
elif page == "Nyheter":
    st.title("📰 Nyheter: Advenica & Mogotes")
    st.markdown("Senaste nyheterna om dina bolag från Google News.")

    # Lista på bolagen du vill bevaka
    my_companies = ["Advenica", "Mogotes Metals"]

    col1, col2 = st.columns(2)

    for i, company in enumerate(my_companies):
        # Välj kolumn
        current_col = col1 if i % 2 == 0 else col2
        
        with current_col:
            st.header(f"{company}")
            
            with st.spinner(f"Söker nyheter om {company}..."):
                news_items = fetch_company_news(company)
            
            if news_items:
                for item in news_items:
                    with st.expander(item.title):
                        # Visa datum om det finns
                        if 'published' in item:
                            st.caption(f"📅 {item.published}")
                        
                        # Länk till artikeln
                        st.markdown(f"👉 [Läs hela artikeln]({item.link})")
            else:
                st.info(f"Inga nyliga nyheter hittades för {company} just nu.")
            
            st.divider()