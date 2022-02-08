
from flask import Flask, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from decouple import config
from sqlalchemy import null
from newsapi import NewsApiClient
# from newsdataapi import NewsDataApiClient
# from newscatcherapi import NewsCatcherApiClient
import json
# from urllib.request import urlopen
# import http.client
# import urllib.parse

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


api_key = config('NEWS_API_API_KEY')
# newsapi = NewsDataApiClient(apikey=api_key)
newsapi = NewsApiClient(api_key=api_key)
# newsapi = NewsCatcherApiClient(x_api_key=api_key)
#######################
unsplash_api_key = config('UNSPLASH_API')

# preparations...........................
generalprefrences = ['world', 'design', 'stocks',
                     'entertainment', 'arts', 'technology', 'culture', 'photography', 'politics', 'celebrity']
generalprefrencenewsarr = []
generalprefrenceimgarr = []
generalprefrencelinkarr = []
for topic in generalprefrences:
    # newsData
    # all_articles = newsapi.news_api(q=topic,
    #                                 language='en')
    # newscatcher
    # all_articles = newsapi.get_search(q=topic,
    #                                   lang='en',                                         page_size=100)
    # newsapi
    all_articles = newsapi.get_everything(q=topic,
                                          language='en',
                                          page=2)
    # with open('news.json', 'a') as f:
    #     json.dump(all_articles, f)
    generalprefrencenewsarr.append(all_articles['articles'][0]['title'])
    generalprefrenceimgarr.append(all_articles['articles'][0]['urlToImage'])
    generalprefrencelinkarr.append(all_articles['articles'][0]['url'])


@app.route("/")
def index():
    newsarr = [generalprefrencenewsarr, generalprefrenceimgarr]
    try:
        myname = session.get('myname', None)
    except:
        print("User not detected")
    if myname:
        foryouimg = []
        foryoulink = []
        user = User.query.filter(User.uname == myname).first()
        # print(user.userprefrencesstr)
        userprefrencesarr = user.userprefrencesstr.split()
        # print(userprefrencesarr)
        # print(newsarr)
        for topic in userprefrencesarr:
            print(topic)
            if topic != 'inovations':
                all_articles = newsapi.get_everything(q=topic,
                                                      language='en',
                                                      page=2)

                newsarr.append(all_articles['articles'][0]['title'])
                foryouimg.append(all_articles['articles'][0]['urlToImage'])
                foryoulink.append(all_articles['articles'][0]['url'])
                print(type(all_articles['articles'][0]['title']))
            else:
                print("nothing to show")
        return render_template('index.html', myname=myname, generalprefrences=generalprefrences, todayTopTenarr=generalprefrencenewsarr, userprefrencesarr=userprefrencesarr, unsplash_api_key=unsplash_api_key, todayTopTenimgsrc=generalprefrenceimgarr, todayTopTenlinks=generalprefrencelinkarr, newsarr=newsarr, foryouimg=foryouimg, foryoulink=foryoulink, gforyouimg=generalprefrenceimgarr, gforyoulink=generalprefrencelinkarr)
    return render_template('index.html', myname=myname, generalprefrences=generalprefrences, todayTopTenarr=generalprefrencenewsarr, unsplash_api_key=unsplash_api_key, todayTopTenimgsrc=generalprefrenceimgarr, todayTopTenlinks=generalprefrencelinkarr, newsarr=newsarr, foryouimg=generalprefrenceimgarr, foryoulink=generalprefrencelinkarr)


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
