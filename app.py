import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(
    page_title="StepQueen Challenge",
    page_icon="https://cdn-icons-png.flaticon.com/512/182/182335.png", # Ikona zlaté koruny
    layout="centered"
)

st.title("🏃‍♀️ StepQueen Challenge")
st.write("Souboj mezi **Lili**, **Lenka** a **Monka**!")

# --- PROPOJENÍ S GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(worksheet="List1", ttl="0s")
        if data is None or data.empty:
            return pd.DataFrame(columns=["datum", "jmeno", "kroky"])
        data['datum'] = pd.to_datetime(data['datum']).dt.date
        return data
    except Exception:
        return pd.DataFrame(columns=["datum", "jmeno", "kroky"])

df = load_data()

# --- VÝPOČET KRÁLOVNY A DASHBOARD ---
# 1. Příprava dat pro výběr měsíce
df_temp = df.copy()
df_temp['month_year'] = pd.to_datetime(df_temp['datum']).dt.strftime("%m/%Y")

current_month_str = datetime.now().strftime("%m/%Y")
today_date = datetime.now().date()

# 2. Vytvoření seznamu dostupných měsíců z dat + aktuální měsíc
seznam_mesicu = sorted(df_temp['month_year'].unique().tolist(), reverse=True) if not df.empty else []
if current_month_str not in seznam_mesicu:
    seznam_mesicu.insert(0, current_month_str)

# 3. Samotný výběr měsíce v aplikaci
vybrany_mesic = st.selectbox("📅 Zobrazit statistiky za období:", seznam_mesicu)
st.subheader(f"📊 Přehled za {vybrany_mesic}")

if not df.empty:
    # Filtrace dat podle vybraného měsíce
    df_current = df_temp[df_temp['month_year'] == vybrany_mesic]
    
    if not df_current.empty:
        stats = df_current.groupby("jmeno")["kroky"].sum().reset_index()
        
        # Výpočet dnů pro průměr
        if vybrany_mesic == current_month_str:
            div_days = datetime.now().day
        else:
            div_days = 30 
        
        cols = st.columns(3)
        holky_nastaveni = {
            "Lili": {"icon": "👱‍♀️✨", "color": "#4B8BFF"}, 
            "Lenka": {"icon": "👩🏻", "color": "#FFD700"},   
            "Monka": {"icon": "👱‍♀️", "color": "#FF4B4B"}    
        }

        for i, (jmeno, info) in enumerate(holky_nastaveni.items()):
            osoba_total = stats[stats['jmeno'] == jmeno]
            pocet_total = int(osoba_total['kroky'].iloc[0]) if not osoba_total.empty else 0
            
            # Kroky DNES / Formátování čísla pro zobrazení
            if vybrany_mesic == current_month_str:
                dnes_data = df[df['datum'] == today_date]
                osoba_dnes = dnes_data[dnes_data['jmeno'] == jmeno]
                pocet_dnes_val = int(osoba_dnes['kroky'].sum()) if not osoba_dnes.empty else 0
                display_dnes = f"{pocet_dnes_val:,}"
                dnes_label = "DNES"
            else:
                display_dnes = "-"
                dnes_label = "VÝSLEDNÉ"

            prumer_den = int(pocet_total / div_days)
            
            with cols[i]:
                st.markdown(
                    f"""
                    <div style="background-color: {info['color']}22; padding: 12px; border-radius: 15px; border: 2px solid {info['color']}; text-align: center; min-height: 200px;">
                        <h2 style="margin:0; font-size: 30px;">{info['icon']}</h2>
                        <p style="margin:0; font-weight: bold; color: {info['color']}; font-size: 14px;">{jmeno}</p>
                        <hr style="border: 0.5px solid {info['color']}55; margin: 5px 0;">
                        <p style="margin:0; font-size: 10px; opacity: 0.8;">{dnes_label}</p>
                        <h3 style="margin:0; font-size: 22px;">{display_dnes}</h3>
                        <hr style="border: 0.5px solid {info['color']}55; margin: 5px 0;">
                        <p style="margin:0; font-size: 11px;">ø den: <b>{prumer_den:,}</b></p>
                        <p style="margin:0; font-size: 11px;">celkem: <b>{pocet_total:,}</b></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        winner_row = stats.loc[stats['kroky'].idxmax()]
        st.write("")
        st.success(f"👑 Královnou měsíce {vybrany_mesic} je **{winner_row['jmeno']}**!")

# --- SEKCE ODMĚNA PRO KRÁLOVNU ---
st.divider()
st.subheader("🎁 Odměna pro vítězku měsíce")

try:
    df_darky = conn.read(worksheet="Darky", ttl="0s")
except:
    df_darky = pd.DataFrame(columns=["navrh", "autor", "lajky"])

with st.expander("💡 Navrhnout nebo hlasovat pro dárek"):
    with st.form("new_gift"):
        novy_tip = st.text_input("Tvůj tip na dárek:")
        kdo_navrhl = st.selectbox("Navrhuje:", ["Lili", "Lenka", "Monka"])
        if st.form_submit_button("Přidat návrh"):
            if novy_tip:
                new_gift_row = pd.DataFrame({"navrh": [novy_tip], "autor": [kdo_navrhl], "lajky": [0]})
                updated_darky = pd.concat([df_darky, new_gift_row], ignore_index=True)
                conn.update(worksheet="Darky", data=updated_darky)
                st.cache_data.clear()
                st.rerun()

    if not df_darky.empty:
        for idx, row in df_darky.iterrows():
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.write(f"**{row['navrh']}**")
                st.caption(f"od {row['autor']}")
            with c2:
                st.write(f"❤️ {int(row['lajky'])}")
            with c3:
                if st.button("Lajk", key=f"like_{idx}"):
                    df_darky.at[idx, 'lajky'] += 1
                    conn.update(worksheet="Darky", data=df_darky)
                    st.cache_data.clear()
                    st.rerun()

# --- FORMULÁŘ PRO ZÁPIS S KONTROLOU EXISTUJÍCÍCH DAT ---
st.divider()
with st.expander("➕ Zapsat / Opravit kroky", expanded=False):
    with st.form("add_steps"):
        col1, col2 = st.columns(2)
        with col1:
            jmeno_volba = st.selectbox("Kdo jsi?", ["Lili", "Lenka", "Monka"], key="user_select")
        with col2:
            datum_volba = st.date_input("Den", datetime.now())
        
        # Kontrola, zda již existuje záznam
        existujici_zaznam = df[(df['jmeno'] == jmeno_volba) & (df['datum'] == datum_volba)]
        
        if not existujici_zaznam.empty:
            puvodni_kroky = int(existujici_zaznam['kroky'].iloc[0])
            st.info(f"💡 Pro tento den už máš zapsáno **{puvodni_kroky:,}** kroků. Novým uložením hodnotu opravíš.")
        
        kroky_cislo = st.number_input("Zadej správný počet kroků", min_value=0, step=100, value=10000)
        
        if st.form_submit_button("Uložit změnu ✨"):
            fresh_df = load_data()
            
            # Odstraníme případný starý záznam pro tento den a osobu
            fresh_df = fresh_df[~((fresh_df['jmeno'] == jmeno_volba) & (fresh_df['datum'] == datum_volba))]
            
            # Přidáme nový/opravený záznam
            new_entry = pd.DataFrame({
                "datum": [datum_volba], 
                "jmeno": [jmeno_volba], 
                "kroky": [int(kroky_cislo)]
            })
            
            final_df = pd.concat([fresh_df, new_entry], ignore_index=True)
            final_df = final_df.sort_values(by="datum", ascending=False)
            
            conn.update(worksheet="List1", data=final_df)
            st.cache_data.clear()
            st.balloons()
            st.rerun()

# --- SPRÁVA ZÁZNAMŮ ---
st.divider()
st.subheader("🗑️ Historie a mazání")
if not df.empty:
    df_display = df.copy().sort_values(by="datum", ascending=False)
    for index, row in df_display.iterrows():
        # Přiřazení barev pro historii (Lili modrá, Lenka žlutá, Monka červená)
        if row['jmeno'] == "Lili": color, icon = "#4B8BFF", "👱‍♀️✨"
        elif row['jmeno'] == "Lenka": color, icon = "#FFD700", "👩🏻"
        elif row['jmeno'] == "Monka": color, icon = "#FF4B4B", "👱‍♀️"
        else: color, icon = "#808080", "🏃‍♀️"
        
        with st.container():
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                st.markdown(f"**📅 {row['datum']}**")
                st.markdown(f"<span style='color:{color}; font-weight:bold;'>{icon} {row['jmeno']}</span>", unsafe_allow_html=True)
            with c2: st.markdown(f"**👣 {int(row['kroky']):,}**")
            with c3:
                if st.button("🗑️", key=f"del_{index}"):
                    df_to_save = df.drop(index)
                    conn.update(worksheet="List1", data=df_to_save)
                    st.cache_data.clear()
                    st.rerun()
            st.markdown("---")
