# app.py

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# Caminho do arquivo CSV
caminho_csv = 'dados/registros.csv'
os.makedirs('dados', exist_ok=True)

# Se o CSV ainda não existe, cria com cabeçalho
if not os.path.exists(caminho_csv):
    pd.DataFrame(columns=["Data", "Operador", "Frota", "Horímetro Inicial", "Horímetro Final", "Horas Trabalhadas"]).to_csv(caminho_csv, index=False)

# Função para registrar horímetro
def registrar_horimetro():
    st.subheader("Registrar Horímetro")

    with st.form("formulario_registro"):
        operador = st.text_input("Nome do operador")
        frota = st.selectbox("Número da Frota", ["230", "231", "232", "233", "234", "235"])
        horimetro_inicial = st.number_input("Horímetro Inicial", format="%.2f")
        horimetro_final = st.number_input("Horímetro Final", format="%.2f")
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        enviado = st.form_submit_button("Registrar")

        if enviado:
            horas_trabalhadas = round(horimetro_final - horimetro_inicial, 2)
            novo = pd.DataFrame([[data, operador, frota, horimetro_inicial, horimetro_final, horas_trabalhadas]],
                                columns=["Data", "Operador", "Frota", "Horímetro Inicial", "Horímetro Final", "Horas Trabalhadas"])
            df_antigo = pd.read_csv(caminho_csv)
            df_novo = pd.concat([df_antigo, novo], ignore_index=True)
            df_novo.to_csv(caminho_csv, index=False)
            st.success("✅ Registro salvo com sucesso!")

# Função para a área do administrador
def visualizar_dados():
    st.subheader("📊 Registros por Frota")
    df = pd.read_csv(caminho_csv)

    frota_escolhida = st.selectbox("Selecione uma frota para filtrar", df["Frota"].unique())
    df_filtrado = df[df["Frota"] == frota_escolhida]

    st.dataframe(df_filtrado)
    st.markdown(f"**Total de horas trabalhadas:** {df_filtrado['Horas Trabalhadas'].sum():.2f} h")

    if st.button("📁 Exportar Excel"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name='Horimetros')
        st.download_button(label="⬇️ Baixar Excel", data=output.getvalue(), file_name="horimetros.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Estilo
st.set_page_config(page_title="Controle de Horímetro", layout="centered")
st.title("Controle de Horímetro - Transjap")

abas = st.tabs(["Registrar", "Administrador"])

with abas[0]:
    registrar_horimetro()

with abas[1]:
    visualizar_dados()
