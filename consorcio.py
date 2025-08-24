import streamlit as st
import pandas as pd

# ---------------- Classe de Consórcio ----------------
class Consorcio:
    def __init__(self, valor_credito, prazo_meses, taxa_adm_anual, fundo_reserva=0.0, seguro=0.0):
        self.valor_credito = valor_credito
        self.prazo_meses = prazo_meses
        self.taxa_adm_anual = taxa_adm_anual / 100
        self.fundo_reserva = fundo_reserva / 100
        self.seguro = seguro

    def calcular(self):
        taxa_total = self.valor_credito * self.taxa_adm_anual * (self.prazo_meses / 12)
        fundo_total = self.valor_credito * self.fundo_reserva
        total_parcelas = self.valor_credito + taxa_total + fundo_total
        parcela_base = total_parcelas / self.prazo_meses
        parcela_final = parcela_base + self.seguro

        parcelas = [round(parcela_final, 2) for _ in range(self.prazo_meses)]

        return {
            "taxa_total": round(taxa_total, 2),
            "fundo_total": round(fundo_total, 2),
            "parcela": round(parcela_final, 2),
            "custo_total": round(parcela_final * self.prazo_meses, 2),
            "parcelas": parcelas
        }

    def simular_lance(self, lance_valor, resultado, tipo="prazo"):
        saldo_devedor = resultado["custo_total"] - lance_valor
        if saldo_devedor < 0:
            saldo_devedor = 0

        if tipo == "prazo":  # Mantém valor da parcela, reduz prazo
            parcelas_restantes = int(saldo_devedor // resultado["parcela"])
            return {
                "tipo": "Prazo",
                "nova_parcela": resultado["parcela"],
                "parcelas_restantes": parcelas_restantes,
                "novo_saldo_devedor": round(saldo_devedor, 2)
            }

        elif tipo == "parcela":  # Mantém prazo, reduz valor da parcela
            if self.prazo_meses > 0:
                nova_parcela = saldo_devedor / self.prazo_meses
            else:
                nova_parcela = 0
            return {
                "tipo": "Parcela",
                "nova_parcela": round(nova_parcela, 2),
                "parcelas_restantes": self.prazo_meses,
                "novo_saldo_devedor": round(saldo_devedor, 2)
            }


# ---------------- Interface Web ----------------
st.set_page_config(page_title="Calculadora de Consórcio", page_icon="💰", layout="centered")
st.title("📊 Calculadora de Consórcio")

# Layout dos inputs
col1, col2 = st.columns(2)

with col1:
    valor_credito = st.number_input("Valor da Carta de Crédito (R$):", min_value=1000.0, step=1000.0, format="%.2f")
    prazo = st.slider("Prazo (meses):", min_value=12, max_value=240, step=12, value=60)
    taxa = st.number_input("Taxa de Administração (% ao ano):", min_value=0.0, step=0.1, format="%.2f")

with col2:
    fundo = st.slider("Fundo de Reserva (% do crédito):", min_value=0.0, max_value=10.0, step=0.1, value=0.0)
    seguro = st.number_input("Seguro Mensal (R$):", min_value=0.0, step=10.0, format="%.2f")

if st.button("📌 Calcular Consórcio"):
    consorcio = Consorcio(valor_credito, prazo, taxa, fundo, seguro)
    resultado = consorcio.calcular()

    # ---------------- Abas ----------------
    tab1, tab2, tab3 = st.tabs(["📋 Resumo", "📑 Parcelas", "💰 Lance"])

    # Resumo
    with tab1:
        colr1, colr2 = st.columns(2)
        with colr1:
            st.metric("Parcela Mensal", f"R$ {resultado['parcela']:.2f}")
            st.metric("Taxa de Administração Total", f"R$ {resultado['taxa_total']:.2f}")
        with colr2:
            st.metric("Custo Total do Consórcio", f"R$ {resultado['custo_total']:.2f}")
            st.metric("Fundo de Reserva Total", f"R$ {resultado['fundo_total']:.2f}")

    # Parcelas
    with tab2:
        df = pd.DataFrame({
            "Nº Parcela": list(range(1, prazo+1)),
            "Valor (R$)": resultado["parcelas"]
        })
        st.dataframe(df, use_container_width=True)

    # Lance
    with tab3:
        lance_valor = st.number_input("Lance ofertado (R$):", min_value=0.0, step=500.0, format="%.2f")
        tipo = st.radio("Tipo de abatimento:", ["Prazo", "Parcela"], horizontal=True)

        if lance_valor > 0:
            resultado_lance = consorcio.simular_lance(lance_valor, resultado, tipo.lower())
            st.success(f"**Simulação ({resultado_lance['tipo']})**")
            st.metric("Nova Parcela", f"R$ {resultado_lance['nova_parcela']:.2f}")
            st.metric("Parcelas Restantes", resultado_lance["parcelas_restantes"])
            st.metric("Novo Saldo Devedor", f"R$ {resultado_lance['novo_saldo_devedor']:.2f}")
