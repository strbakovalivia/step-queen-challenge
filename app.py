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
            jmeno = st.selectbox("Kdo jsi?", ["Lili", "Lenka", "Monka"])
        with col2:
            datum = st.date_input("Den", datetime.now())
        
        kroky = st.number_input("Počet kroků", min_value=0, step=1000, value=10000)
        
        submitted = st.form_submit_button("Uložit do deníčku ✨")
        
        if submitted:
            new_row = pd.DataFrame({"datum": [pd.to_datetime(datum)], "jmeno": [jmeno], "kroky": [kroky]})
            st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
            st.balloons()
            st.rerun()

# --- HISTORIE ---
if st.checkbox("Zobrazit historii záznamů"):
    st.dataframe(st.session_state.data.sort_values(by="datum", ascending=False), use_container_width=True)
