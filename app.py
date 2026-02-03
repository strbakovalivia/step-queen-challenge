import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="StepQueen 🏃‍♀️", page_icon="👑")

st.title("🏃‍♀️ StepQueen Challenge")
st.write("Souboj mezi **Lili**, **Lenkou** a **Monkou**!")

# --- PROPOJENÍ S GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Funkce pro bezpečné načtení dat
def load_data():
    try:
        data = conn.read(ttl="0s")
        # Pokud je tabulka úplně prázdná, vytvoříme základní strukturu
        if data is None or data.empty:
            return pd.DataFrame(columns=["datum", "jmeno", "kroky"])
        return data
    except:
        return pd.DataFrame(columns=["datum", "jmeno", "kroky"])

df = load_data()

# --- VÝPOČET KRÁLOVNY ---
current_month = datetime.now().strftime("%m/%Y")

if not df.empty:
    # Převod na datetime pro jistotu
    df['datum'] = pd.to_datetime(df['datum'])
    df_current = df[df['datum'].dt.strftime("%m/%Y") == current_month]
    
    if not df_current.empty:
        stats = df_current.groupby("jmeno")["kroky"].sum().reset_index()
        winner = stats.loc[stats['kroky'].idxmax()]
        st.success(f"🏆 Aktuální královna měsíce: **{winner['jmeno']}** ({int(winner['kroky']):,} kroků)")
        st.bar_chart(data=stats, x="jmeno", y="kroky")
    else:
        st.info("Tento měsíc zatím žádné kroky. Kdo začne?")
else:
    st.info("Zatím žádná data v Google Tabulce.")

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
                "kroky": [int(kroky_cislo)]
            })
            
            # 2. Načtení čerstvých dat před zápisem
            fresh_df = load_data()
            
            # 3. Spojení a odeslání
            final_df = pd.concat([fresh_df, new_entry], ignore_index=True)
            conn.update(data=final_df)
            
            # 4. Úklid
            st.cache_data.clear()
            st.balloons()
            st.success("Hotovo! Kroky jsou v tabulce. 🚀")
            st.rerun()

# --- HISTORIE ---
if st.checkbox("Zobrazit historii"):
    st.dataframe(df.sort_values(by="datum", ascending=False), use_container_width=True)
