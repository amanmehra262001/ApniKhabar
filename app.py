
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    uname = db.Column(db.String(20), primary_key=True)
    mail = db.Column(db.String(100), nullable=False)
    paswrd = db.Column(db.String(100), nullable=False)
    date_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.uname}-{self.mail}"


Pokemons = ["Pikachu", "Charizard", "Squirtle", "Jigglypuff",
            "Bulbasaur", "Gengar", "Charmander", "Mew", "Lugia", "Gyarados"]


@app.route("/")
def index():

    return render_template('index.html')


@app.route("/about")
def about(name=None):
    return render_template('about.html', name=name)


@app.route("/signin")
def signin():
    return render_template('signin.html')


@app.route("/signin", methods=['GET', 'POST'])
def checksignin():
    uname = request.form['uname']
    pss = request.form['paswrd']
    # print(pss)
    user = User.query.filter(User.uname == uname).first()
    # print(user.paswrd)
    if user:
        if pss == user.paswrd:
            occupied = "matched"
        else:
            occupied = "passnotmatched"

    else:
        if request.method == 'POST':
            uname = (request.form['uname'])
            mail = (request.form['mail'])
            paswrd = (request.form['paswrd'])
            user = User(uname=uname, mail=mail, paswrd=paswrd)
            db.session.add(user)
            db.session.commit()
            occupied = "userregistered"
    return render_template('signin.html', occupied=occupied, user=user)


if __name__ == "__main__":
    app.run(debug=True)
