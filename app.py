import streamlit as st
import pandas as pd
from datetime import datetime

# --- NASTAVENÍ ---
st.set_page_config(page_title="StepQueen 🏃‍♀️", page_icon="👑")

# Stylizace "vibe" aplikace
st.markdown("""
    <style>
    .main { background-color: #fff5f8; }
    .stButton>button { background-color: #ff4b4b; color: white; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA ---
# (Poznámka: Pro trvalá data na GitHubu je nejlepší použít st.connection("gsheets"))
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["datum", "jmeno", "kroky"])

# --- UI ---
st.title("🏃‍♀️ StepQueen Challenge")
st.write("Souboj mezi **Lili**, **Lenkou** a **Monkou**!")

# Horní statistika - Kdo kraluje tento měsíc
current_month = datetime.now().strftime("%m/%Y")
df = st.session_state.data

if not df.empty:
    # Převod datumu pro filtrování
    df['datum'] = pd.to_datetime(df['datum'])
    df_current = df[df['datum'].dt.strftime("%m/%Y") == current_month]
    
    if not df_current.empty:
        stats = df_current.groupby("jmeno")["kroky"].sum().reset_index()
        winner = stats.loc[stats['kroky'].idxmax()]
        st.success(f"🏆 Aktuální královna měsíce: **{winner['jmeno']}** ({int(winner['kroky']):,} kroků)")
        
        # Graf
        st.bar_chart(data=stats, x="jmeno", y="kroky")
    else:
        st.info("Tento měsíc zatím žádné kroky. Kdo začne?")
else:
    st.info("Zatím žádná data. Šup ven na procházku!")

# --- FORMULÁŘ PRO ZÁPIS ---
st.divider()
with st.expander("➕ Zapsat dnešní kroky", expanded=True):
    with st.form("add_steps"):
        col1, col2 = st.columns(2)
        with col1:
            jmeno_volba = st.selectbox("Kdo jsi?", ["Lili", "Lenka", "Monka"])
        with col2:
            datum_volba = st.date_input("Den", datetime.now())
        
        kroky_cislo = st.number_input("Počet kroků", min_value=0, step=100, value=10000)
        submitted = st.form_submit_button("Uložit do Google Tabulky ✨")
        
        if submitted:
            # 1. Vytvoření nového řádku
            new_entry = pd.DataFrame({
                "datum": [datum_volba.strftime("%Y-%m-%d")],
                "jmeno": [jmeno_volba],
                "kroky": [kroky_cislo]
            })
            
            # 2. Načtení aktuálních dat, aby se nepřemazala
            current_df = conn.read(ttl="0s")
            
            # 3. Spojení starých dat s novým záznamem
            final_df = pd.concat([current_df, new_entry], ignore_index=True)
            
            # 4. Odeslání do Google Sheets
            conn.update(data=final_df)
            
            # 5. Úklid a radost
            st.cache_data.clear()
            st.balloons()
            st.success("Kroky úspěšně propsány do Google Tabulky! 🚀")
            st.rerun()

# --- HISTORIE ---
if st.checkbox("Zobrazit historii záznamů"):
    st.dataframe(st.session_state.data.sort_values(by="datum", ascending=False), use_container_width=True)
