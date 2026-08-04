"""
Organizador de Compras - versão Streamlit
-------------------------------------------
Para rodar:
    streamlit run organizador_compras_streamlit.py
"""

import ast
import io
import json
import operator
import os
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "compras_data.json")

st.set_page_config(page_title="Organizador de Compras", page_icon="🛒", layout="wide")


# ---------------- Dados ----------------
def carregar_dados():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []
    return []


def salvar_dados():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.compras, f, ensure_ascii=False, indent=2)


if "compras" not in st.session_state:
    st.session_state.compras = carregar_dados()


def adicionar_compra(nome, valor):
    st.session_state.compras.append(
        {
            "nome": nome,
            "valor": valor,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
    )
    salvar_dados()


def remover_compra(indice):
    del st.session_state.compras[indice]
    salvar_dados()


def editar_compra(indice, nome, valor):
    st.session_state.compras[indice]["nome"] = nome
    st.session_state.compras[indice]["valor"] = valor
    salvar_dados()


def limpar_tudo():
    st.session_state.compras = []
    salvar_dados()


def importar_excel(arquivo):
    """Lê um arquivo Excel (colunas: nome, valor e opcionalmente data) e retorna a lista de compras."""
    df = pd.read_excel(arquivo)
    df.columns = [str(c).strip().lower() for c in df.columns]

    if "nome" not in df.columns or "valor" not in df.columns:
        raise ValueError("O arquivo precisa ter as colunas 'nome' e 'valor'.")

    compras_importadas = []
    for _, linha in df.iterrows():
        nome = str(linha["nome"]).strip()
        valor = float(linha["valor"])

        if "data" in df.columns and pd.notna(linha["data"]):
            data = str(linha["data"]).strip()
        else:
            data = datetime.now().strftime("%d/%m/%Y %H:%M")

        compras_importadas.append({"nome": nome, "valor": valor, "data": data})

    return compras_importadas


def gerar_figura_grafico():
    nomes = [c["nome"] for c in st.session_state.compras]
    valores = [c["valor"] for c in st.session_state.compras]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(nomes, valores, color="#4CAF50")
    ax.set_title("Gastos por item")
    ax.set_ylabel("Valor (R$)")
    ax.set_xlabel("Item")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    return fig


def gerar_pdf_bytes():
    total = sum(c["valor"] for c in st.session_state.compras)
    buffer = io.BytesIO()

    with PdfPages(buffer) as pdf:
        fig_tabela, ax_tabela = plt.subplots(figsize=(8.27, 11.69))  # A4
        ax_tabela.axis("off")
        ax_tabela.set_title("Relatório de Compras", fontsize=16, fontweight="bold", pad=20)

        linhas = [[c["nome"], f'R$ {c["valor"]:.2f}', c["data"]] for c in st.session_state.compras]
        tabela = ax_tabela.table(
            cellText=linhas,
            colLabels=["Item", "Valor", "Data"],
            loc="upper center",
            cellLoc="left",
        )
        tabela.auto_set_font_size(False)
        tabela.set_fontsize(10)
        tabela.scale(1, 1.5)

        ax_tabela.text(
            0.5, 0.05, f"Total gasto: R$ {total:.2f}",
            transform=ax_tabela.transAxes,
            fontsize=13, fontweight="bold", ha="center",
        )

        pdf.savefig(fig_tabela)
        plt.close(fig_tabela)

        fig_grafico = gerar_figura_grafico()
        pdf.savefig(fig_grafico)
        plt.close(fig_grafico)

    buffer.seek(0)
    return buffer


# ---------------- Calculadora ----------------
OPERADORES_PERMITIDOS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calcular_expressao(expressao):
    """Avalia uma expressão matemática simples (+, -, *, /, %, **, parênteses) com segurança."""

    def _avaliar(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPERADORES_PERMITIDOS:
            return OPERADORES_PERMITIDOS[type(node.op)](_avaliar(node.left), _avaliar(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPERADORES_PERMITIDOS:
            return OPERADORES_PERMITIDOS[type(node.op)](_avaliar(node.operand))
        raise ValueError("Expressão inválida.")

    arvore = ast.parse(expressao, mode="eval")
    return _avaliar(arvore.body)


# ---------------- Menu lateral ----------------
st.sidebar.title("🛒 Organizador de Compras")
pagina = st.sidebar.radio(
    "Menu",
    ["➕ Nova Compra", "📊 Gráfico de Gastos", "🧮 Calculadora", "📄 Relatório (PDF)", "⚙️ Configurações"],
)

total_atual = sum(c["valor"] for c in st.session_state.compras)
st.sidebar.markdown("---")
st.sidebar.metric("Total gasto", f"R$ {total_atual:.2f}")
st.sidebar.metric("Itens registrados", len(st.session_state.compras))

st.sidebar.markdown("---")
st.sidebar.subheader("📥 Importar Excel")
arquivo_excel = st.sidebar.file_uploader(
    "Selecione um arquivo Excel (.xlsx)",
    type=["xlsx", "xls"],
    key="upload_excel",
    label_visibility="collapsed",
)
if arquivo_excel is not None:
    try:
        compras_importadas = importar_excel(arquivo_excel)
        st.sidebar.success(f"{len(compras_importadas)} item(ns) encontrado(s) no arquivo.")
        if st.sidebar.button("Confirmar importação", key="confirmar_import_excel", use_container_width=True):
            st.session_state.compras = compras_importadas
            salvar_dados()
            st.sidebar.success("Dados importados com sucesso!")
            st.rerun()
    except (ValueError, KeyError) as erro:
        st.sidebar.error(f"Não foi possível importar: {erro}")
    except Exception:
        st.sidebar.error("Arquivo Excel inválido.")


# ---------------- Página: Nova Compra ----------------
if pagina == "➕ Nova Compra":
    st.title("➕ Adicionar nova compra")
    st.caption("Preencha os campos e pressione Enter (ou clique no botão) para adicionar.")

    valor_padrao = st.session_state.pop("valor_calculado", "")

    with st.form(key="form_add", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            nome = st.text_input("Nome do item")
        with col2:
            valor = st.text_input("Valor (R$)", value=valor_padrao)

        enviado = st.form_submit_button("Adicionar compra", use_container_width=True)

        if enviado:
            nome_limpo = nome.strip()
            valor_limpo = valor.strip().replace(",", ".")

            if not nome_limpo:
                st.warning("Digite o nome do item.")
            else:
                try:
                    valor_float = float(valor_limpo)
                    adicionar_compra(nome_limpo, valor_float)
                    st.success(f"'{nome_limpo}' adicionado com sucesso!")
                except ValueError:
                    st.warning("Digite um valor numérico válido.")

    st.markdown("---")

    if not st.session_state.compras:
        st.info("Nenhuma compra registrada ainda.")
    else:
        st.subheader("Suas compras")

        editando_idx = st.session_state.get("editando_idx")

        for i, compra in enumerate(reversed(st.session_state.compras)):
            indice_real = len(st.session_state.compras) - 1 - i

            if editando_idx == indice_real:
                with st.form(key=f"form_editar_{indice_real}"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        novo_nome = st.text_input("Nome do item", value=compra["nome"])
                    with col2:
                        novo_valor = st.text_input("Valor (R$)", value=f'{compra["valor"]:.2f}')

                    col_salvar, col_cancelar = st.columns(2)
                    salvar = col_salvar.form_submit_button("Salvar", use_container_width=True)
                    cancelar = col_cancelar.form_submit_button("Cancelar", use_container_width=True)

                    if salvar:
                        nome_limpo = novo_nome.strip()
                        valor_limpo = novo_valor.strip().replace(",", ".")
                        if not nome_limpo:
                            st.warning("Digite o nome do item.")
                        else:
                            try:
                                valor_float = float(valor_limpo)
                                editar_compra(indice_real, nome_limpo, valor_float)
                                del st.session_state["editando_idx"]
                                st.success("Item atualizado!")
                                st.rerun()
                            except ValueError:
                                st.warning("Digite um valor numérico válido.")

                    if cancelar:
                        del st.session_state["editando_idx"]
                        st.rerun()
            else:
                col_nome, col_valor, col_data, col_editar, col_remover = st.columns([2.5, 1, 1.5, 0.6, 0.6])
                col_nome.write(compra["nome"])
                col_valor.write(f'R$ {compra["valor"]:.2f}')
                col_data.write(compra["data"])
                if col_editar.button("✏️", key=f"editar_{indice_real}"):
                    st.session_state.editando_idx = indice_real
                    st.rerun()
                if col_remover.button("🗑️", key=f"remover_{indice_real}"):
                    remover_compra(indice_real)
                    st.rerun()

        st.markdown("---")
        st.metric("Total gasto", f"R$ {total_atual:.2f}")


# ---------------- Página: Gráfico ----------------
elif pagina == "📊 Gráfico de Gastos":
    st.title("📊 Gráfico de gastos")

    if not st.session_state.compras:
        st.info("Nenhuma compra registrada ainda.")
    else:
        tipo_grafico = st.radio("Tipo de gráfico", ["Barras", "Pizza"], horizontal=True)

        if tipo_grafico == "Barras":
            fig = gerar_figura_grafico()
            st.pyplot(fig)

            buf_png = io.BytesIO()
            fig.savefig(buf_png, format="png")
            buf_png.seek(0)
            st.download_button("Baixar gráfico (PNG)", data=buf_png, file_name="grafico_compras.png", mime="image/png")
        else:
            fig, ax = plt.subplots(figsize=(7, 7))
            nomes = [c["nome"] for c in st.session_state.compras]
            valores = [c["valor"] for c in st.session_state.compras]
            ax.pie(valores, labels=nomes, autopct="%1.1f%%")
            ax.set_title("Distribuição de gastos")
            st.pyplot(fig)


# ---------------- Página: Calculadora ----------------
elif pagina == "🧮 Calculadora":
    st.title("🧮 Calculadora")
    st.caption("Some, subtraia, multiplique ou divida. Aceita expressões como `12.90 + 5*3`.")

    if "expressao_calc" not in st.session_state:
        st.session_state.expressao_calc = ""

    def _add_ao_visor(texto):
        st.session_state.expressao_calc += texto

    def _limpar_visor():
        st.session_state.expressao_calc = ""

    def _apagar_ultimo():
        st.session_state.expressao_calc = st.session_state.expressao_calc[:-1]

    st.text_input("Expressão", key="expressao_calc", label_visibility="collapsed")

    # mapeia o símbolo exibido no botão para o caractere realmente inserido na expressão
    linhas_botoes = [
        [("7", "7"), ("8", "8"), ("9", "9"), ("÷", "/")],
        [("4", "4"), ("5", "5"), ("6", "6"), ("×", "*")],
        [("1", "1"), ("2", "2"), ("3", "3"), ("−", "-")],
        [("0", "0"), (".", "."), ("%", "%"), ("\\+", "+")],
    ]
    for linha in linhas_botoes:
        cols = st.columns(4)
        for col, (exibido, valor_real) in zip(cols, linha):
            col.button(exibido, on_click=_add_ao_visor, args=(valor_real,), use_container_width=True, key=f"btn_{exibido}")

    col_c, col_apagar, col_igual = st.columns(3)
    col_c.button("C", on_click=_limpar_visor, use_container_width=True)
    col_apagar.button("⌫", on_click=_apagar_ultimo, use_container_width=True)
    calcular = col_igual.button("=", type="primary", use_container_width=True)

    if calcular:
        try:
            resultado = calcular_expressao(st.session_state.expressao_calc)
            st.session_state.resultado_calc = resultado
        except (ValueError, SyntaxError, ZeroDivisionError, TypeError):
            st.session_state.resultado_calc = None
            st.error("Expressão inválida.")

    if st.session_state.get("resultado_calc") is not None:
        st.metric("Resultado", f"{st.session_state.resultado_calc:.2f}")

        if st.button("Usar este valor em uma nova compra"):
            st.session_state.valor_calculado = f"{st.session_state.resultado_calc:.2f}"
            st.success("Valor pronto! Vá até '➕ Nova Compra' para concluir.")


# ---------------- Página: Relatório PDF ----------------
elif pagina == "📄 Relatório (PDF)":
    st.title("📄 Gerar relatório em PDF")

    if not st.session_state.compras:
        st.info("Nenhuma compra registrada ainda.")
    else:
        st.write("O relatório inclui a lista completa das compras, o total gasto e o gráfico de barras.")
        pdf_buffer = gerar_pdf_bytes()
        st.download_button(
            "Baixar relatório em PDF",
            data=pdf_buffer,
            file_name="relatorio_compras.pdf",
            mime="application/pdf",
        )


# ---------------- Página: Configurações ----------------
elif pagina == "⚙️ Configurações":
    st.title("⚙️ Configurações")

    st.caption("A importação de dados agora é feita por Excel, através do botão na barra lateral.")

    st.markdown("---")
    st.subheader("Zona de risco")
    if st.button("🗑️ Limpar todas as compras", type="primary"):
        limpar_tudo()
        st.success("Todas as compras foram removidas.")
        st.rerun()
