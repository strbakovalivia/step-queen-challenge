import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(
    page_title="StepQueen 🏃‍♀️", 
    page_icon="👑",
    layout="centered",
    initial_sidebar_state="collapsed"
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
        # Převod sloupce datum na skutečný typ datum, aby s ním šlo pracovat
        data['datum'] = pd.to_datetime(data['datum']).dt.date
        return data
    except Exception:
        return pd.DataFrame(columns=["datum", "jmeno", "kroky"])

df = load_data()

# --- VÝPOČET KRÁLOVNY A DASHBOARD ---
current_month_str = datetime.now().strftime("%m/%Y")
today_date = datetime.now().date()

st.subheader(f"📊 Přehled za {current_month_str}")

if not df.empty:
    # Pomocné výpočty
    df_temp = df.copy()
    df_temp['month_year'] = pd.to_datetime(df_temp['datum']).dt.strftime("%m/%Y")
    df_current = df_temp[df_temp['month_year'] == current_month_str]
    
    if not df_current.empty:
        # Celkové statistiky pro graf/výpočty
        stats = df_current.groupby("jmeno")["kroky"].sum().reset_index()
        den_v_mesici = datetime.now().day
        
        cols = st.columns(3)
        holky_nastaveni = {
            "Lili": {"icon": "👱‍♀️✨", "color": "#FF4B4B"},
            "Lenka": {"icon": "👩🏻", "color": "#4B8BFF"},
            "Monka": {"icon": "👱‍♀️", "color": "#FFD700"}
        }

        for i, (jmeno, info) in enumerate(holky_nastaveni.items()):
            # 1. Kroky celkem
            osoba_celkem = stats[stats['jmeno'] == jmeno]
            pocet_celkem = int(osoba_celkem['kroky'].iloc[0]) if not osoba_celkem.empty else 0
            
            # 2. Kroky dnes (filtrujeme jen dnešní datum)
            dnes_data = df[df['datum'] == today_date]
            osoba_dnes = dnes_data[dnes_data['jmeno'] == jmeno]
            pocet_dnes = int(osoba_dnes['kroky'].iloc[0]) if not osoba_dnes.empty else 0
            
            # 3. Průměr
            prumer_den = int(pocet_celkem / den_v_mesici)
            
            with cols[i]:
                st.markdown(
                    f"""
                    <div style="background-color: {info['color']}22; padding: 12px; border-radius: 15px; border: 2px solid {info['color']}; text-align: center; min-height: 220px;">
                        <h1 style="margin:0; font-size: 30px;">{info['icon']}</h1>
                        <p style="margin:0; font-weight: bold; color: {info['color']}; font-size: 18px;">{jmeno}</p>
                        <hr style="border: 0.5px solid {info['color']}55; margin: 8px 0;">
                        <p style="margin:0; font-size: 10px; text-transform: uppercase;">Dnes</p>
                        <h3 style="margin:0; font-size: 22px;">{pocet_dnes:,}</h3>
                        <hr style="border: 0.5px solid {info['color']}55; margin: 8px 0;">
                        <p style="margin:0; font-size: 10px; text-transform: uppercase;">Průměr: <b>{prumer_den:,}</b></p>
                        <p style="margin:0; font-size: 10px; text-transform: uppercase;">Celkem: <b>{pocet_celkem:,}</b></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Motivační hláška (kdo vede)
        winner_row = stats.loc[stats['kroky'].idxmax()]
        st.markdown(f"<br><center>👑 Aktuální StepQueen je <b>{winner_row['jmeno']}</b></center>", unsafe_allow_html=True)
        
        # 3. Určení vítězky a barevný graf
        winner_row = stats.loc[stats['kroky'].idxmax()]
        st.markdown(f"<br>👑 Aktuálně vede **{winner_row['jmeno']}**! Holky, makejte!", unsafe_allow_html=True)
        
        color_map = {"Lili": "#FF4B4B", "Lenka": "#4B8BFF", "Monka": "#FFD700"}
        fig = px.bar(
            stats, 
            x="jmeno", 
            y="kroky", 
            color="jmeno",
            color_discrete_map=color_map,
            text_auto=',.0f'
        )
        
        fig.update_traces(textposition='outside', cliponaxis=False)
        
        fig.update_layout(
            showlegend=False,             # Tímto zmizí ten červený/barevný sloupec vpravo (legenda)
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=30, l=0, r=0, b=0), # Vyladění okrajů
            xaxis_title="",               # Odstraní nápis "jmeno" pod grafem
            yaxis_visible=False,          # Skryje celou levou osu
            xaxis_visible=True            # Nechá jen jména pod sloupci
        )
        
        # config={'displayModeBar': False} zajistí, že neuvidíš tu lištu s foťákem a lupou
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("Tento měsíc zatím žádné kroky.")
else:
    st.info("Zatím žádná data.")

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

# --- FORMULÁŘ PRO ZÁPIS ---
st.divider()
with st.expander("➕ Zapsat dnešní kroky", expanded=False):
    with st.form("add_steps"):
        col1, col2 = st.columns(2)
        with col1:
            jmeno_volba = st.selectbox("Kdo jsi?", ["Lili", "Lenka", "Monka"], key="user_select")
        with col2:
            datum_volba = st.date_input("Den", datetime.now())
        
        kroky_cislo = st.number_input("Počet kroků", min_value=0, step=100, value=10000)
        if st.form_submit_button("Uložit ✨"):
            new_entry = pd.DataFrame({"datum": [datum_volba.strftime("%Y-%m-%d")], "jmeno": [jmeno_volba], "kroky": [int(kroky_cislo)]})
            fresh_df = load_data()
            final_df = pd.concat([fresh_df, new_entry], ignore_index=True)
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
        if row['jmeno'] == "Lili": color, icon = "#FF4B4B", "👱‍♀️✨"
        elif row['jmeno'] == "Lenka": color, icon = "#4B8BFF", "👩🏻"
        elif row['jmeno'] == "Monka": color, icon = "#FFD700", "👱‍♀️"
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
