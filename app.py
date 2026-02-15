import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(
    page_title="StepQueen 🏃‍♀️", 
    page_icon="👑",
    layout="centered", # Na mobilu je lepší 'centered' než 'wide'
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
    # Převod na datetime, aby fungovaly filtry
    df['datum'] = pd.to_datetime(df['datum'])
    df_current = df[df['datum'].dt.strftime("%m/%Y") == current_month]
    
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
    # Zkontrolujeme, kdo dnes ještě nezapsal
    today_str = now.strftime("%Y-%m-%d")
    zapsali_dnes = df[df['datum'].astype(str) == today_str]['jmeno'].unique()
    
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
            # 1. Vytvoření nového řádku
            new_entry = pd.DataFrame({
                "datum": [datum_volba.strftime("%Y-%m-%d")],
                "jmeno": [jmeno_volba],
                "kroky": [int(kroky_cislo)]
            })
            
            # 2. Načtení čerstvých dat
            fresh_df = load_data()
            
            # 3. Spojení starých dat s novými
            final_df = pd.concat([fresh_df, new_entry], ignore_index=True)
            
            # 4. Odeslání do Google Sheets (TADY MÁ BÝT UPDATE)
            conn.update(worksheet="List1", data=final_df)
            
            # 5. Refresh
            st.cache_data.clear()
            st.balloons()
            st.success("Kroky úspěšně propsány do Google Tabulky! 🚀")
            st.rerun()

# --- HEZČÍ SPRÁVA ZÁZNAMŮ ---
st.divider()
st.subheader("🗑️ Upravit nebo smazat záznamy")

# Seřadíme data od nejnovějších
df_display = df.copy().sort_values(by="datum", ascending=False)

for index, row in df_display.iterrows():
    # Definice barev pro holky
    color = "#FF4B4B" if row['jmeno'] == "Lili" else "#4B8BFF" if row['jmeno'] == "Lenka" else "#FFD700"
    
    # Vytvoření "karty" pro každý záznam
    with st.container():
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            st.markdown(f"**📅 {row['datum']}**")
        with col2:
            st.markdown(f"<span style='color:{color}; font-weight:bold;'>👤 {row['jmeno']}</span>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"**👣 {int(row['kroky']):,}**")
        with col4:
            # Unikátní klíč pro každé tlačítko smazání
            if st.button("Smazat", key=f"del_{index}"):
                new_df = df.drop(index)
                conn.update(worksheet="List1", data=new_df)
                st.cache_data.clear()
                st.success("Smazáno!")
                st.rerun()
        st.markdown("---") # Oddělovač mezi kartami
    }
)

if st.button("💾 Uložit všechny změny do tabulky"):
    try:
        # Převod datumu zpět na řetězec, aby se v Google Sheets správně zobrazoval
        if "datum" in edited_df.columns:
            edited_df["datum"] = edited_df["datum"].astype(str)
        
        # Odeslání kompletně upraveného DataFrame zpět
        conn.update(worksheet="List1", data=edited_df)
        
        st.cache_data.clear()
        st.success("Tabulka byla úspěšně aktualizována! 🚀")
        st.rerun()
    except Exception as e:
        st.error(f"Chyba při ukládání: {e}")

# --- HISTORIE (Původní zobrazení pro kontrolu) ---
if st.checkbox("Zobrazit rychlý přehled historie"):
    st.write(df.sort_values(by="datum", ascending=False))
