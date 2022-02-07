from webbrowser import get
from flask import Flask, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from decouple import config
from sqlalchemy import null
from newsapi import NewsApiClient
import json
from urllib.request import urlopen

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
    uname = db.Column(db.String(20), unique=True, primary_key=True)
    mail = db.Column(db.String(100), nullable=False)
    paswrd = db.Column(db.String(100), nullable=False)
    userprefrencesstr = db.Column(db.String(200))
    date_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.uname}-{self.mail}"


# class Query(db.Model):
#     queryfname = db.Column(db.String(20), nullable=False)
#     querylname = db.Column(db.String(20), nullable=False)
#     querymail = db.Column(db.String(50), nullable=False, primary_key=True)
#     querydesc = db.Column(db.String(500), nullable=False)


api_key = config('API_KEY')
generalprefrences = ['world', 'design', 'stocks',
                     'entertainment', 'arts', 'technology', 'culture', 'photography', 'politics', 'celebrity']
newsapi = NewsApiClient(api_key=api_key)

#######################
unsplash_api_key = config('UNSPLASH_API')


def getimage(topicsarr, imgsrcarr):
    imgsrcarr = []
    for topic in topicsarr:
        unsplash_image = f"https://api.unsplash.com/search/photos/?query={topic}&per_page=1&client_id={unsplash_api_key}"
        # store the response of URL
        response = urlopen(unsplash_image)
        # # storing the JSON response
        # # from url in data
        data_json = json.loads(response.read())
        # # print the json response
        imgsrcarr.append(data_json['results'][0]['urls']['raw'])
    return imgsrcarr


def getnews(topicsarr):
    finalnewsarr = ['0', '1']
    newsarr = []
    imgsrcarr = []
    for topic in topicsarr:
        unsplash_image = f"https://api.unsplash.com/search/photos/?query={topic}&per_page=1&client_id={unsplash_api_key}"
        response = urlopen(unsplash_image)
        data_json = json.loads(response.read())
        imgsrcarr.append(data_json['results'][0]['urls']['raw'])
        all_articles = newsapi.get_everything(q=topic,
                                              sources='bbc-news,the-verge',
                                              domains='bbc.co.uk,techcrunch.com',
                                              from_param='2022-01-08',
                                              to='2022-02-05',
                                              language='en',
                                              sort_by='relevancy',
                                              page=2)
        newsarr.append(all_articles['articles'][0]['title'])
    finalnewsarr[0] = newsarr
    finalnewsarr[1] = imgsrcarr
    return finalnewsarr


@app.route("/")
def index():
    # print(all_articles)
    todayTopTenarr = []
    todayTopTenimgsrc = []
    # with open('news.json', 'w') as f:
    #     json.dump(all_articles, f)
    for topic in generalprefrences:
        all_articles = newsapi.get_everything(q=topic,
                                              sources='bbc-news,the-verge',
                                              domains='bbc.co.uk,techcrunch.com',
                                              from_param='2022-01-08',
                                              to='2022-02-05',
                                              language='en',
                                              sort_by='relevancy',
                                              page=2)
        todayTopTenarr.append(all_articles['articles'][0]['title'])
        print(topic)
    # print(todayTopTenarr)
    todayTopTenimgsrc = getimage(generalprefrences, todayTopTenimgsrc)
    print(todayTopTenimgsrc)
    newsarr = getnews(generalprefrences)
    try:
        myname = session.get('myname', None)
    except:
        print("error occured username not defined")
    if myname:
        user = User.query.filter(User.uname == myname).first()
        # print(user.userprefrencesstr)
        userprefrencesarr = user.userprefrencesstr.split()
        # print(userprefrencesarr)
        newsarr = getnews(userprefrencesarr)
        return render_template('index.html', myname=myname, generalprefrences=generalprefrences, todayTopTenarr=todayTopTenarr, userprefrencesarr=userprefrencesarr, unsplash_api_key=unsplash_api_key, todayTopTenimgsrc=todayTopTenimgsrc, newsarr=newsarr)
    return render_template('index.html', generalprefrences=generalprefrences, todayTopTenarr=todayTopTenarr, unsplash_api_key=unsplash_api_key, todayTopTenimgsrc=todayTopTenimgsrc, newsarr=newsarr)


@ app.route("/contact")
def contact():
    myname = session.get('myname', None)
    if myname:
        return render_template('contact.html', myname=myname)
    return render_template('contact.html')


@ app.route("/signin")
def signin():
    return render_template('signin.html')


@ app.route("/signin", methods=['POST'])
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
            print(uname)
            if uname == "":
                if paswrd == "":
                    occupied = "emptysubmit"
            else:
                return redirect(url_for('pref'))

    return render_template('signin.html', occupied=occupied, user=user)


@ app.route("/pref", methods=['GET', 'POST'])
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
                else:
                    userunprefered.append(topics)
            except:
                print("some error occured")
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
        return redirect(url_for('signin'))
    return render_template('pref.html')


@ app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect('/')


# business movies shopping crypto inovations
if __name__ == "__main__":
    app.run(debug=True)
