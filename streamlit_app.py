import os; os.system("pip install plotly pandas")
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone, timedelta
import base64

st.set_page_config(page_title="FAC PAMPAS — Ritmo de Batalha", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<meta http-equiv=\"refresh\" content=\"60\">", unsafe_allow_html=True)

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    return None

img_fac_b64 = get_image_base64("fac.png")

st.markdown("""
<style>
    .stApp { background-color: #030811; color: #C9D1D9; }
    .header-clock-box { font-family: "Courier New", Courier, monospace; padding: 5px; }
    .zulu-text { font-size: 28px; color: #00BFFF; font-weight: 900; line-height: 1.1; }
    .local-text { font-size: 13px; color: #FFD700; font-weight: 700; }
    .main-title { text-align: center; font-size: 32px; font-weight: 900; color: #FFFFFF; letter-spacing: 3px; margin-top: -5px; }
    .blinking-badge-container { display: flex; justify-content: center; margin-top: 10px; margin-bottom: 10px; }
    .blinking-badge { background: linear-gradient(90deg, #B22222 0%, #FF0000 50%, #B22222 100%); color: #FFFFFF; font-weight: 800; font-size: 13px; padding: 6px 18px; border-radius: 20px; border: 1px solid #FF4D4D; box-shadow: 0 0 12px rgba(255, 0, 0, 0.8); letter-spacing: 1px; animation: pulseGlow 1.5s infinite; display: inline-flex; align-items: center; gap: 8px; }
    @keyframes pulseGlow { 0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.8); transform: scale(1); } 50% { box-shadow: 0 0 0 10px rgba(255, 0, 0, 0); transform: scale(1.02); } 100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); transform: scale(1); } }
    .floating-logo-container { display: flex; justify-content: flex-end; align-items: center; padding-right: 10px; }
    .floating-logo-img { width: 110px; height: auto; border-radius: 12px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6); border: 1px solid #30363D; background-color: #0B0E14; }
</style>
""", unsafe_allow_html=True)

agora_utc = datetime.now(timezone.utc)
agora_local = agora_utc.astimezone(timezone(timedelta(hours=-3)))
str_zulu = agora_utc.strftime("%H:%MZ")
str_local = agora_local.strftime("%H:%MP")
hoje_str = agora_local.strftime("%Y-%m-%d")

col_esq, col_cen, col_dir = st.columns([3, 6, 3])
with col_esq:
    st.markdown(f'''<div class="header-clock-box"><div class="zulu-text">{str_zulu}</div><div class="local-text">LOCAL: {str_local}</div></div>''', unsafe_allow_html=True)
with col_cen:
    st.markdown('<div class="main-title">FAC PAMPAS</div>', unsafe_allow_html=True)
with col_dir:
    st.markdown('<div class="floating-logo-container">', unsafe_allow_html=True)
    if img_fac_b64:
        st.markdown(f'''<img src="{img_fac_b64}" class="floating-logo-img" alt="FAC PAMPAS">''', unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align: right; margin:0;'>🛡️</h1>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

SHEET_ID = "10HRI46x5vI43i8-mXoQLexxsGDZvKfTG"
GID = "1505958346"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=15)
def carregar_dados():
    try: return pd.read_csv(CSV_URL)
    except: return pd.DataFrame()

df = carregar_dados()
dados_gantt = []
atividades_em_andamento = set()

if not df.empty:
    col_etiqueta = df.columns[0]
    colunas_horarios = list(df.columns[1:])
    for idx, col in enumerate(colunas_horarios):
        col_str = str(col).strip()
        if len(col_str) >= 5 and ":" in col_str: h_inicio_str = col_str[:5]
        else: continue
        if idx + 1 < len(colunas_horarios):
            prox_col_str = str(colunas_horarios[idx + 1]).strip()
            h_fim_str = prox_col_str[:5] if len(prox_col_str) >= 5 and ":" in prox_col_str else "23:59"
        else: h_fim_str = "23:59"
        try:
            time_start = pd.to_datetime(f"{hoje_str} {h_inicio_str}")
            time_end = pd.to_datetime(f"{hoje_str} {h_fim_str}")
        except: continue
        for _, row in df.iterrows():
            etiqueta = str(row[col_etiqueta]).strip() if pd.notna(row[col_etiqueta]) else ""
            val = str(row[col]).strip() if pd.notna(row[col]) else ""
            if val != "" and val.lower() not in ["none", "nan", "null"]:
                time_now = pd.to_datetime(agora_local.strftime("%Y-%m-%d %H:%M"))
                is_andamento = (time_start <= time_now < time_end)
                dados_gantt.append({"Etiqueta": etiqueta, "Inicio": time_start, "Fim": time_end, "Evento": val, "Status": "EM ANDAMENTO" if is_andamento else "PROGRAMADO"})
                if is_andamento: atividades_em_andamento.add(val)

if atividades_em_andamento:
    texto_eventos = " | ".join(sorted(list(atividades_em_andamento)))
    st.markdown(f'''<div class="blinking-badge-container"><div class="blinking-badge"><span>🔴 AGORA ({str_local}):</span> {texto_eventos}</div></div>''', unsafe_allow_html=True)

st.markdown("<h4 style='color: #00BFFF; margin-bottom: 10px;'>⚔️ Ritmo de Batalha - FAC PAMPAS COMAEX 2026</h4>", unsafe_allow_html=True)

if dados_gantt:
    df_gantt = pd.DataFrame(dados_gantt)
    fig = px.timeline(df_gantt, x_start="Inicio", x_end="Fim", y="Etiqueta", color="Status", hover_data=["Evento"], text="Evento", color_discrete_map={"EM ANDAMENTO": "#FF2400", "PROGRAMADO": "#1E90FF"})
    fig.update_yaxes(autorange="reversed", title="Etiqueta / Setor", tickfont=dict(color="white"))
    fig.update_xaxes(title="", tickfont=dict(color="white"))
    fig.add_vline(x=pd.to_datetime(agora_local.strftime("%Y-%m-%d %H:%M:%S")), line_width=3, line_dash="solid", line_color="red")
    fig.update_layout(plot_bgcolor="#0A0D14", paper_bgcolor="#0A0D14", font=dict(color="white"), margin=dict(l=10, r=10, t=10, b=10), height=620, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_traces(textposition="inside", insidetextanchor="middle")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nenhuma atividade cadastrada na planilha para exibição no Ritmo de Batalha.")
