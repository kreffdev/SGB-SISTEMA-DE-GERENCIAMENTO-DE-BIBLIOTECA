# ----------------------Funções utilitárias para SQL---------------------------------
def executar_sql(sql, parametros=()):
    #Executa comandos SQL que modificam dados (INSERT, UPDATE, DELETE)
    conexao = conectar()
    cursor_banco = conexao.cursor()
    cursor_banco.execute(sql, parametros)
    conexao.commit()
    conexao.close()

def consultar_sql(sql, parametros=()):
    #Executa comandos SQL de consulta e retorna os resultados
    conexao = conectar()
    cursor_banco = conexao.cursor()
    cursor_banco.execute(sql, parametros)
    resultado = cursor_banco.fetchall()
    conexao.close()
    return resultado
import sqlite3
from datetime import datetime
import os
import sys

# Obtém o caminho do diretório onde o programa está instalado resolve problemas de duplicidade de base de dados

if getattr(sys, 'frozen', False):
    # Executado como executável (.exe)
    diretorio_programa = os.path.dirname(sys.executable)
else:
    # Executado como script Python caso não seja um .exe
    diretorio_programa = os.path.dirname(os.path.abspath(__file__))

NOME_BANCO_DADOS = os.path.join(diretorio_programa, "biblioteca.db")

def conectar():
    conexao = sqlite3.connect(NOME_BANCO_DADOS, timeout=10.0)
    conexao.execute("PRAGMA journal_mode = WAL")
    return conexao


#------------------- CRIAÇÃO DAS TABELAS------------------------------------

def criar_tabelas():
    executar_sql("""
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            ano INTEGER,
            disponivel INTEGER DEFAULT 1
        );
    """)
    executar_sql("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        );
    """)
    executar_sql("""
        CREATE TABLE IF NOT EXISTS emprestimos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            livro_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            data_emprestimo TEXT NOT NULL,
            data_devolucao TEXT,
            FOREIGN KEY(livro_id) REFERENCES livros(id),
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        );
    """)


# ----------------------FUNÇÕES de LIVROS----------------------------------

def adicionar_livro(titulo, autor, ano):
    executar_sql(
        "INSERT INTO livros (titulo, autor, ano, disponivel) VALUES (?, ?, ?, 1)",
        (titulo, autor, ano)
    )

def listar_livros():
    # lista de todos os livros cadastrados
    return consultar_sql("SELECT * FROM livros")

def buscar_livro_por_titulo(titulo):
    return consultar_sql(
        "SELECT * FROM livros WHERE titulo LIKE ?",
        ('%' + titulo + '%',)
    )

def alterar_disponibilidade(id_livro, disponivel):
    executar_sql(
        "UPDATE livros SET disponivel=? WHERE id=?",
        (disponivel, id_livro)
    )


# ----------------FUNÇÕES USUÁRIOS----------------------------------

def adicionar_usuario(nome):
    executar_sql("INSERT INTO usuarios (nome) VALUES (?)", (nome,))

def listar_usuarios():
    # retorna lista de todos os usuários cadastrados
    return consultar_sql("SELECT * FROM usuarios")


def remover_usuario(id_usuario):
    # remove usuário se não tiver empréstimos em aberto, retorna (ok, mensagem)
    try:
        resultado = consultar_sql("SELECT COUNT(*) FROM emprestimos WHERE usuario_id=? AND data_devolucao IS NULL", (id_usuario,))
        quantidade_emprestimos_abertos = resultado[0][0] if resultado else 0
        if quantidade_emprestimos_abertos > 0:
            return False, "Usuário possui empréstimos em aberto."

        executar_sql("DELETE FROM usuarios WHERE id=?", (id_usuario,))
        return True, "Usuário removido com sucesso."
    except Exception as erro:
        return False, str(erro)


#--------------------- FUNÇÕES EMPRÉSTIMOS--------------------

def emprestar_livro(id_livro, id_usuario):
    # registra empréstimo de um livro para um usuário
    try:
        resultado = consultar_sql("SELECT disponivel FROM livros WHERE id=?", (id_livro,))
        status_livro = resultado[0] if resultado else None
        if not status_livro or status_livro[0] == 0:
            return False

        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M")
        executar_sql("""
            INSERT INTO emprestimos (livro_id, usuario_id, data_emprestimo)
            VALUES (?, ?, ?)
        """, (id_livro, id_usuario, data_atual))

        executar_sql("UPDATE livros SET disponivel=? WHERE id=?", (0, id_livro))
        return True
    except Exception as erro:
        print(f"Erro ao emprestar livro: {erro}")
        return False

def devolver_livro(id_emprestimo):
    # registra devolução de um livro emprestado
    try:
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M")

        resultado = consultar_sql("SELECT livro_id FROM emprestimos WHERE id=?", (id_emprestimo,))
        if not resultado:
            return False
        id_livro = resultado[0][0]

        executar_sql("UPDATE emprestimos SET data_devolucao=? WHERE id=?", (data_atual, id_emprestimo))
        executar_sql("UPDATE livros SET disponivel=? WHERE id=?", (1, id_livro))
        return True
    except Exception as erro:
        print(f"Erro ao devolver livro: {erro}")
        return False

def listar_emprestimos():
    # retorna lista de todos os empréstimos com dados de livro e usuário
    return consultar_sql("""
        SELECT e.id, l.titulo, u.nome, e.data_emprestimo, e.data_devolucao
        FROM emprestimos e
        JOIN livros l ON l.id = e.livro_id
        JOIN usuarios u ON u.id = e.usuario_id
    """)


if __name__ == "__main__":
    criar_tabelas()

