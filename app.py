
from crypt import methods
from flask import Flask, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from sqlalchemy import null

app = Flask(__name__)
app.secret_key = "super secret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

uname = null
paswrd = null
mail = null
userprefrencesstr = null


class User(db.Model):
    uname = db.Column(db.String(20), primary_key=True)
    mail = db.Column(db.String(100), nullable=False)
    paswrd = db.Column(db.String(100), nullable=False)
    userprefrencesstr = db.Column(db.String(200))
    date_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.uname}-{self.mail}"


@app.route("/")
def index():
    try:
        myname = session.get('myname', None)
    except:
        print("error occured username not defined")
    if myname:
        return render_template('index.html', myname=myname)
    return render_template('index.html')


@app.route("/about")
def about():
    myname = session.get('myname', None)
    if myname:
        return render_template('about.html', myname=myname)
    return render_template('about.html')


@app.route("/signin")
def signin():
    return render_template('signin.html')


@app.route("/signin", methods=['POST'])
def checksignin():
    global uname, mail, paswrd
    uname = request.form['uname']
    pss = request.form['paswrd']
    # print(uname, pss)
    user = User.query.filter(User.uname == uname).first()
    if user:
        if pss == user.paswrd:
            session['myname'] = uname
            return redirect('/')
        else:
            occupied = "passnotmatched"

    else:
        if request.method == 'POST':

            uname = (request.form['uname'])
            mail = (request.form['mail'])
            paswrd = (request.form['paswrd'])

            # occupied = "userregistered"
            return redirect('/pref')

    return render_template('signin.html', occupied=occupied, user=user)


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect('/')


@app.route("/pref", methods=['GET', 'POST'])
def pref():
    userprefrences = []
    userunprefered = []
    options = ['business', 'movies', 'sports', 'cricket', 'shopping', 'international',
               'food', 'crypto', 'web', 'education', 'lifestyle', 'inovations', ]
    if request.method == 'POST':
        for topics in options:
            try:
                if request.form[topics] == "on":
                    userprefrences.append(topics)
            except:
                userunprefered.append(topics)
        # print(userprefrences)
        if len(userprefrences) > 0:  # if list not empty
            # converting python list to string
            userprefrencesstr = ' '.join(userprefrences)
        else:  # if list is empty
            userprefrencesstr = "general business sports movies education lifestyle art"
        user = User(uname=uname, mail=mail, paswrd=paswrd,
                    userprefrencesstr=userprefrencesstr)
        db.session.add(user)
        db.session.commit()
        # print(userprefrencesstr)
        return redirect('/signin')
    return render_template('pref.html')


# business movies shopping crypto inovations
if __name__ == "__main__":
    app.run(debug=True)
