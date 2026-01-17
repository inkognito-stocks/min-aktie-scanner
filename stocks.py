import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import feedparser   # För att hämta nyheter
import urllib.parse # För att skapa sök-länkar
import re           # För regex-matchning i nyhetsfiltrering

# --- FUNKTIONER ---

# 1. Räkna ut RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/window, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/window, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 2. Hämta nyheter (Google News RSS) - DIN NYA SMARTA FUNKTION
def fetch_company_news(company_name, ticker=None):
    all_entries = []
    
    # Skapa specifika söktermer med exakta matchningar
    search_terms = []
    
    if "Advenica" in company_name:
        search_terms = ['"Advenica"', 'ADVE.ST', '"ADVE.ST"']
    elif "Mogotes" in company_name or "Mogotes Metals" in company_name:
        search_terms = ['"Mogotes Metals"', 'MOG.V', '"MOG.V"']
    else:
        search_terms = [f'"{company_name}"']
        if ticker:
            search_terms.append(ticker)
            search_terms.append(f'"{ticker}"')
    
    relevance_terms = []
    company_lower = company_name.lower()
    if "advenica" in company_lower:
        relevance_terms = ["advenica", "adve.st", "adve.st"]
    elif "mogotes" in company_lower:
        relevance_terms = ["mogotes", "mog.v"]
    
    locales = [
        ("sv", "SE", "SE:sv"),  # Svenska
        ("en", "CA", "CA:en"),  # Kanadensisk engelska
        ("en", "US", "US:en"),  # Amerikansk engelska
    ]
    
    for term in search_terms:
        query = urllib.parse.quote(term)
        for hl, gl, ceid in locales:
            try:
                rss_url = f"https://news.google.com/rss/search?q={query}&hl={hl}&gl={gl}&ceid={ceid}"
                feed = feedparser.parse(rss_url)
                if feed.entries:
                    all_entries.extend(feed.entries)
            except Exception as e:
                continue
    
    filtered_entries = []
    for entry in all_entries:
        title = entry.get('title', '').lower()
        summary = entry.get('summary', '').lower()
        text_to_check = title + ' ' + summary
        
        is_relevant = False
        if relevance_terms:
            for term in relevance_terms:
                term_lower = term.lower()
                if term_lower == "advenica":
                    if re.search(r'\badvenica\b', text_to_check):
                        is_relevant = True
                        break
                elif "." in term_lower:
                    if term_lower in text_to_check:
                        is_relevant = True
                        break
                else:
                    if re.search(r'\b' + re.escape(term_lower) + r'\b', text_to_check):
                        is_relevant = True
                        break
        else:
            is_relevant = True
        
        if is_relevant:
            filtered_entries.append(entry)
    
    seen = set()
    unique_entries = []
    for entry in filtered_entries:
        key = (entry.get('title', ''), entry.get('link', ''))
        if key not in seen and key[0]:
            seen.add(key)
            unique_entries.append(entry)
    
    try:
        unique_entries.sort(key=lambda x: x.get('published_parsed', (0,)), reverse=True)
    except:
        pass
    
    return unique_entries[:10]

# --- IMPORT AV LISTOR (UPPDATERAD) ---
try:
    # Nu importerar vi hela dictionaryn 'ticker_lists' istället för separata listor
    from scanner_tickers import ticker_lists
except ImportError:
    st.error("Hittade inte filen 'scanner_tickers.py'. Se till att den ligger i samma mapp.")
    ticker_lists = {}

# Sidinställningar
st.set_page_config(layout="wide", page_title="Aktie Dashboard")

# --- SIDOMENY ---
st.sidebar.title("Navigering")
page = st.sidebar.radio("Gå till:", ["Mina Innehav", "Market Scanner", "Nyheter"])

# ==========================================
# SIDA 1: MINA INNEHAV
# ==========================================
if page == "Mina Innehav":
    st.title("Mina Innehav: Advenica & Mogotes")

    TICKERS = {
        "Advenica (ADVE.ST)": "ADVE.ST",
        "Mogotes Metals (MOG.V)": "MOG.V"
    }

    # Datuminställningar
    date_mode = st.radio("Välj tidsintervall:", ["Snabbknappar", "Anpassat datumintervall"], horizontal=True)

    if 'selected_period' not in st.session_state:
        st.session_state.selected_period = "12mo"

    if date_mode == "Snabbknappar":
        period_options = {"1 mån": "1mo", "3 månader": "3mo", "6 månader": "6mo", "12 månader": "12mo", "3 år": "3y", "5 år": "5y"}
        
        default_index = 0
        current_label = None
        for idx, (label, value) in enumerate(period_options.items()):
            if value == st.session_state.selected_period:
                default_index = idx
                current_label = label
                break
        
        if current_label is None:
            current_label = list(period_options.keys())[0]
            default_index = 0
        
        selected_label = st.selectbox("Välj tidsperiod:", options=list(period_options.keys()), index=default_index, key="period_selectbox")
        st.session_state.selected_period = period_options[selected_label]
        period = st.session_state.selected_period
        start_date = None
        end_date = None
    else:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Startdatum", value=datetime.now() - timedelta(days=365), max_value=datetime.now().date())
        with col2:
            end_date = st.date_input("Slutdatum", value=datetime.now().date(), max_value=datetime.now().date())
        period = None

    chart_type = st.selectbox("Välj graftyp:", ["Linje", "Candlestick", "Area"], index=1)

    col1, col2 = st.columns(2)

    for i, (name, ticker) in enumerate(TICKERS.items()):
        current_col = col1 if i == 0 else col2

        with current_col:
            st.subheader(f"📈 {name}")

            try:
                if period:
                    if period == "3mo":
                        start = datetime.now() - timedelta(days=3*30)
                        data = yf.Ticker(ticker).history(start=start, end=datetime.now())
                    elif period == "3y":
                        start = datetime.now() - timedelta(days=3*365)
                        data = yf.Ticker(ticker).history(start=start, end=datetime.now())
                    else:
                        data = yf.Ticker(ticker).history(period=period)
                else:
                    data = yf.Ticker(ticker).history(start=start_date, end=end_date)
            except Exception as e:
                st.error(f"Fel: {e}")
                continue

            if data is None or data.empty:
                st.warning(f"Inga data för {ticker}")
                continue

            # RSI Beräkning
            rsi_value = None
            rsi_text = "Inväntar data..."
            rsi_display_color = '#000000'
            
            if len(data) >= 14:
                data['RSI'] = calculate_rsi(data)
                rsi_value = data['RSI'].iloc[-1]
                if rsi_value < 30:
                    rsi_text = "🟢 KÖPLÄGE (Översåld)"
                    rsi_display_color = '#00aa00'
                elif rsi_value > 70:
                    rsi_text = "🔴 VARNING (Överköpt)"
                    rsi_display_color = '#ff0000'
                else:
                    rsi_text = "⚪ NEUTRAL"
                    rsi_display_color = '#000000'

            # Grafer
            if chart_type == "Linje":
                st.line_chart(data['Close'], width='stretch')
            elif chart_type == "Candlestick":
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Pris'), row=1, col=1)
                colors = ['red' if data['Close'].iloc[i] < data['Open'].iloc[i] else 'green' for i in range(len(data))]
                fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volym', marker_color=colors), row=2, col=1)
                fig.update_layout(height=600, showlegend=False, xaxis_rangeslider_visible=False, template='plotly_white', margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig, use_container_width=True)
            elif chart_type == "Area":
                st.area_chart(data['Close'], width='stretch')

            if chart_type != "Candlestick":
                st.bar_chart(data['Volume'], width='stretch')

            # Statistik
            last_close = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2] if len(data) > 1 else last_close
            pct_change = ((last_close - prev_close) / prev_close) * 100
            
            latest_volume = data['Volume'].iloc[-1]
            prev_volume = data['Volume'].iloc[-2] if len(data) > 1 else latest_volume
            currency = 'SEK' if '.ST' in ticker else 'CAD'
            latest_volume_value = latest_volume * last_close
            prev_volume_value = prev_volume * prev_close if len(data) > 1 else latest_volume_value
            
            m_col1, m_col2 = st.columns(2)
            st.markdown("""<style>div[data-testid='stMetricValue'] { margin-top: -15px !important; } </style>""", unsafe_allow_html=True)
            
            with m_col1:
                st.markdown("<h3 style='font-weight: bold; font-size: 1.2em; margin: 0;'>Pris & Utveckling</h3>", unsafe_allow_html=True)
                if pct_change > 0:
                    price_color, delta_symbol = '#00aa00', '↑'
                elif pct_change < 0:
                    price_color, delta_symbol = '#ff0000', '↓'
                else:
                    price_color, delta_symbol = '#000000', '→'
                
                st.markdown(f"<div style='font-size: 2rem; font-weight: 600; color: {price_color}; margin-top: -15px;'>{last_close:.2f} {currency}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size: 0.875rem; color: {price_color}; font-weight: 500;'>{delta_symbol} {abs(pct_change):.2f} %</div>", unsafe_allow_html=True)
            
            with m_col2:
                st.markdown("<h3 style='font-weight: bold; font-size: 1.2em; margin: 0;'>RSI Indikator</h3>", unsafe_allow_html=True)
                if rsi_value:
                    st.markdown(f"<div style='font-size: 2rem; font-weight: 600; color: {rsi_display_color}; margin-top: -15px;'>{rsi_value:.1f}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size: 0.875rem; color: {rsi_display_color}; font-weight: 500;'>{rsi_text}</div>", unsafe_allow_html=True)
                else:
                    st.write("N/A")
            
            # Volymjämförelse
            if len(data) > 1:
                volume_change = latest_volume - prev_volume
                volume_change_pct = ((latest_volume - prev_volume) / prev_volume * 100) if prev_volume > 0 else 0
                if volume_change > 0:
                    st.markdown(f"<span style='color: #00aa00; font-weight: bold; font-size: 1.4em;'>Volym idag: {latest_volume:,.0f} st ({latest_volume_value:,.0f} {currency})</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color: #00aa00; font-size: 1.3em;'>Gårdagens volym: {prev_volume:,.0f} st | ↑ {volume_change_pct:.1f}%</span>", unsafe_allow_html=True)
                elif volume_change < 0:
                    st.markdown(f"<span style='color: #ff0000; font-weight: bold; font-size: 1.4em;'>Volym idag: {latest_volume:,.0f} st ({latest_volume_value:,.0f} {currency})</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color: #ff0000; font-size: 1.3em;'>Gårdagens volym: {prev_volume:,.0f} st | ↓ {abs(volume_change_pct):.1f}%</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color: #000000; font-weight: bold; font-size: 1.4em;'>Volym idag: {latest_volume:,.0f} st</span>", unsafe_allow_html=True)
            
            st.divider()

# ==========================================
# SIDA 2: MARKET SCANNER (UPPDATERAD MED VAL AV LISTOR)
# ==========================================
elif page == "Market Scanner":
    st.title("🔎 Market Scanner")
    
    # 1. Välj strategi
    scan_mode = st.radio(
        "Välj vad du vill leta efter:",
        ["🚀 Stora Rörelser", "🔊 Volym-Raketer", "⚠️ RSI-Signaler"],
        horizontal=True
    )

    # 2. Välj Marknader & Listor (Dynamiskt baserat på scanner_tickers.py)
    st.subheader("Välj listor att scanna")
    
    # Förbered lista för Multiselect-menyn
    available_lists = []
    list_map = {} # Hjälper oss hitta rätt tickers när man valt ett namn

    # Loopa igenom din dictionary (Sverige, Kanada...)
    for market, sublists in ticker_lists.items():
        for list_name, tickers in sublists.items():
            full_name = f"{market} - {list_name}" # T.ex. "Sverige 🇸🇪 - Large Cap"
            available_lists.append(full_name)
            list_map[full_name] = tickers

    # Visa menyn (Allt valt som standard)
    selected_lists = st.multiselect("Välj marknader:", options=available_lists, default=available_lists)

    # Förklaringstext
    if scan_mode == "🚀 Stora Rörelser":
        st.info("Visar aktier som gått upp eller ner mer än **3%** idag.")
    elif scan_mode == "🔊 Volym-Raketer":
        st.info("Visar aktier som handlas med **dubbelt så hög volym** som normalt (2.0x).")
    elif scan_mode == "⚠️ RSI-Signaler":
        st.info("Visar aktier som är **Översålda (RSI < 30)** eller **Överköpta (RSI > 70)**.")

    if st.button("Starta Scanning 🕵️‍♂️"):
        # 3. Samla ihop alla tickers från de listor du valt
        all_tickers = []
        for selection in selected_lists:
            if selection in list_map:
                all_tickers.extend(list_map[selection])
        
        # Ta bort dubbletter (om någon aktie skulle finnas på flera ställen)
        all_tickers = list(set(all_tickers))

        if not all_tickers:
            st.error("Du måste välja minst en lista ovan!")
            st.stop()
        
        # 4. Hämta data
        with st.spinner(f"Analyserar {len(all_tickers)} aktier från valda listor..."):
            try:
                batch_data = yf.download(all_tickers, period="1mo", group_by='ticker', progress=False)
            except Exception as e:
                st.error(f"Fel vid hämtning: {e}")
                st.stop()

        results = []
        for ticker in all_tickers:
            try:
                if len(all_tickers) > 1:
                    df = batch_data[ticker]
                else:
                    df = batch_data
                
                # Behöver minst 14 dagar för RSI
                if len(df) < 14: continue

                # Hämta värden
                close = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2]
                change_pct = ((close - prev_close) / prev_close) * 100
                
                # Volymanalys
                vol_today = df['Volume'].iloc[-1]
                vol_avg = df['Volume'].mean()
                r_vol = vol_today / vol_avg if vol_avg > 0 else 0
                
                # RSI Analys
                df['RSI'] = calculate_rsi(df)
                rsi = df['RSI'].iloc[-1]

                news_link = f"https://www.google.com/search?q={ticker}+stock+news"

                row = {
                    "Ticker": ticker,
                    "Pris": close,
                    "Utv %": round(change_pct, 2),
                    "RVol (x)": round(r_vol, 1),
                    "RSI": round(rsi, 1),
                    "Länk": news_link
                }

                # --- FILTRERING ---
                should_add = False
                if scan_mode == "🚀 Stora Rörelser":
                    if abs(change_pct) > 3.0: should_add = True
                elif scan_mode == "🔊 Volym-Raketer":
                    if r_vol > 2.0: should_add = True
                elif scan_mode == "⚠️ RSI-Signaler":
                    if rsi < 30 or rsi > 70: should_add = True

                if should_add:
                    results.append(row)

            except Exception: continue

        # --- VISA RESULTAT ---
        if results:
            df_results = pd.DataFrame(results)
            
            if scan_mode == "🚀 Stora Rörelser":
                df_results = df_results.sort_values("Utv %", ascending=False)
                st.dataframe(df_results, column_config={"Länk": st.column_config.LinkColumn("Nyheter")}, hide_index=True, width='stretch')
                
            elif scan_mode == "🔊 Volym-Raketer":
                df_results = df_results.sort_values("RVol (x)", ascending=False)
                st.dataframe(df_results, column_config={"Länk": st.column_config.LinkColumn("Nyheter")}, hide_index=True, width='stretch')
                
            elif scan_mode == "⚠️ RSI-Signaler":
                df_results = df_results.sort_values("RSI", ascending=True)
                
                # Färgläggning för RSI
                def color_rsi(val):
                    if val < 30: return 'background-color: #d4edda; color: green'
                    if val > 70: return 'background-color: #f8d7da; color: red'
                    return ''

                st.dataframe(
                    df_results.style.map(color_rsi, subset=['RSI']).format({"Pris": "{:.2f}", "Utv %": "{:.2f}%", "RSI": "{:.1f}"}),
                    column_config={"Länk": st.column_config.LinkColumn("Nyheter")},
                    hide_index=True,
                    width='stretch'
                )
        else:
            st.warning("Inga aktier matchade dina kriterier just nu.")

# ==========================================
# SIDA 3: NYHETER
# ==========================================
elif page == "Nyheter":
    st.title("📰 Nyheter: Advenica & Mogotes")
    st.markdown("Senaste nyheterna om dina bolag från Google News.")

    my_companies = {
        "Advenica": "ADVE.ST",
        "Mogotes Metals": "MOG.V"
    }

    col1, col2 = st.columns(2)

    for i, (company, ticker) in enumerate(my_companies.items()):
        current_col = col1 if i % 2 == 0 else col2
        
        with current_col:
            st.header(f"{company}")
            with st.spinner(f"Söker nyheter om {company}..."):
                news_items = fetch_company_news(company, ticker)
            
            if news_items:
                for item in news_items:
                    with st.expander(item.title):
                        if 'published' in item: st.caption(f"📅 {item.published}")
                        if 'link' in item: st.markdown(f"👉 [Läs hela artikeln]({item.link})")
            else:
                st.info(f"Inga nyliga nyheter hittades för {company}.")
            st.divider()