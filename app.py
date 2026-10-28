from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave-catalogo-filmes")

# Caminho do banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "filmes.db")


# Conecta ao banco de dados
def conectar_banco():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    return conexao


# Cria a tabela automaticamente
def criar_tabela():
    conexao = conectar_banco()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS filmes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            genero TEXT NOT NULL,
            ano INTEGER NOT NULL,
            nota REAL NOT NULL CHECK (nota >= 1 AND nota <= 10)
        )
    """)

    conexao.commit()
    conexao.close()


# Página inicial: listar filmes
@app.route("/")
def index():
    conexao = conectar_banco()

    filmes = conexao.execute(
        "SELECT * FROM filmes ORDER BY titulo"
    ).fetchall()

    conexao.close()

    return render_template("index.html", filmes=filmes)


# Cadastrar filme
@app.route("/adicionar", methods=["GET", "POST"])
def adicionar():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        genero = request.form.get("genero", "").strip()
        ano_texto = request.form.get("ano", "").strip()
        nota_texto = request.form.get("nota", "").strip()

        try:
            ano = int(ano_texto)
            nota = float(nota_texto.replace(",", "."))

            if not titulo or not genero:
                raise ValueError

            if ano < 1888 or ano > 2100:
                raise ValueError

            if not 1 <= nota <= 10:
                raise ValueError

        except ValueError:
            flash("Preencha os campos corretamente.", "error")
            return render_template("form.html", filme=None)

        conexao = conectar_banco()

        conexao.execute("""
            INSERT INTO filmes (titulo, genero, ano, nota)
            VALUES (?, ?, ?, ?)
        """, (titulo, genero, ano, nota))

        conexao.commit()
        conexao.close()

        flash("Filme cadastrado com sucesso!", "success")
        return redirect(url_for("index"))

    return render_template("form.html", filme=None)


# Editar filme
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conexao = conectar_banco()

    filme = conexao.execute(
        "SELECT * FROM filmes WHERE id = ?", (id,)
    ).fetchone()

    if filme is None:
        conexao.close()
        flash("Filme não encontrado.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        genero = request.form.get("genero", "").strip()
        ano_texto = request.form.get("ano", "").strip()
        nota_texto = request.form.get("nota", "").strip()

        try:
            ano = int(ano_texto)
            nota = float(nota_texto.replace(",", "."))

            if not titulo or not genero:
                raise ValueError

            if ano < 1888 or ano > 2100:
                raise ValueError

            if not 1 <= nota <= 10:
                raise ValueError

        except ValueError:
            conexao.close()
            flash("Preencha os campos corretamente.", "error")
            return render_template("form.html", filme=filme)

        conexao.execute("""
            UPDATE filmes
            SET titulo = ?, genero = ?, ano = ?, nota = ?
            WHERE id = ?
        """, (titulo, genero, ano, nota, id))

        conexao.commit()
        conexao.close()

        flash("Filme atualizado com sucesso!", "success")
        return redirect(url_for("index"))

    conexao.close()
    return render_template("form.html", filme=filme)


# Excluir filme
@app.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    conexao = conectar_banco()

    conexao.execute(
        "DELETE FROM filmes WHERE id = ?", (id,)
    )

    conexao.commit()
    conexao.close()

    flash("Filme excluído com sucesso!", "success")
    return redirect(url_for("index"))


# Cria o banco e inicia o servidor
criar_tabela()

if __name__ == "__main__":
    app.run(debug=True)
