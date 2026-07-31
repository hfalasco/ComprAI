"""
Organizador de Compras
-----------------------
Aplicativo simples com interface gráfica para registrar compras (nome + valor),
salvar os dados, gerar um relatório em PDF com a lista e o total, e exibir
um gráfico de barras com os gastos.
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "compras_data.json")


class OrganizadorCompras:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizador de Compras")
        self.root.geometry("520x560")
        self.root.resizable(False, False)

        self.compras = self.carregar_dados()

        self._montar_interface()
        self._atualizar_lista()

    # ---------------- Dados ----------------
    def carregar_dados(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def salvar_dados(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.compras, f, ensure_ascii=False, indent=2)

    # ---------------- Interface ----------------
    def _montar_interface(self):
        titulo = tk.Label(self.root, text="Organizador de Compras", font=("Segoe UI", 16, "bold"))
        titulo.pack(pady=10)

        form = tk.Frame(self.root)
        form.pack(pady=5)

        tk.Label(form, text="Nome do item:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_nome = tk.Entry(form, width=30)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="Valor (R$):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_valor = tk.Entry(form, width=30)
        self.entry_valor.grid(row=1, column=1, padx=5, pady=5)

        btn_adicionar = tk.Button(self.root, text="Adicionar compra", command=self.adicionar_compra, bg="#4CAF50", fg="white")
        btn_adicionar.pack(pady=8)

        # Lista de compras
        lista_frame = tk.Frame(self.root)
        lista_frame.pack(pady=5, fill="both", expand=False)

        colunas = ("nome", "valor", "data")
        self.tree = ttk.Treeview(lista_frame, columns=colunas, show="headings", height=10)
        self.tree.heading("nome", text="Item")
        self.tree.heading("valor", text="Valor (R$)")
        self.tree.heading("data", text="Data")
        self.tree.column("nome", width=220)
        self.tree.column("valor", width=100, anchor="e")
        self.tree.column("data", width=140, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0))

        scrollbar = ttk.Scrollbar(lista_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 10))

        self.label_total = tk.Label(self.root, text="Total: R$ 0,00", font=("Segoe UI", 13, "bold"))
        self.label_total.pack(pady=8)

        botoes = tk.Frame(self.root)
        botoes.pack(pady=5)

        tk.Button(botoes, text="Remover selecionado", command=self.remover_compra).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(botoes, text="Limpar tudo", command=self.limpar_tudo).grid(row=0, column=1, padx=5, pady=5)

        botoes2 = tk.Frame(self.root)
        botoes2.pack(pady=5)

        tk.Button(botoes2, text="Ver gráfico de gastos", command=self.mostrar_grafico, bg="#2196F3", fg="white").grid(row=0, column=0, padx=5, pady=5)
        tk.Button(botoes2, text="Gerar PDF", command=self.gerar_pdf, bg="#FF9800", fg="white").grid(row=0, column=1, padx=5, pady=5)

    # ---------------- Ações ----------------
    def adicionar_compra(self):
        nome = self.entry_nome.get().strip()
        valor_texto = self.entry_valor.get().strip().replace(",", ".")

        if not nome:
            messagebox.showwarning("Atenção", "Digite o nome do item.")
            return

        try:
            valor = float(valor_texto)
        except ValueError:
            messagebox.showwarning("Atenção", "Digite um valor numérico válido.")
            return

        compra = {
            "nome": nome,
            "valor": valor,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
        self.compras.append(compra)
        self.salvar_dados()
        self._atualizar_lista()

        self.entry_nome.delete(0, tk.END)
        self.entry_valor.delete(0, tk.END)
        self.entry_nome.focus()

    def remover_compra(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showinfo("Info", "Selecione um item para remover.")
            return

        indice = self.tree.index(selecionado[0])
        del self.compras[indice]
        self.salvar_dados()
        self._atualizar_lista()

    def limpar_tudo(self):
        if not self.compras:
            return
        if messagebox.askyesno("Confirmar", "Deseja apagar todas as compras registradas?"):
            self.compras = []
            self.salvar_dados()
            self._atualizar_lista()

    def _atualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        total = 0.0
        for compra in self.compras:
            self.tree.insert("", "end", values=(compra["nome"], f'{compra["valor"]:.2f}', compra["data"]))
            total += compra["valor"]

        self.label_total.config(text=f"Total: R$ {total:.2f}")

    # ---------------- Gráfico ----------------
    def _gerar_figura_grafico(self):
        nomes = [c["nome"] for c in self.compras]
        valores = [c["valor"] for c in self.compras]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(nomes, valores, color="#4CAF50")
        ax.set_title("Gastos por item")
        ax.set_ylabel("Valor (R$)")
        ax.set_xlabel("Item")
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        fig.tight_layout()
        return fig

    def mostrar_grafico(self):
        if not self.compras:
            messagebox.showinfo("Info", "Nenhuma compra registrada ainda.")
            return

        fig = self._gerar_figura_grafico()

        janela = tk.Toplevel(self.root)
        janela.title("Gráfico de gastos")

        canvas = FigureCanvasTkAgg(fig, master=janela)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        def salvar_png():
            caminho = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("Imagem PNG", "*.png")],
                initialfile="grafico_compras.png",
                initialdir=os.path.join(os.path.expanduser("~"), "Desktop"),
            )
            if caminho:
                fig.savefig(caminho)
                messagebox.showinfo("Sucesso", f"Gráfico salvo em:\n{caminho}")

        tk.Button(janela, text="Salvar como PNG", command=salvar_png, bg="#2196F3", fg="white").pack(pady=8)

    # ---------------- PDF ----------------
    def gerar_pdf(self):
        if not self.compras:
            messagebox.showinfo("Info", "Nenhuma compra registrada ainda.")
            return

        caminho = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Arquivo PDF", "*.pdf")],
            initialfile="relatorio_compras.pdf",
            initialdir=os.path.join(os.path.expanduser("~"), "Desktop"),
        )
        if not caminho:
            return

        total = sum(c["valor"] for c in self.compras)

        with PdfPages(caminho) as pdf:
            # Página 1: lista de compras em formato de tabela
            fig_tabela, ax_tabela = plt.subplots(figsize=(8.27, 11.69))  # tamanho A4
            ax_tabela.axis("off")
            ax_tabela.set_title("Relatório de Compras", fontsize=16, fontweight="bold", pad=20)

            linhas = [[c["nome"], f'R$ {c["valor"]:.2f}', c["data"]] for c in self.compras]
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

            # Página 2: gráfico de barras
            fig_grafico = self._gerar_figura_grafico()
            pdf.savefig(fig_grafico)
            plt.close(fig_grafico)

        messagebox.showinfo("Sucesso", f"PDF gerado em:\n{caminho}")


def main():
    root = tk.Tk()
    app = OrganizadorCompras(root)
    root.mainloop()


if __name__ == "__main__":
    main()
