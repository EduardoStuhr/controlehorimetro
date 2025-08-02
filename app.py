import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Caminho para o CSV
caminho_csv = 'dados/registros.csv'
os.makedirs(os.path.dirname(caminho_csv), exist_ok=True)

# Cria CSV se não existir
if not os.path.exists(caminho_csv):
    df_vazio = pd.DataFrame(columns=[
        'Data', 'Frota', 'Horímetro Inicial', 'Horímetro Final', 'Horas Trabalhadas', 'Registrado por'
    ])
    df_vazio.to_csv(caminho_csv, index=False)

# Configurações da página
st.set_page_config(page_title="Horímetro Transjap", page_icon="🛠️", layout="wide")

# CSS personalizado para fundo e estilos
st.markdown("""
    <style>
        body {
            background-color: #f0f2f6;
        }
        .main {
            background-color: #f0f2f6;
        }
        header {
            background-color: #ffffff;
        }
        .block-container {
            padding: 2rem;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }
        .stButton>button {
            background-color: #2b9348;
            color: white;
            border-radius: 10px;
            padding: 0.6em 1.2em;
            font-weight: bold;
            transition: background-color 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #267a3e;
        }
        .stSelectbox>div>div {
            border-radius: 6px;
        }
        h2 {
            color: #1e90ff;
        }
    </style>
""", unsafe_allow_html=True)

# Menu lateral
menu = st.sidebar.radio("📂 Navegação", ["Registrar Horímetro", "Painel do Administrador"])

# Função para carregar dados com tratamento
def carregar_dados():
    try:
        df = pd.read_csv(caminho_csv)
        if 'Horas Trabalhadas' not in df.columns:
            df['Horas Trabalhadas'] = df['Horímetro Final'] - df['Horímetro Inicial']
            df.to_csv(caminho_csv, index=False)
        df['Data'] = pd.to_datetime(df['Data'])
        return df.sort_values(by="Data", ascending=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=[
            'Data', 'Frota', 'Horímetro Inicial', 'Horímetro Final', 'Horas Trabalhadas', 'Registrado por'
        ])

# ===== Página de Registro =====
if menu == "Registrar Horímetro":
    st.markdown("<h2 style='text-align:center;'>📋 Registro de Horímetro - Transjap</h2>", unsafe_allow_html=True)
    st.markdown("Registre abaixo os dados do dia da máquina.")
    st.markdown("---")

    with st.form("formulario_horimetro"):
        col1, col2 = st.columns(2)

        with col1:
            operador = st.text_input("👷 Nome do operador")
            frota = st.text_input("🚜 Frota da máquina")

        with col2:
            horimetro_inicial = st.number_input("⏱️ Horímetro Inicial", min_value=0.0, step=0.01)
            horimetro_final = st.number_input("⏱️ Horímetro Final", min_value=0.0, step=0.01)

        enviado = st.form_submit_button("✅ Registrar")

        if enviado:
            if operador and frota and horimetro_final >= horimetro_inicial:
                horas_trabalhadas = round(horimetro_final - horimetro_inicial, 2)
                data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                novo = pd.DataFrame([[data, frota, horimetro_inicial, horimetro_final, horas_trabalhadas, operador]],
                                    columns=['Data', 'Frota', 'Horímetro Inicial', 'Horímetro Final', 'Horas Trabalhadas', 'Registrado por'])

                df_existente = carregar_dados()
                df_atualizado = pd.concat([df_existente, novo], ignore_index=True)
                df_atualizado.to_csv(caminho_csv, index=False)

                st.success(f"✅ Registro salvo com sucesso! ({horas_trabalhadas} horas trabalhadas)")
            else:
                st.warning("⚠️ Preencha todos os campos corretamente!")

# ===== Painel do Administrador =====
elif menu == "Painel do Administrador":
    st.markdown("<h2 style='text-align:center;'>🧑‍💼 Painel do Administrador</h2>", unsafe_allow_html=True)
    st.markdown("Visualize todos os registros agrupados por frota.")
    st.markdown("---")

    df = carregar_dados()

    if df.empty:
        st.warning("Nenhum registro encontrado.")
    else:
        st.markdown(f"🔢 **Total de registros:** `{len(df)}`")
        st.markdown(f"⏱️ **Total de horas registradas:** `{round(df['Horas Trabalhadas'].sum(), 2)} h`")
        st.markdown("### 📌 Registros agrupados por frota:")

        frotas = sorted(df['Frota'].unique())
        for frota in frotas:
            with st.expander(f"🚜 Frota {frota} - Total de registros: {len(df[df['Frota'] == frota])}"):
                df_frota = df[df['Frota'] == frota].copy()
                df_frota = df_frota.sort_values(by="Data", ascending=False)
                st.dataframe(df_frota[['Data', 'Horímetro Inicial', 'Horímetro Final', 'Horas Trabalhadas', 'Registrado por']],
                             use_container_width=True)
