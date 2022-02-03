from flask import Flask
from flask import render_template

app = Flask(__name__)

Pokemons = ["Pikachu", "Charizard", "Squirtle", "Jigglypuff",
            "Bulbasaur", "Gengar", "Charmander", "Mew", "Lugia", "Gyarados"]


@app.route("/")
def index():
    return render_template('index.html', len=len(Pokemons), Pokemons=Pokemons)


@app.route("/about")
def about(name=None):
    return render_template('about.html', name=name)


@app.route("/signin")
def signin(name=None):
    return render_template('signin.html', name=name)


app.run(use_reloader=True, debug=True)
