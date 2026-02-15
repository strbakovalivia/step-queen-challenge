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
# --- VÝPOČET KRÁLOVNY A DASHBOARD ---
if not df_current.empty:
    stats = df_current.groupby("jmeno")["kroky"].sum().reset_index()
    
    # Výpočet průměru (počet dní v měsíci do dneška)
    den_v_mesici = datetime.now().day
    
    cols = st.columns(3)
    holky_nastaveni = {
        "Lili": {"icon": "👱‍♀️✨", "color": "#FF4B4B"},
        "Lenka": {"icon": "👩🏻", "color": "#4B8BFF"},
        "Monka": {"icon": "👱‍♀️", "color": "#FFD700"}
    }

    for i, (jmeno, info) in enumerate(holky_nastaveni.items()):
        osoba_data = stats[stats['jmeno'] == jmeno]
        pocet_kroku = int(osoba_data['kroky'].iloc[0]) if not osoba_data.empty else 0
        prumer_den = int(pocet_kroku / den_v_mesici) # Denní průměr v měsíci
        
        with cols[i]:
            st.markdown(
                f"""
                <div style="background-color: {info['color']}22; padding: 15px; border-radius: 15px; border: 2px solid {info['color']}; text-align: center;">
                    <h1 style="margin:0;">{info['icon']}</h1>
                    <p style="margin:0; font-weight: bold; color: {info['color']};">{jmeno}</p>
                    <h2 style="margin:0;">{pocet_kroku:,}</h2>
                    <p style="margin:0; font-size: 12px;">celkem</p>
                    <hr style="border: 0.5px solid {info['color']}55;">
                    <p style="margin:0; font-size: 14px; font-weight: bold;">{prumer_den:,}</p>
                    <p style="margin:0; font-size: 10px; opacity: 0.8;">denní průměr</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Určení celkové vítězky pro motivační zprávu
        winner_row = stats.loc[stats['kroky'].idxmax()]
        st.balloons() if winner_row['kroky'] > 0 else None
        st.markdown(f"👑 Aktuálně vede **{winner_row['jmeno']}**! Holky, makejte!")
        
        # Stylový graf pod kartami
        st.bar_chart(data=stats, x="jmeno", y="kroky", color="#FF4B4B")
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
    df_display = df.copy().sort_values(by="datum", ascending=False)

    for index, row in df_display.iterrows():
        # Nastavení ikon a barev podle jména
        if row['jmeno'] == "Lili":
            color = "#FF4B4B"  # Červená/Růžová
            icon = "👱‍♀️✨"      # Melír (blonďatá s jiskrou)
        elif row['jmeno'] == "Lenka":
            color = "#4B8BFF"  # Modrá
            icon = "👩🏻"        # Tmavovláska
        elif row['jmeno'] == "Monka":
            color = "#FFD700"  # Zlatá
            icon = "👱‍♀️"        # Blondýnka
        else:
            color = "#808080"
            icon = "🏃‍♀️"
        
        with st.container():
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                st.markdown(f"**📅 {row['datum']}**")
                # Zobrazení unikátní ikony a jména v barvě
                st.markdown(f"<span style='color:{color}; font-weight:bold;'>{icon} {row['jmeno']}</span>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"**👣 {int(row['kroky']):,}**")
            with c3:
                if st.button("🗑️", key=f"del_{index}"):
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
