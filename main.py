from flask import Flask, render_template, request, flash, redirect, url_for, session
import fdb
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'Aqui_e_a_chave_da_turma_a'

host = "localhost"
database = r"C:\Users\Aluno\Downloads\JUNTAR\BANCO.FDB"
user ="sysdba"
password = "sysdba"

con = fdb.connect(host=host,database=database,user=user,password=password)

@app.route("/")
def index():
    cursor = con.cursor() #Abrir cursor
    cursor.execute(""" SELECT l.id_livro, l.NOME, l.autor, l.ANO_PUBLICACAO FROM livro l
                   order by l.nome asc """)
    livros = cursor.fetchall()
    cursor.close()
    return render_template('index.html', livros=livros)

@app.route('/novo')
def novo():
    if 'id_usuario' not in session:
        flash('Precisa estar loggado.')
        return redirect(url_for('entrar_user'))
    else:
        return render_template('novo.html')

@app.route('/criar', methods=['POST'])
def criar():


    nome = request.form['nome']
    autor = request.form['autor']
    ano_publicacao = request.form['ano_publicacao']

    cursor = con.cursor()

    try:

       cursor.execute(""" SELECT 1
                          FROM LIVRO 
                          WHERE nome = ?""", (nome,))
       if cursor.fetchone() is not None:
           flash("Erro: Livro já cadastrado!")
           return redirect(url_for('novo'))


       cursor.execute("""INSERT INTO LIVRO (nome, AUTOR, ANO_PUBLICACAO)
                      values(?, ?, ?) RETURNING ID_LIVRO """, (nome, autor, ano_publicacao))

       id_livro = cursor.fetchone()[0]
       con.commit()

       arquivo = request.files['imagem']

       arquivo.save(f'uploads/capa{id_livro}.jpg')

       flash("Livro criado com sucesso!")


    except Exception as e:
      flash(f"Ocorreu um erro! -> {e}")
      con.rollback()

    finally:
        cursor.close()
    return redirect(url_for('index'))


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cursor = con.cursor()
    try:
        cursor.execute(""" SELECT id_livro, nome, autor, ano_publicacao from livro where id_livro = ? """, (id,))
        livro = cursor.fetchone()
        print(livro)
        if livro is None:
            flash("Livro NÃO encontrado")
            return redirect(url_for('index'))

        if request.method == 'POST':
            nome = request.form['nome']
            autor = request.form['autor']
            ano_publicacao = request.form['ano_publicacao']
            arquivo = request.files['imagem']


            cursor.execute(""" UPDATE LIVRO
                               SET nome = ?, autor = ?, ano_publicacao = ?
                               WHERE id_livro = ? """,
                           (nome, autor, ano_publicacao, id))


            id_livro = cursor.fetchone()[0]
            con.commit()


            arquivo.save(f'uploads/capa{id_livro}.jpg')

            flash("Livro editado com sucesso!")

            print(livro)

            print(livro[3])

        return render_template('editar.html', livro=livro)

    except Exception as e:
        flash(f"Ocorreu um erro! -> {e}")
        return redirect(url_for('index'))

    finally:
        cursor.close()

@app.route('/deletar/<int:id>', methods=['GET', 'POST'])
def deletar(id):
    cursor = con.cursor()
    try:
        cursor.execute("""DELETE FROM LIVRO WHERE ID_LIVRO = ?""", (id,))
        con.commit()
        flash("Livro deletado com sucesso!")
        return redirect(url_for('index'))
    except Exception as e:
        con.rollback()
        flash(f"Ocorreu um erro! -> {e}")
        return redirect(url_for('index'))
    finally:
        cursor.close()

@app.route("/usuario")
def usuario():
    cursor = con.cursor() #Abrir cursor
    cursor.execute(""" SELECT u.id_usuario, u.NOME, u.email, u.senha FROM usuario u
                   order by u.nome asc """)
    usuarios = cursor.fetchall()
    cursor.close()
    return render_template('usuario.html', usuarios=usuarios)

@app.route('/novo_user')
def novo_user():
    return render_template('novo_user.html')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']


    senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')
    cursor = con.cursor()

    try:
       cursor.execute(""" SELECT 1
                          FROM usuario  
                          WHERE email = ?""", (email,))
       if cursor.fetchone() is not None:
           flash("Erro: Usuário já cadastrado!")
           return redirect(url_for('usuario'))


       cursor.execute("""INSERT INTO usuario (nome, email, senha)
                      values(?, ?, ?)""", (nome, email, senha_hash))
       con.commit()
       flash("Usuário cadastrado com sucesso!")


    except Exception as e:
      flash(f"Ocorreu um erro! -> {e}")
      con.rollback()

    finally:
        cursor.close()
    return redirect(url_for('usuario'))

@app.route('/editar_usuario/<int:id>', methods=['GET','POST'])
def editar_usuario(id):
    cursor = con.cursor()
    try:
        cursor.execute(""" SELECT id_usuario, nome, email, senha
                           FROM usuario
                           WHERE id_usuario = ? """, (id,))
        usuario = cursor.fetchone()

        if usuario is None:
            flash("Usuário NÃO encontrado")
            return redirect(url_for('usuario'))

        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']

            senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')

            cursor.execute(""" UPDATE usuario
                               SET nome = ?, email = ?, senha = ?
                               WHERE id_usuario = ? """,
                           (nome, email, senha_hash, id))

            con.commit()
            flash("Usuário editado com sucesso!")
            return redirect(url_for('usuario'))

        return render_template('editar_user.html', usuario=usuario)

    except Exception as e:
        flash(f"Ocorreu um erro! -> {e}")
        con.rollback()
        return redirect(url_for('usuario'))

    finally:
        cursor.close()

@app.route('/deletar_usuario/<int:id>', methods=['GET', 'POST'])
def deletar_usuario(id):
    cursor = con.cursor()
    try:
        cursor.execute("""DELETE
                          FROM usuario
                          WHERE ID_usuario = ?""", (id,))
        con.commit()
        flash("Usuário deletado com sucesso!")
        return redirect(url_for('usuario'))
    except Exception as e:
        con.rollback()
        flash(f"Ocorreu um erro! -> {e}")
        return redirect(url_for('usuario'))
    finally:
        cursor.close()

@app.route('/entrar_user')
def entrar_user():
    return render_template('login.html')


@app.route('/entrar', methods=['POST'])
def entrar():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']
    cursor = con.cursor()

    try:
       cursor.execute(""" SELECT id_usuario,senha
                          FROM usuario  
                          WHERE nome = ? and email = ? """, (nome, email))

       usuario =cursor.fetchone()

       if not usuario:
           flash("Erro: Login incorreto!")
           return redirect(url_for('entrar_user'))

       id_usuario, senha_hash = usuario

       if usuario:
           if bcrypt.check_password_hash(senha_hash, senha):
               session ['id_usuario'] = id_usuario

               flash("Login bem-sucedido!")
               return render_template('usuario2.html', usuario=usuario)
           else:
               flash("Login incorreto!")
               return redirect(url_for('entrar_user'))

    except Exception as e:
      flash(f"Ocorreu um erro! -> {e}")
      con.rollback()

    finally:
        cursor.close()

@app.route('/logout')
def logout():
    session.pop('id_usuario', None)
    flash("Logout com sucesso!")
    return redirect(url_for('usuario'))
    
@app.route('/usuario2')
def usuario2():
    if 'id_usuario' not in session:
        flash('Precisa estar logado.')
        return redirect(url_for('entrar_user'))
    else:
        return render_template('usuario2.html')

if __name__ == "__main__":
    app.run(debug=True)
