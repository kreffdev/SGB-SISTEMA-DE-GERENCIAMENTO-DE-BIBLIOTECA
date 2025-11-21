
from dataclasses import dataclass, asdict
from datetime import datetime
import os
import sys
import json
from typing import Optional, List, Dict

if getattr(sys, 'frozen', False):
    diretorio_programa = os.path.dirname(sys.executable)
else:
    diretorio_programa = os.path.dirname(os.path.abspath(__file__))

# Garante que o diretório existe
os.makedirs(diretorio_programa, exist_ok=True)

NOME_ARQUIVO_DADOS = os.path.join(diretorio_programa, "biblioteca_data.json")

# Garante que o diretório existe
os.makedirs(diretorio_programa, exist_ok=True)

NOME_BANCO_DADOS = os.path.join(diretorio_programa, "biblioteca.db")


@dataclass
class Livro:
    titulo: str
    autor: str
    ano: int
    isbn: str
    disponivel: bool = True

    def para_dicionario(self):
        return asdict(self)

    @staticmethod
    def do_dicionario(d):
        return Livro(
            titulo=d["titulo"],
            autor=d["autor"],
            ano=int(d["ano"]),
            isbn=d["isbn"],
            disponivel=bool(d.get("disponivel", True))
        )


@dataclass
class Usuario:
    usuario_id: str  # pode ser CPF, email ou id simples
    nome: str

    def para_dicionario(self):
        return asdict(self)


@dataclass
class Emprestimo:
    isbn: str
    usuario_id: str
    data_emprestimo: str  # ISO format
    data_devolucao: Optional[str] = None

    def para_dicionario(self):
        return asdict(self)


class Biblioteca:
    def __init__(self):
        self.livros: Dict[str, Livro] = {}        # chave = isbn
        self.usuarios: Dict[str, Usuario] = {}    # chave = usuario_id
        self.emprestimos: List[Emprestimo] = []   # histórico de empréstimos

    # ---------------CRUD Livros--------------------
    def adicionar_livro(self, livro: Livro) -> bool:
        if livro.isbn in self.livros:
            return False
        self.livros[livro.isbn] = livro
        return True

    def remover_livro(self, isbn: str) -> bool:
        livro = self.livros.get(isbn)
        if not livro:
            return False
        if not livro.disponivel:
            return False  
        del self.livros[isbn]
        return True

    def buscar_por_isbn(self, isbn: str) -> Optional[Livro]:
        return self.livros.get(isbn)

    def buscar_por_titulo(self, termo: str) -> List[Livro]:
        # busca livros por termo no título 
        termo_lower = termo.lower()
        resultados = []
        for livro in self.livros.values():
            titulo_lower = livro.titulo.lower()
            if termo_lower in titulo_lower:
                resultados.append(livro)
        return resultados

    def buscar_por_autor(self, termo: str) -> List[Livro]:
        # busca livros por termo no autor 
        termo_lower = termo.lower()
        resultados = []
        for livro in self.livros.values():
            autor_lower = livro.autor.lower()
            if termo_lower in autor_lower:
                resultados.append(livro)
        return resultados

    def listar_todos(self) -> List[Livro]:
        return list(self.livros.values())

    def listar_disponiveis(self) -> List[Livro]:
        # retorna lista de livros disponíveis para empréstimo
        livros_disponiveis = []
        for livro in self.livros.values():
            if livro.disponivel:
                livros_disponiveis.append(livro)
        return livros_disponiveis

    # -------------Usuários-----------------------------
    def cadastrar_usuario(self, usuario: Usuario) -> bool:
        if usuario.usuario_id in self.usuarios:
            return False
        self.usuarios[usuario.usuario_id] = usuario
        return True

    def buscar_usuario(self, usuario_id: str) -> Optional[Usuario]:
        return self.usuarios.get(usuario_id)

    # -----------------Empréstimos-----------------------------
    def emprestar(self, isbn: str, usuario_id: str) -> tuple[bool, str]:
        livro = self.buscar_por_isbn(isbn)
        if not livro:
            return False, "Livro não encontrado."
        if not livro.disponivel:
            return False, "Livro já está emprestado."
        usuario = self.buscar_usuario(usuario_id)
        if not usuario:
            return False, "Usuário não encontrado."

        # marcar como emprestado
        livro.disponivel = False
        emprestimo = Emprestimo(
            isbn=isbn,
            usuario_id=usuario_id,
            data_emprestimo=datetime.now().isoformat()
        )
        self.emprestimos.append(emprestimo)
        return True, "Empréstimo realizado com sucesso."

    def devolver(self, isbn: str, usuario_id: str) -> tuple[bool, str]:
        livro = self.buscar_por_isbn(isbn)
        if not livro:
            return False, "Livro não encontrado."
        if livro.disponivel:
            return False, "Livro já está disponível (não parece estar emprestado)."

        # encontrar empréstimo aberto
        for emprestimo in reversed(self.emprestimos):  # percorre do mais recente
            if emprestimo.isbn == isbn and emprestimo.usuario_id == usuario_id and emprestimo.data_devolucao is None:
                emprestimo.data_devolucao = datetime.now().isoformat()
                livro.disponivel = True
                return True, "Devolução registrada com sucesso."
        return False, "Empréstimo correspondente não encontrado."

    # --------------------------Persistência -----------------
    def salvar_em_arquivo(self, caminho: str = NOME_ARQUIVO_DADOS):
        # Persiste dados em arquivo JSON
        dados_serializados = {}
        
        livros_dicionario = []
        for livro in self.livros.values():
            livro_convertido = livro.para_dicionario()
            livros_dicionario.append(livro_convertido)
        dados_serializados["livros"] = livros_dicionario
        
        usuarios_dicionario = []
        for usuario in self.usuarios.values():
            usuario_convertido = usuario.para_dicionario()
            usuarios_dicionario.append(usuario_convertido)
        dados_serializados["usuarios"] = usuarios_dicionario
        
        emprestimos_dicionario = []
        for emprestimo in self.emprestimos:
            emprestimo_convertido = emprestimo.para_dicionario()
            emprestimos_dicionario.append(emprestimo_convertido)
        dados_serializados["emprestimos"] = emprestimos_dicionario
        
        arquivo = open(caminho, "w", encoding="utf-8")
        json.dump(dados_serializados, arquivo, ensure_ascii=False, indent=2)
        arquivo.close()

    def carregar_de_arquivo(self, caminho: str = NOME_ARQUIVO_DADOS):
        # Carrega dados do arquivo JSON
        try:
            arquivo = open(caminho, "r", encoding="utf-8")
            data = json.load(arquivo)
            arquivo.close()
            
            livros_carregados = {}
            for d in data.get("livros", []):
                livro_objeto = Livro.do_dicionario(d)
                livros_carregados[d["isbn"]] = livro_objeto
            self.livros = livros_carregados
            
            usuarios_carregados = {}
            for d in data.get("usuarios", []):
                usuario_objeto = Usuario.do_dicionario(d)
                usuarios_carregados[d["usuario_id"]] = usuario_objeto
            self.usuarios = usuarios_carregados
            
            emprestimos_carregados = []
            for d in data.get("emprestimos", []):
                emprestimo_objeto = Emprestimo.do_dicionario(d)
                emprestimos_carregados.append(emprestimo_objeto)
            self.emprestimos = emprestimos_carregados
            
            return True
        except FileNotFoundError:
            return False

    # ----------------Relatórios simples-----------------------
    def relatorio_emprestimos_abertos(self) -> List[Emprestimo]:
        return [e for e in self.emprestimos if e.data_devolucao is None]


# ---------------------------Interface de Texto (Menu)-----------------------
def menu():
    biblioteca = Biblioteca()
    biblioteca.carregar_de_arquivo()  # tenta carregar dados existentes

    def input_int(prompt, default=None):
        try:
            valor = input(prompt)
            if valor.strip() == "" and default is not None:
                return default
            return int(valor)
        except ValueError:
            return None

    while True:
        print("\n=== Biblioteca ===")
        print("1 - Cadastrar livro")
        print("2 - Remover livro")
        print("3 - Buscar livro (ISBN)")
        print("4 - Buscar por título")
        print("5 - Buscar por autor")
        print("6 - Listar todos os livros")
        print("7 - Listar livros disponíveis")
        print("8 - Cadastrar usuário")
        print("9 - Emprestar livro")
        print("10 - Devolver livro")
        print("11 - Relatório: empréstimos abertos")
        print("12 - Salvar dados")
        print("0 - Sair")
        opcao_escolhida = input("Escolha uma opção: ").strip()

        if opcao_escolhida == "1":
            titulo = input("Título: ").strip()
            autor = input("Autor: ").strip()
            ano = input_int("Ano: ")
            isbn = input("ISBN: ").strip()
            if not titulo or not autor or not ano or not isbn:
                print("Dados incompletos.")
                continue
            livro = Livro(titulo=titulo, autor=autor, ano=ano, isbn=isbn)
            ok = biblioteca.adicionar_livro(livro)
            print("Livro cadastrado." if ok else "ISBN já cadastrado.")

        elif opcao_escolhida == "2":
            isbn = input("ISBN do livro a remover: ").strip()
            ok = biblioteca.remover_livro(isbn)
            if ok:
                print("Livro removido.")
            else:
                print("Não foi possível remover (não existe ou está emprestado).")

        elif opcao_escolhida == "3":
            isbn = input("ISBN: ").strip()
            l = biblioteca.buscar_por_isbn(isbn)
            if l:
                print(f"{l.titulo} — {l.autor} ({l.ano}) — {'Disponível' if l.disponivel else 'Emprestado'}")
            else:
                print("Livro não encontrado.")

        elif opcao_escolhida == "4":
            termo = input("Termo no título: ").strip()
            res = biblioteca.buscar_por_titulo(termo)
            if res:
                for l in res:
                    print(f"{l.isbn} | {l.titulo} — {l.autor} ({l.ano}) — {'Disponível' if l.disponivel else 'Emprestado'}")
            else:
                print("Nenhum livro encontrado com esse termo no título.")

        elif opcao_escolhida == "5":
            termo = input("Termo no autor: ").strip()
            res = biblioteca.buscar_por_autor(termo)
            if res:
                for l in res:
                    print(f"{l.isbn} | {l.titulo} — {l.autor} ({l.ano}) — {'Disponível' if l.disponivel else 'Emprestado'}")
            else:
                print("Nenhum livro encontrado com esse termo no autor.")

        elif opcao_escolhida == "6":
            todos = biblioteca.listar_todos()
            if not todos:
                print("Nenhum livro cadastrado.")
            else:
                for l in todos:
                    print(f"{l.isbn} | {l.titulo} — {l.autor} ({l.ano}) — {'Disponível' if l.disponivel else 'Emprestado'}")

        elif opcao_escolhida == "7":
            disponiveis = biblioteca.listar_disponiveis()
            if not disponiveis:
                print("Nenhum livro disponível no momento.")
            else:
                for l in disponiveis:
                    print(f"{l.isbn} | {l.titulo} — {l.autor} ({l.ano})")

        elif opcao_escolhida == "8":
            user_id = input("ID do usuário (ex: email ou matrícula): ").strip()
            nome = input("Nome do usuário: ").strip()
            if not user_id or not nome:
                print("Dados incompletos.")
                continue
            user = Usuario(usuario_id=user_id, nome=nome)
            ok = biblioteca.cadastrar_usuario(user)
            print("Usuário cadastrado." if ok else "ID de usuário já existe.")

        elif opcao_escolhida == "9":
            isbn = input("ISBN do livro a emprestar: ").strip()
            user_id = input("ID do usuário: ").strip()
            ok, msg = biblioteca.emprestar(isbn, user_id)
            print(msg)

        elif opcao_escolhida == "10":
            isbn = input("ISBN do livro a devolver: ").strip()
            user_id = input("ID do usuário que devolve: ").strip()
            ok, msg = biblioteca.devolver(isbn, user_id)
            print(msg)

        elif opcao_escolhida == "11":
            abertos = biblioteca.relatorio_emprestimos_abertos()
            if not abertos:
                print("Nenhum empréstimo em aberto.")
            else:
                for e in abertos:
                    livro = biblioteca.buscar_por_isbn(e.isbn)
                    usuario = biblioteca.buscar_usuario(e.usuario_id)
                    titulo = livro.titulo if livro else "(desconhecido)"
                    nome_u = usuario.nome if usuario else e.usuario_id
                    print(f"ISBN: {e.isbn} | Título: {titulo} | Usuário: {nome_u} | Empréstimo: {e.data_emprestimo}")

        elif opcao_escolhida == "12":
            biblioteca.salvar_em_arquivo()
            print(f"Dados salvos em '{NOME_ARQUIVO_DADOS}'.")

        elif opcao_escolhida == "0":
            salvar = input("Deseja salvar antes de sair? (s/n) [s]: ").strip().lower() or "s"
            if salvar == "s":
                biblioteca.salvar_em_arquivo()
                print(f"Dados salvos em '{NOME_ARQUIVO_DADOS}'.")
            print("Saindo...")
            break

        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu()