# ComprAI

Projeto de estudo pessoal criado para praticar **Python** e explorar a construção de interfaces web com **Streamlit**.

O app é um organizador de compras simples: permite registrar itens e valores, visualizar gastos em gráficos, usar uma calculadora integrada, importar dados de planilhas Excel e gerar relatórios em PDF.

## Propósito

Este repositório não tem fins comerciais — é um espaço de aprendizado para experimentar:

- Estruturação de um app Python com estado (`st.session_state`);
- Manipulação de dados com `pandas`;
- Geração de gráficos com `matplotlib`;
- Leitura de planilhas (`openpyxl`) e geração de PDFs;
- Construção de interfaces interativas com `streamlit`.

## Como rodar

1. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

2. Execute o aplicativo:

   ```bash
   streamlit run organizador_compras_streamlit.py
   ```

3. Acesse o endereço exibido no terminal (geralmente `http://localhost:8501`).

## Funcionalidades

- ➕ Cadastro de compras (nome e valor)
- 📊 Gráficos de gastos (barras e pizza)
- 🧮 Calculadora integrada
- 📥 Importação de compras via arquivo Excel
- 📄 Geração de relatório em PDF
- ⚙️ Exportação dos dados em JSON

## Tecnologias

- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [pandas](https://pandas.pydata.org/)
- [matplotlib](https://matplotlib.org/)
- [openpyxl](https://openpyxl.readthedocs.io/)

## Licença

Este projeto está licenciado sob os termos da licença [MIT](LICENSE).
