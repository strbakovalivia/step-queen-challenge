import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(
    page_title="StepQueen 🏃‍♀️", 
    page_icon="👑",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🏃‍♀️ StepQueen Challenge")
st.write("Souboj mezi **Lili**, **Lenkou** a **Monkou**!")

# --- PROPOJENÍ S GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Funkce pro bezpečné načtení dat
def load_data():
    try:
        data = conn.read(worksheet="List1", ttl="0s")
        if data is None or data.empty:
            return pd.DataFrame(columns=["datum", "jmeno", "kroky"])
        return data
    except Exception:
        return pd.DataFrame(columns=["datum", "jmeno", "kroky"])

df = load_data()

# --- VÝPOČET KRÁLOVNY ---
current_month = datetime.now().strftime("%m/%Y")

if not df.empty:
    # Převod na datetime, aby fungovaly filtry a správné řazení
    df['datum'] = pd.to_datetime(df['datum']).dt.date
    
    # Filtrujeme aktuální měsíc
    df_current = df[pd.to_datetime(df['datum']).dt.strftime("%m/%Y") == current_month]
    
    if not df_current.empty:
        stats = df_current.groupby("jmeno")["kroky"].sum().reset_index()
        winner_row = stats.loc[stats['kroky'].idxmax()]
        st.success(f"🏆 Aktuální královna měsíce: **{winner_row['jmeno']}** ({int(winner_row['kroky']):,} kroků)")
        st.bar_chart(data=stats, x="jmeno", y="kroky")
    else:
        st.info("Tento měsíc zatím žádné kroky. Kdo začne?")
else:
    st.info("Zatím žádná data. Šup ven na procházku!")
    
# --- VEČERNÍ PŘIPOMÍNAČ V APLIKACI ---
now = datetime.now()
if now.hour >= 21:
    today_date = now.date()
    # Zkontrolujeme, kdo dnes zapsal
    zapsali_dnes = df[df['datum'] == today_date]['jmeno'].unique()
    chybejici = [j for j in ["Lili", "Lenka", "Monka"] if j not in zapsali_dnes]
    
    if chybejici:
        st.warning(f"⚠️ Je po deváté večer a tyto královny ještě nezapsaly kroky: {', '.join(chybejici)}!")

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
            new_entry = pd.DataFrame({
                "datum": [datum_volba.strftime("%Y-%m-%d")],
                "jmeno": [jmeno_volba],
                "kroky": [int(kroky_cislo)]
            })
            fresh_df = load_data()
            final_df = pd.concat([fresh_df, new_entry], ignore_index=True)
            conn.update(worksheet="List1", data=final_df)
            st.cache_data.clear()
            st.balloons()
            st.rerun()

# --- HEZČÍ SPRÁVA ZÁZNAMŮ (Smazání) ---
st.divider()
st.subheader("🗑️ Historie a mazání")

if not df.empty:
    # Seřadíme od nejnovějších
    df_display = df.copy().sort_values(by="datum", ascending=False)

    for index, row in df_display.iterrows():
        color = "#FF4B4B" if row['jmeno'] == "Lili" else "#4B8BFF" if row['jmeno'] == "Lenka" else "#FFD700"
        
        with st.container():
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                st.markdown(f"**📅 {row['datum']}**")
                st.markdown(f"<span style='color:{color}; font-weight:bold;'>👤 {row['jmeno']}</span>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"**👣 {int(row['kroky']):,}**")
            with c3:
                # Smažeme přímo pomocí tlačítka u řádku
                if st.button("🗑️", key=f"del_{index}"):
                    # Musíme smazat z původního df (pomocí indexu)
                    df_to_save = df.drop(index)
                    conn.update(worksheet="List1", data=df_to_save)
                    st.cache_data.clear()
                    st.rerun()
            st.markdown("---")
else:
    st.write("Žádná data k zobrazení.")

# --- RYCHLÝ PŘEHLED ---
if st.checkbox("Zobrazit tabulku pro kontrolu"):
    st.dataframe(df)
