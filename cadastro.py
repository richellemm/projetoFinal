import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import datetime as dt
import sqlite3
import csv


# Função para fechar a janela atual
def fechar_janela(janela):
    janela.destroy()


# Função para voltar à janela anterior
def voltar_janela(janela_atual, janela_anterior):
    janela_atual.destroy()
    janela_anterior.deiconify()


def criar_tabela():
    conn = sqlite3.connect('biblioteca.db')
    c = conn.cursor()
    conn.commit()
    conn.close()

def abrir_cadastro():
    global cadastro_window
    cadastro_window = tk.Toplevel()  # Cria uma nova janela de nível superior para o cadastro
    cadastro_window.title("Cadastro de Livro")

    # TÍTULO DO LIVRO
    label_livro = tk.Label(cadastro_window, text='TÍTULO DO LIVRO')
    label_livro.grid(row=1, column=0, padx=10, pady=10, sticky='nswe', columnspan=4)

    global entry_livro
    entry_livro = tk.Entry(cadastro_window)
    entry_livro.grid(row=2, column=0, padx=10, pady=10, sticky='nswe', columnspan=12)

    # NOME DO AUTOR
    label_autor = tk.Label(cadastro_window, text='NOME DO AUTOR')
    label_autor.grid(row=3, column=0, padx=10, pady=10, sticky='nswe', columnspan=4)

    global entry_autor
    entry_autor = tk.Entry(cadastro_window)
    entry_autor.grid(row=4, column=0, padx=10, pady=10, sticky='nswe', columnspan=12)

    # QUANTIDADE DE EXEMPLARES
    label_qtd = tk.Label(cadastro_window, text='QUANTIDADE DE EXEMPLARES')
    label_qtd.grid(row=5, column=0, padx=10, pady=10, sticky='nswe', columnspan=4)

    global entry_qtd
    entry_qtd = tk.Entry(cadastro_window)
    entry_qtd.grid(row=6, column=0, padx=10, pady=10, sticky='nswe', columnspan=12)

    # BOTÃO CADASTRAR LIVRO
    botao_criar_codigo = tk.Button(cadastro_window, text='Cadastrar Livro', command=cadastrar_livro)
    botao_criar_codigo.grid(row=7, column=0, padx=10, pady=10, sticky='nswe', columnspan=6)

    # BOTÃO FECHAR
    botao_fechar = tk.Button(cadastro_window, text='Fechar', command=lambda: fechar_janela(cadastro_window))
    botao_fechar.grid(row=7, column=4, padx=10, pady=10, sticky='nswe', columnspan=6)

    # Atualizar a função principal ao fechar a janela de cadastro
    cadastro_window.protocol("WM_DELETE_WINDOW", lambda: voltar_janela(cadastro_window, principal))

def cadastrar_livro():
    global entry_livro, entry_autor, entry_qtd  # Tornando as entradas globais
    livro = entry_livro.get()
    autor = entry_autor.get()
    qtd = int(entry_qtd.get())

    # Validação dos dados
    if qtd <= 0:
        messagebox.showerror('Erro', 'Quantidade inválida. Não é possível cadastrar o livro.')
        entry_qtd.delete(0, tk.END)
        return

    if not livro or not autor:
        messagebox.showerror('Erro', 'Por favor, preencha o título e o autor do livro.')
        return

    data_criacao = dt.datetime.now().strftime("%d/%m/%Y %H:%M")
    conn = sqlite3.connect('biblioteca.db')
    c = conn.cursor()
    c.execute("INSERT INTO livros (titulo, autor, quantidade, data_criacao) VALUES (?, ?, ?, ?)",
              (livro, autor, qtd, data_criacao))
    conn.commit()
    conn.close()

    messagebox.showinfo('Sucesso', 'Livro cadastrado com sucesso.')
    limpar_campos() # Limpar campos
    fechar_janela(cadastro_window)


def limpar_campos():
    entry_livro.delete(0, tk.END)
    entry_autor.delete(0, tk.END)
    entry_qtd.delete(0, tk.END)


def pesquisar_livro():
    pesquisa_window = tk.Toplevel()  # Criar uma nova janela para pesquisa
    pesquisa_window.title("Pesquisar Livro")

    # Label e Entry para o termo de pesquisa
    label_pesquisa = tk.Label(pesquisa_window, text="Digite o título do livro ou o autor")
    label_pesquisa.grid(row=0, column=0, padx=10, pady=5)

    entry_pesquisa = tk.Entry(pesquisa_window)
    entry_pesquisa.grid(row=0, column=1, padx=10, pady=5)

    # Botão para iniciar a pesquisa
    botao_pesquisar = tk.Button(pesquisa_window, text="Pesquisar",
                                command=lambda: exibir_resultados(entry_pesquisa.get()))
    botao_pesquisar.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

    # BOTÃO FECHAR
    botao_fechar = tk.Button(pesquisa_window, text='Fechar', command=lambda: fechar_janela(pesquisa_window))
    botao_fechar.grid(row=1, column=4, columnspan=2, padx=10, pady=5)


def exibir_resultados(termo_pesquisa):
    conn = sqlite3.connect('biblioteca.db')
    c = conn.cursor()
    c.execute("SELECT * FROM livros WHERE titulo LIKE ? OR autor LIKE ?",
              ('%' + termo_pesquisa + '%', '%' + termo_pesquisa + '%'))
    resultados = c.fetchall()
    conn.close()

    if not resultados:
        messagebox.showinfo('Informação', 'Nenhum livro encontrado com o termo de pesquisa fornecido.')
        return

    resultados_window = tk.Toplevel()
    resultados_window.title("Resultados da Pesquisa")

    for livro in resultados:
        tk.Label(resultados_window,
                 text=f"Título: {livro[1]}, Autor: {livro[2]}, Quantidade: {livro[3]}, Código: {livro[0]}, Data de Criação: {livro[4]}").pack(
            padx=10, pady=5)

    botao_fechar = tk.Button(resultados_window, text='Fechar', command=lambda: fechar_janela(resultados_window))
    botao_fechar.pack()

def salvar_csv():
    # Abrir uma caixa de diálogo para selecionar o local de salvamento
    filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Arquivos CSV", "*.csv")])
    if filename:
        # Conectar ao banco de dados
        conn = sqlite3.connect('biblioteca.db')
        c = conn.cursor()
        
        # Consultar o banco de dados para obter os dados dos livros
        c.execute("SELECT * FROM livros")
        dados_livros = c.fetchall()
        
        # Escrever os dados CSV no arquivo selecionado
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Código", "Título", "Autor", "Quantidade", "Data de Criação"])
            writer.writerows(dados_livros)

        # Fechar a conexão com o banco de dados
        conn.close()
     
def main_window():
    global principal

    principal = tk.Tk()
    principal.title('Biblioteca')
    
    label_titulo = tk.Label(principal, text="SELECIONE A OPÇÃO DESEJADA")
    label_titulo.pack(pady=10)

    button_cadastrar = tk.Button(principal, text="CADASTRO DE LIVRO", command=abrir_cadastro)
    button_cadastrar.pack(pady=5)

    button_pesquisar = tk.Button(principal, text="PESQUISAR LIVRO", command=pesquisar_livro)
    button_pesquisar.pack(pady=5)

    button_csv = tk.Button(principal, text="BAIXAR LISTA DE LIVROS CADASTRADOS (.csv)", command=salvar_csv)
    button_csv.pack(pady=5)

    principal.mainloop()


# Chamando a função para exibir a janela principal
main_window()
