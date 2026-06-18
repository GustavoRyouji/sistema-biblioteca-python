from sistema.interface import *
from sistema.livro import *
from sistema.clientes import *
import time
from datetime import date

def emprestarLivros(conexao):
    while True:
        cabeçalho('CLIENTE')
        cliente = input('Digite o nome ou CPF do cliente (0 para cancelar): ')
        if cliente == '0':
            print('Empréstimo Cancelado.')
            return
        if cliente.isnumeric():
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM clientes WHERE CPF = ?", (cliente,))
            busca = cursor.fetchone()
            if busca is None:
                print('Cliente não encontrado.')
                continue
            cabeçalho('CLIENTE')
            mostrarcliente([busca])
        else:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM clientes WHERE Nome LIKE ?", 
                           (f"%{cliente}%",))
            nome = cursor.fetchall()
            if not nome:
                print('Cliente não encontrado.')
                continue
            mostrarcliente(nome)
            id = leiaInt('Digite o ID do cliente desejado: ')
            cursor.execute("SELECT * FROM clientes WHERE id = ?", 
                           (id,))
            busca = cursor.fetchone()
            if busca is None:
                print('Cliente não encontrado.')
                continue
            cabeçalho('CLIENTE')
            mostrarcliente([busca])
        time.sleep(2)
        cabeçalho('LIVRO')
        livro = input('Digite o título do livro (0 para cancelar): ')
        if livro == '0':
            print('Empréstimo Cancelado.')
            return
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM livros WHERE Título LIKE ?", (f"%{livro}%",))
        bu = cursor.fetchall()
        if not bu:
            print('Livro não encontrado.')
            continue
        cabeçalho('LIVRO')
        mostrarLivros(bu)
        id_livro = leiaInt('Digite o ID do livro desejado: ')
        cursor.execute("SELECT * FROM livros WHERE id = ?", 
                           (id_livro,))
        bus = cursor.fetchone()
        if bus is None:
            print('livro não encontrado.')
            continue
        cabeçalho('CLIENTE')
        mostrarcliente([busca])
        cabeçalho('LIVRO')
        mostrarLivros([bus])
        
        res = retornar(['Continuar','Modificar dados' ], 'Os dados estão corretos?')
        if res == 1:
            cursor.execute("""INSERT INTO emprestimos (
                        id_clientes, id_livros, data_emprestimo, status) VALUES (?, ?, ?, ?)""",
                        (busca[0], bus[0], date.today(), 'Ativo'))
            cursor.execute("UPDATE livros SET Quantidade = Quantidade - 1 WHERE id = ?",
                            (bus[0],))
            conexao.commit()
            print('Empréstimo criado com sucesso.')
            break


def listarEmprestimo(conexao):
    cabeçalho('LISTA DE EMPRÉSTIMOS')
    cursor = conexao.cursor()
    cursor.execute("""SELECT emprestimos.id, clientes.Nome, livros.Título,
                   emprestimos.data_emprestimo, emprestimos.status
                   FROM emprestimos
                   JOIN clientes ON emprestimos.id_clientes = clientes.id
                   JOIN livros ON emprestimos.id_livros = livros.id""")
    resultado = cursor.fetchall()
    mostrarEmprestimo(resultado)


def mostrarEmprestimo(emprestimo):
    print('-' * 90)
    print(f'{"ID":<5} {"Cliente":<30} {"Título":<28} {"  Data":<15} {"Status":<14}')
    print('-' * 90)
    for emp in emprestimo:
        nome = emp[2][:20] + '..' if len(emp[2]) > 20 else emp[2]
        print(f'{emp[0]:<5} {emp[1]:<30} {nome:<28} {str(emp[3]):<15} {emp[4]:<14}')
        print('-' * 90)

def devolverLivro(conexao):
    while True:
        cabeçalho('DEVOLUÇÃO')
        listarEmprestimo(conexao)
        id = leiaInt('Digite o ID do Empréstimo: ')
        cursor = conexao.cursor()
        cursor.execute("""
                SELECT emprestimos.id, clientes.Nome, livros.Título,
                emprestimos.data_emprestimo, emprestimos.status,
                emprestimos.id_livros
                FROM emprestimos
                JOIN clientes ON emprestimos.id_clientes = clientes.id
                JOIN livros ON emprestimos.id_livros = livros.id
                WHERE emprestimos.id = ?""", (id,))
        busca = cursor.fetchone()
        if not busca:
            print('ID de empréstimo não encontrado.')
            return
        mostrarEmprestimo([busca])
        data_emp = date.fromisoformat(busca[3])
        hoje = date.today()
        dias = (hoje - data_emp).days
        res = retornar(['Livro Devolvido', 'Livro danificado'], 'Livro Devolvido?')
        if res == 1:
            cursor.execute("""UPDATE emprestimos 
                SET data_devolucao = ?, status = 'Devolvido'
                WHERE id = ?""", (hoje, id))
            cursor.execute("UPDATE livros SET Quantidade = Quantidade + 1 WHERE id = ?", (busca[5],))
            
            prazo = 7  
            if dias > prazo:
                atraso = dias - prazo
                multa = atraso * 2.50 
                print(f'Multa: R${multa:.2f}')        

        elif res == 2:
            cursor.execute("""UPDATE emprestimos 
                SET data_devolucao = ?, status = 'Danificado'
                WHERE id = ?""", (hoje, id))
            preco = leiaDinheiro('Digite o preço do Livro: R$')
            multa = preco + 2.50
            print(f'Multa: R${multa:.2f}')
        conexao.commit()
            
        opc = retornar(['Atualizar', 'Não Atualizar'], 'Atualizar Status?')
        if opc == 1:
            print('Status de Empréstimo atualizados.')
            break
            
