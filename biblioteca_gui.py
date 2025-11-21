import tkinter as tk
from tkinter import ttk, messagebox
from database import (criar_tabelas,adicionar_livro, listar_livros,adicionar_usuario, listar_usuarios, remover_usuario,emprestar_livro, devolver_livro, listar_emprestimos
)

# Chama a função que cria as tabalas
criar_tabelas()


class BibliotecaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GB - Gerenciamento de Biblioteca")
        self.root.geometry("1000x600")

        self.abas = ttk.Notebook(root)
        self.abas.pack(fill="both", expand=True)

        # abas
        self.frame_livros = ttk.Frame(self.abas)
        self.frame_usuarios = ttk.Frame(self.abas)
        self.frame_emprestimos = ttk.Frame(self.abas)

        self.abas.add(self.frame_livros, text="Livros")
        self.abas.add(self.frame_usuarios, text="Usuários")
        self.abas.add(self.frame_emprestimos, text="Empréstimos")

        # construir interfaces
        self.tela_livros()
        self.tela_usuarios()
        self.tela_emprestimos()


  
    # ------------------ABA DE LIVROS------------------

    def tela_livros(self):
        frame_principal = self.frame_livros

        # campos
        tk.Label(frame_principal, text="Título").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(frame_principal, text="Autor").grid(row=1, column=0, padx=5, pady=5)
        tk.Label(frame_principal, text="Ano").grid(row=2, column=0, padx=5, pady=5)
        tk.Label(frame_principal, text="ISBN").grid(row=3, column=0, padx=5, pady=5)

        self.campo_titulo = tk.Entry(frame_principal, width=40)
        self.campo_autor = tk.Entry(frame_principal, width=40)
        self.campo_ano = tk.Entry(frame_principal, width=40)
        self.campo_isbn = tk.Entry(frame_principal, width=40)

        self.campo_titulo.grid(row=0, column=1)
        self.campo_autor.grid(row=1, column=1)
        self.campo_ano.grid(row=2, column=1)
        self.campo_isbn.grid(row=3, column=1)

        # botões
        tk.Button(frame_principal, text="Cadastrar Livro", command=self.cadastrar_livro).grid(row=4, column=1, pady=10)
        tk.Button(frame_principal, text="Remover Livro", command=self.remover_livro).grid(row=4, column=2, pady=10)
        tk.Button(frame_principal, text="Emprestar", command=self.abrir_popup_emprestar).grid(row=4, column=3, pady=10)
        tk.Button(frame_principal, text="Atualizar Lista", command=self.atualizar_lista_livros).grid(row=4, column=4, pady=10)

        # tabela
        self.tabela_livros = ttk.Treeview(frame_principal, columns=("Título", "Autor", "Ano", "Disponível"), show="headings")
        self.tabela_livros.heading("Título", text="Título")
        self.tabela_livros.heading("Autor", text="Autor")
        self.tabela_livros.heading("Ano", text="Ano")
        self.tabela_livros.heading("Disponível", text="Disponível")

        self.tabela_livros.grid(row=5, column=0, columnspan=5, sticky="nsew")

        # permitir que todas as colunas do frame cresçam para ocupar toda a largura
        frame_principal.rowconfigure(5, weight=1)
        for coluna_indice in range(5):
            frame_principal.columnconfigure(coluna_indice, weight=1)

        # ajustar larguras iniciais das colunas da Treeview para preencher melhor o espaço
        try:
            self.tabela_livros.column("Título", width=400, anchor="w")
            self.tabela_livros.column("Autor", width=250, anchor="w")
            self.tabela_livros.column("Ano", width=80, anchor="center")
            self.tabela_livros.column("Disponível", width=100, anchor="center")
        except Exception:
            pass

        self.atualizar_lista_livros()


    def cadastrar_livro(self):
        # cadastra um novo livro no banco de dados
        titulo = self.campo_titulo.get()
        autor = self.campo_autor.get()
        ano = self.campo_ano.get()

        if not titulo:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        if not autor:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        if not ano:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        try:
            ano = int(ano)
        except ValueError:
            messagebox.showerror("Erro", "Ano deve ser um número.")
            return

        adicionar_livro(titulo, autor, ano)
        messagebox.showinfo("OK", "Livro cadastrado.")
        
        self.campo_titulo.delete(0, tk.END)
        self.campo_autor.delete(0, tk.END)
        self.campo_ano.delete(0, tk.END)
        self.campo_isbn.delete(0, tk.END)
        
        self.atualizar_lista_livros()


    def remover_livro(self):
        # remove um livro selecionado da lista
        linha_selecionada = self.tabela_livros.selection()
        
        if not linha_selecionada:
            messagebox.showinfo("Aviso", "Selecione um livro na lista.")
            return

        item = self.tabela_livros.item(linha_selecionada)
        valores = item["values"]
        
        if len(valores) > 4:
            id_livro = valores[4]
        else:
            id_livro = None

        if id_livro is None:
            messagebox.showerror("Erro", "Não foi possível identificar o livro.")
            return

        messagebox.showinfo("OK", "Funcionalidade de remoção ainda não implementada no banco.")
        self.atualizar_lista_livros()


    def abrir_popup_emprestar(self):
        # abre popup para emprestar um livro selecionado
        linha_selecionada = self.tabela_livros.selection()
        if not linha_selecionada:
            messagebox.showinfo("Aviso", "Selecione um livro na lista.")
            return

        item = self.tabela_livros.item(linha_selecionada)
        titulo_livro = item["values"][0]
        id_livro = item["values"][4] if len(item["values"]) > 4 else None
        disponivel = item["values"][3]

        if disponivel == "Não":
            messagebox.showerror("Erro", "Este livro não está disponível para empréstimo.")
            return

        if id_livro is None:
            messagebox.showerror("Erro", "Não foi possível identificar o livro.")
            return

        popup = tk.Toplevel(self.root)
        popup.title(f"Emprestar - {titulo_livro}")
        popup.geometry("400x300")
        popup.resizable(False, False)

        tk.Label(popup, text="Selecione um usuário para emprestar:", font=("Arial", 10, "bold")).pack(pady=10)

        frame_usuarios = ttk.Frame(popup)
        frame_usuarios.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(frame_usuarios)
        scrollbar.pack(side="right", fill="y")

        listbox_usuarios = tk.Listbox(frame_usuarios, yscrollcommand=scrollbar.set, font=("Arial", 10))
        listbox_usuarios.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox_usuarios.yview)

        usuarios = listar_usuarios()
        dicionario_usuarios = {}
        for id_usuario, nome in usuarios:
            dicionario_usuarios[nome] = id_usuario
            listbox_usuarios.insert(tk.END, nome)

        frame_botoes = ttk.Frame(popup)
        frame_botoes.pack(fill="x", padx=10, pady=10)

        def realizar_emprestimo():
            selection = listbox_usuarios.curselection()
            if not selection:
                messagebox.showwarning("Aviso", "Selecione um usuário.")
                return

            nome_usuario = listbox_usuarios.get(selection[0])
            id_usuario = dicionario_usuarios[nome_usuario]

            operacao_bem_sucedida = emprestar_livro(id_livro, id_usuario)
            if operacao_bem_sucedida:
                messagebox.showinfo("Sucesso", f"Livro '{titulo_livro}' emprestado para {nome_usuario}.")
                popup.destroy()
                self.atualizar_lista_livros()
            else:
                messagebox.showerror("Erro", "Não foi possível realizar o empréstimo.")

        tk.Button(frame_botoes, text="Emprestar", command=realizar_emprestimo, bg="green", fg="white", width=15).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Cancelar", command=popup.destroy, bg="red", fg="white", width=15).pack(side="left", padx=5)


    def atualizar_lista_livros(self):
        # atualiza tabela de livros com dados do banco
        linhas = self.tabela_livros.get_children()
        for linha_indice in linhas:
            self.tabela_livros.delete(linha_indice)

        lista_livros = listar_livros()
        
        # percorre cada livro da lista
        for livro in lista_livros:
            # desempacota os valores do livro
            id_livro = livro[0]
            titulo = livro[1]
            autor = livro[2]
            ano = livro[3]
            disponivel = livro[4]
            
            # verifica se livro está disponível
            if disponivel:
                status_disponibilidade = "Sim"
            else:
                status_disponibilidade = "Não"
            
            # insere a linha na tabela
            self.tabela_livros.insert(
                "", "end",
                values=(titulo, autor, ano, status_disponibilidade, id_livro)
            )


    #---------------- ABA DE USUÁRIOS------------------------

    def tela_usuarios(self):
        frame_principal = self.frame_usuarios

        tk.Label(frame_principal, text="ID do Usuário").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(frame_principal, text="Nome").grid(row=1, column=0, padx=5, pady=5)

        self.campo_usuario_id = tk.Entry(frame_principal, width=40)
        self.campo_usuario_nome = tk.Entry(frame_principal, width=40)

        self.campo_usuario_id.grid(row=0, column=1)
        self.campo_usuario_nome.grid(row=1, column=1)

        tk.Button(frame_principal, text="Cadastrar Usuário", command=self.cadastrar_usuario).grid(row=2, column=1, pady=10)
        tk.Button(frame_principal, text="Atualizar Lista", command=self.atualizar_lista_usuarios).grid(row=2, column=4, sticky="e", padx=10, pady=10)
        tk.Button(frame_principal, text="Excluir Usuário", command=self.excluir_usuario).grid(row=2, column=5, sticky="e", padx=5, pady=10)

        # tabela
        self.tabela_usuarios = ttk.Treeview(frame_principal, columns=("ID", "Nome"), show="headings")
        self.tabela_usuarios.heading("ID", text="ID")
        self.tabela_usuarios.heading("Nome", text="Nome")
        self.tabela_usuarios.grid(row=3, column=0, columnspan=5, sticky="nsew")

        frame_principal.rowconfigure(3, weight=1)
        frame_principal.columnconfigure(4, weight=1)

        self.atualizar_lista_usuarios()


    def cadastrar_usuario(self):
        # Cadastra um novo usuário no banco de dados
        id_usuario = self.campo_usuario_id.get()
        nome = self.campo_usuario_nome.get()

        if not id_usuario:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return
        
        if not nome:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        adicionar_usuario(nome)
        messagebox.showinfo("OK", "Usuário cadastrado.")
        
        self.campo_usuario_id.delete(0, tk.END)
        self.campo_usuario_nome.delete(0, tk.END)
        
        self.atualizar_lista_usuarios()


    def atualizar_lista_usuarios(self):
        # atualiza tabela de usuários com dados do banco
        linhas = self.tabela_usuarios.get_children()
        for linha_indice in linhas:
            self.tabela_usuarios.delete(linha_indice)

        lista_usuarios = listar_usuarios()
        
        for usuario in lista_usuarios:
            id_usuario = usuario[0]
            nome = usuario[1]
            self.tabela_usuarios.insert("", "end", values=(id_usuario, nome))

    def excluir_usuario(self):
        # exclui um usuário selecionado se não houver empréstimos abertos
        linha_selecionada = self.tabela_usuarios.selection()
        
        if not linha_selecionada:
            messagebox.showinfo("Aviso", "Selecione um usuário na lista.")
            return

        item = self.tabela_usuarios.item(linha_selecionada)
        valores_linha = item.get("values", [])
        
        if not valores_linha:
            messagebox.showerror("Erro", "Não foi possível obter os dados do usuário selecionado.")
            return

        # pega a seleção da tabela
        linha_selecionada = self.tabela_usuarios.selection()
        
        # verifica se selecionou alguma coisa
        if not linha_selecionada:
            messagebox.showinfo("Aviso", "Selecione um usuário na lista.")
            return

        # pega o item selecionado
        item = self.tabela_usuarios.item(linha_selecionada)
        
        # pega os valores do item
        valores_linha = item.get("values", [])
        
        # verifica se tem valores
        if not valores_linha:
            messagebox.showerror("Erro", "Não foi possível obter os dados do usuário selecionado.")
            return

        # desempacota os valores
        id_usuario = valores_linha[0]
        
        # verifica se tem nome
        if len(valores_linha) > 1:
            nome = valores_linha[1]
        else:
            nome = str(id_usuario)

        # pergunta se tem certeza
        tem_certeza = messagebox.askyesno("Confirmar", f"Confirma exclusão do usuário '{nome}' (ID: {id_usuario})?")
        
        if not tem_certeza:
            return

        # chama função para remover usuário
        operacao_bem_sucedida, mensagem_resultado = remover_usuario(id_usuario)
        
        # verifica se foi bem sucedido
        if operacao_bem_sucedida:
            messagebox.showinfo("OK", mensagem_resultado)
            self.atualizar_lista_usuarios()
        else:
            messagebox.showerror("Erro", mensagem_resultado)


    #----------------------- ABA DE EMPRÉSTIMOS-------------------------

    def tela_emprestimos(self):
        frame_principal = self.frame_emprestimos

        # frame para busca
        frame_busca = ttk.LabelFrame(frame_principal, text="Buscar Empréstimo", padding=10)
        frame_busca.grid(row=0, column=0, columnspan=6, sticky="ew", padx=5, pady=5)

        tk.Label(frame_busca, text="ID do Empréstimo:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(frame_busca, text="Nome do Usuário:").grid(row=0, column=2, padx=5, pady=5)

        self.campo_id_emprestimo_busca = tk.Entry(frame_busca, width=20)
        self.campo_usuario_nome_busca = tk.Entry(frame_busca, width=20)

        self.campo_id_emprestimo_busca.grid(row=0, column=1, padx=5, pady=5)
        self.campo_usuario_nome_busca.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(frame_busca, text="Procurar", command=self.procurar_emprestimos, fg="black").grid(row=0, column=4, padx=5, pady=5)
        tk.Button(frame_busca, text="Limpar Filtro", command=self.limpar_filtro_emprestimos).grid(row=0, column=5, padx=5, pady=5)
        tk.Button(frame_busca, text="Atualizar Lista", command=self.atualizar_lista_emprestimos, fg="black").grid(row=0, column=6, padx=5, pady=5)
        tk.Button(frame_busca, text="Devolver Selecionado", command=self.devolver_selecionado).grid(row=0, column=7, padx=5, pady=5)

        # tabela
        self.tabela_emprestimos = ttk.Treeview(
            frame_principal,
            columns=("ID", "Livro", "Usuário", "Data Empréstimo", "Devolução"),
            show="headings"
        )
        self.tabela_emprestimos.heading("ID", text="ID")
        self.tabela_emprestimos.heading("Livro", text="Livro")
        self.tabela_emprestimos.heading("Usuário", text="Usuário")
        self.tabela_emprestimos.heading("Data Empréstimo", text="Data Empréstimo")
        self.tabela_emprestimos.heading("Devolução", text="Devolução")

        self.tabela_emprestimos.grid(row=1, column=0, columnspan=6, sticky="nsew")
        frame_principal.rowconfigure(1, weight=1)
        frame_principal.columnconfigure(5, weight=1)

        self.atualizar_lista_emprestimos()


    def procurar_emprestimos(self):
        # obtém o valor do campo de ID de empréstimo
        filtro_id_emprestimo = self.campo_id_emprestimo_busca.get()
        filtro_id_emprestimo = filtro_id_emprestimo.strip()
        
        # obtém o valor do campo de nome de usuário
        filtro_usuario_nome = self.campo_usuario_nome_busca.get()
        filtro_usuario_nome = filtro_usuario_nome.strip()
        filtro_usuario_nome = filtro_usuario_nome.lower()

        # pega todos os itens da tabela
        linhas = self.tabela_emprestimos.get_children()
        
        # percorre cada linha e deleta
        for linha_indice in linhas:
            self.tabela_emprestimos.delete(linha_indice)

        # chama função para obter todos os empréstimos
        lista_emprestimos = listar_emprestimos()
        
        # percorre cada empréstimo da lista
        for emprestimo in lista_emprestimos:
            # desempacota os valores do empréstimo
            id_emprestimo = emprestimo[0]
            titulo_livro = emprestimo[1]
            nome_usuario = emprestimo[2]
            data_emprestimo = emprestimo[3]
            data_devolucao = emprestimo[4]
            
            # verifica se tem filtro de ID
            if filtro_id_emprestimo:
                # converte ID para string
                id_string = str(id_emprestimo)
                # compara com o filtro
                if id_string != filtro_id_emprestimo:
                    # pula este empréstimo
                    continue
            
            # verifica se tem filtro de usuário
            if filtro_usuario_nome:
                # converte nome para minúsculas
                nome_minusculo = nome_usuario.lower()
                # verifica se o filtro está contido no nome
                if filtro_usuario_nome not in nome_minusculo:
                    # pula este empréstimo
                    continue
            
            # verifica se tem data de devolução
            if data_devolucao:
                status_devolucao = data_devolucao
            else:
                status_devolucao = "Pendente"
            
            # insere a linha na tabela
            self.tabela_emprestimos.insert(
                "",
                "end",
                values=(
                    id_emprestimo,
                    titulo_livro,
                    nome_usuario,
                    data_emprestimo,
                    status_devolucao
                )
            )

        # verifica se a lista está vazia
        if not lista_emprestimos:
            messagebox.showinfo("Resultado", "Nenhum empréstimo encontrado com os critérios especificados.")
        else:
            # verifica se tem filtro de ID
            tem_filtro_id = False
            if filtro_id_emprestimo:
                tem_filtro_id = True
            
            # verifica se tem filtro de usuário
            tem_filtro_usuario = False
            if filtro_usuario_nome:
                tem_filtro_usuario = True
            
            # verifica se tem algum filtro ativo
            tem_filtro = tem_filtro_id or tem_filtro_usuario
            
            # verifica se a tabela está vazia
            linhas_tabela = self.tabela_emprestimos.get_children()
            quantidade_linhas = len(linhas_tabela)
            
            if tem_filtro and quantidade_linhas == 0:
                messagebox.showinfo("Resultado", "Nenhum empréstimo encontrado com os critérios especificados.")


    def limpar_filtro_emprestimos(self):
        # limpa os campos de filtro e mostra todos os empréstimos
        self.campo_id_emprestimo_busca.delete(0, tk.END)
        self.campo_usuario_nome_busca.delete(0, tk.END)
        self.atualizar_lista_emprestimos()


    def devolver_selecionado(self):
        # devolve o empréstimo selecionado na tabela de empréstimos
        
        # pega a seleção da tabela
        linha_selecionada = self.tabela_emprestimos.selection()
        
        # verifica se selecionou alguma coisa
        if not linha_selecionada:
            messagebox.showinfo("Aviso", "Selecione um empréstimo na tabela.")
            return

        # pega o item selecionado
        item = self.tabela_emprestimos.item(linha_selecionada)
        
        # pega os valores do item
        valores_linha = item.get("values", [])
        
        # verifica se tem valores
        if not valores_linha:
            messagebox.showerror("Erro", "Não foi possível obter os dados do empréstimo selecionado.")
            return

        # pega o ID do empréstimo
        id_emprestimo = valores_linha[0]
        
        # tenta converter ID para inteiro
        try:
            id_emprestimo_inteiro = int(id_emprestimo)
        except Exception:
            messagebox.showerror("Erro", "ID de empréstimo inválido.")
            return

        # chama função para devolver livro
        operacao_bem_sucedida = devolver_livro(id_emprestimo_inteiro)
        
        # verifica se foi bem sucedido
        if operacao_bem_sucedida:
            messagebox.showinfo("OK", "Livro devolvido com sucesso.")
            self.atualizar_lista_emprestimos()
        else:
            messagebox.showerror("Erro", "Não foi possível registrar a devolução.")


    def atualizar_lista_emprestimos(self):
        # pega todos os itens da tabela
        linhas = self.tabela_emprestimos.get_children()
        
        # percorre cada linha e deleta
        for linha_indice in linhas:
            self.tabela_emprestimos.delete(linha_indice)

        # chama função para obter todos os empréstimos
        lista_emprestimos = listar_emprestimos()
        

        for emprestimo in lista_emprestimos:
            # desempacota os valores do empréstimo
            id_emprestimo = emprestimo[0]
            titulo_livro = emprestimo[1]
            nome_usuario = emprestimo[2]
            data_emprestimo = emprestimo[3]
            data_devolucao = emprestimo[4]
            
            # verifica se tem data de devolução
            if data_devolucao:
                status_devolucao = data_devolucao
            else:
                status_devolucao = "Pendente"
            
            # insere a linha na tabela
            self.tabela_emprestimos.insert(
                "",
                "end",
                values=(
                    id_emprestimo,
                    titulo_livro,
                    nome_usuario,
                    data_emprestimo,
                    status_devolucao
                )
            )


#execução do programa
if __name__ == "__main__":
    root = tk.Tk()
    app = BibliotecaGUI(root)
    root.mainloop()
