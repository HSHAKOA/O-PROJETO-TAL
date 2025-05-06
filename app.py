
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Carrega ou cria o DataFrame
try:
    df = pd.read_csv("financas.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=["Tipo", "Descrição", "Categoria", "Valor", "Data"])

st.title("💸 Controle de Finanças Pessoais")

# --- Formulário para adicionar transação ---
st.header("Adicionar Transação")
with st.form("form_transacao"):
    tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
    descricao = st.text_input("Descrição")
    categoria = st.text_input("Categoria")
    valor = st.number_input("Valor (R$)", step=0.01)
    enviado = st.form_submit_button("Salvar")

    if enviado and descricao and categoria and valor > 0:
        nova = {
            "Tipo": tipo,
            "Descrição": descricao,
            "Categoria": categoria,
            "Valor": float(valor),
            "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        df = df._append(nova, ignore_index=True)
        df.to_csv("financas.csv", index=False)
        st.success("Transação salva com sucesso!")

# --- Filtros por mês e ano ---
st.header("📅 Filtro de Período")
mes = st.selectbox("Mês", list(range(1, 13)), format_func=lambda x: datetime(1900, x, 1).strftime('%B'))
ano = st.selectbox("Ano", sorted(df["Data"].apply(lambda x: str(x)[:4]).unique()) if not df.empty else [datetime.now().year])
df["Data"] = pd.to_datetime(df["Data"])
df_filtrado = df[(df["Data"].dt.month == mes) & (df["Data"].dt.year == int(ano))]

# --- Saldo atual ---
st.header("💰 Saldo Atual")
total_receitas = df_filtrado[df_filtrado["Tipo"] == "Receita"]["Valor"].sum()
total_despesas = df_filtrado[df_filtrado["Tipo"] == "Despesa"]["Valor"].sum()
saldo = total_receitas - total_despesas
st.metric("Saldo no período", f"R$ {saldo:.2f}")

# --- Histórico de transações ---
st.header("📋 Histórico de Transações")
st.dataframe(df_filtrado.sort_values(by="Data", ascending=False))

# --- Gráfico de despesas por categoria ---
st.header("📊 Despesas por Categoria")
despesas = df_filtrado[df_filtrado["Tipo"] == "Despesa"]
if not despesas.empty:
    categorias = despesas.groupby("Categoria")["Valor"].sum()
    fig1, ax1 = plt.subplots()
    ax1.pie(categorias, labels=categorias.index, autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")
    st.pyplot(fig1)
else:
    st.info("Nenhuma despesa nesse período.")

# --- Gráfico de saldo ao longo do tempo ---
st.header("📈 Evolução do Saldo")
if not df_filtrado.empty:
    df_ordenado = df_filtrado.sort_values("Data")
    saldo_acumulado = []
    saldo_temp = 0
    for _, row in df_ordenado.iterrows():
        if row["Tipo"] == "Receita":
            saldo_temp += row["Valor"]
        else:
            saldo_temp -= row["Valor"]
        saldo_acumulado.append(saldo_temp)
    df_ordenado["Saldo"] = saldo_acumulado
    fig2, ax2 = plt.subplots()
    ax2.plot(df_ordenado["Data"], df_ordenado["Saldo"], marker='o')
    ax2.set_title("Evolução do Saldo")
    ax2.set_xlabel("Data")
    ax2.set_ylabel("Saldo (R$)")
    ax2.grid(True)
    st.pyplot(fig2)
else:
    st.info("Sem transações no período selecionado.")
