import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# Caminho do arquivo CSV
CAMINHO_CSV = 'dados/horimetro.csv'
os.makedirs('dados', exist_ok=True)

# Carrega os dados existentes ou cria um novo DataFrame
def carregar_dados():
    if os.path.exists(CAMINHO_CSV) and os.path.getsize(CAMINHO_CSV) > 0:
        return pd.read_csv(CAMINHO_CSV)
    else:
        return pd.DataFrame(columns=["Data", "Operador", "Frota", "Horímetro Inicial", "Horímetro Final", "Horas Trabalhadas"])

# Salva os dados
def salvar_dados(df):
    df.to_csv(CAMINHO_CSV, index=False)

# Exporta para Excel
def exportar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Horimetro')
    output.seek(0)
    return output

# Estilo da interface
st.set_page_config(
    page_title="Controle de Horímetro - Transjap",
    layout="wide",
)

st.markdown("""
    <style>
        body, .stApp {
            background-color: #f7f9fc;
            font-family: 'Segoe UI', sans-serif;
        }
        .main > div {
            padding-top: 1rem;
        }
        .css-1d391kg {
            color: #333;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Controle de Horímetro - Máquinas Transjap")

aba = st.sidebar.radio("Navegação", ["Registrar Horímetro", "Administrador"])

df = carregar_dados()

if aba == "Registrar Horímetro":
    st.subheader("📋 Registro Diário de Horímetro")

    with st.form("registro_form"):
        col1, col2 = st.columns(2)
        with col1:
            operador = st.text_input("Nome do Operador", "")
            frota = st.selectbox("Número da Frota", options=["Selecione", "230", "231", "240", "250", "260", "270"])
        with col2:
            horimetro_inicial = st.number_input("Horímetro Inicial", min_value=0.0, step=0.01)
            horimetro_final = st.number_input("Horímetro Final", min_value=0.0, step=0.01)

        enviado = st.form_submit_button("Salvar Registro")

    if enviado:
        if operador and frota != "Selecione" and horimetro_final > horimetro_inicial:
            data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            horas_trabalhadas = round(horimetro_final - horimetro_inicial, 2)
            novo = pd.DataFrame([{
                "Data": data,
                "Operador": operador,
                "Frota": frota,
                "Horímetro Inicial": horimetro_inicial,
                "Horímetro Final": horimetro_final,
                "Horas Trabalhadas": horas_trabalhadas
            }])
            df = pd.concat([df, novo], ignore_index=True)
            salvar_dados(df)
            st.success(f"✅ Registro salvo com sucesso! Total de horas: {horas_trabalhadas} h")
        else:
            st.error("❌ Verifique os campos. O horímetro final deve ser maior que o inicial, e os dados devem estar completos.")

else:
    st.subheader("📊 Painel do Administrador")

    if df.empty:
        st.warning("Nenhum registro encontrado.")
    else:
        frota_selecionada = st.selectbox("Filtrar por frota", options=["Todas"] + sorted(df["Frota"].unique().tolist()))
        
        if frota_selecionada != "Todas":
            df_filtrado = df[df["Frota"] == frota_selecionada]
        else:
            df_filtrado = df

        st.markdown(f"**🔄 Total de registros:** {len(df_filtrado)}")
        st.markdown(f"**⏱️ Total de horas registradas:** {round(df_filtrado['Horas Trabalhadas'].sum(), 2)} h")

        st.dataframe(df_filtrado, use_container_width=True)

        excel = exportar_excel(df_filtrado)
        st.download_button(
            label="📥 Baixar Excel",
            data=excel,
            file_name="horimetro_transjap.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

with abas[1]:
    visualizar_dados()
