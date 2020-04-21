from flask import Flask, render_template, request
import pandas as pd
import GetOldTweets3 as got
import pymongo
import datetime, time
import pdfkit
import base64

import re
import nltk
from nltk.corpus import stopwords
from nltk import FreqDist
from wordcloud import WordCloud
import matplotlib.pyplot as plt

import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

app = Flask(__name__)

connection = pymongo.MongoClient('localhost', 27017)
collection = connection.test.twitanalyzer


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        keyword = request.form['content']
        since_date = request.form['since']
        until_date = request.form['until']
        email = request.form['email']
        print(keyword, since_date, until_date)

        # Crawling from Twitter
        tweets = data_crawl(keyword, since_date, until_date)
        objectID = save_data(tweets, keyword, email, since_date, until_date)

        processed_list = pd.DataFrame(tweets, columns=["userID", "text", "date", "time"])

        frequency_result, relative_result, frequency_graph, relative_graph = analyze_data(processed_list, keyword)

        if draw_html_to_pdf(frequency_result, relative_result, frequency_graph, relative_graph):
            print(objectID)
            mail_send(objectID)

        return render_template('index.html', tweets=tweets)
    else:
        return render_template('index.html')


def data_crawl(keyword, since_date, until_date):
    tweet_list = []
    tweetCriteria = got.manager.TweetCriteria().setQuerySearch(keyword).setSince(since_date).setUntil(until_date)
    start_time = time.time()
    tweet = got.manager.TweetManager.getTweets(tweetCriteria)
    for each in tweet:
        tweets = [each.username, each.text, each.date.strftime("%Y-%m-%d"), each.date.strftime("%H:%M:%S")]
        tweet_list.append(tweets)

    print(time.time() - start_time)
    return tweet_list

def save_data(tweet_list, keyword, email, since_date, until_date):
    list_size = len(tweet_list)
    today = datetime.date.today()
    date = today.isoformat()
    new_documents = [
        {"email": email,
         "searched_at": date,
         "analyzed": False,
         "sent": False,
         "search_info":[
             {
                 "keyword": keyword,
                 "since": since_date,
                 "until": until_date,
             }
         ],
         "tweet": [
             {
                 "username": tweet_list[i][0],
                 "text": tweet_list[i][1],
                 "date": tweet_list[i][2],
                 "time": tweet_list[i][3]
             } for i in range(list_size)
         ]
         }
    ]
    objectID = collection.insert_many(new_documents).inserted_ids
    return objectID

def draw_html_to_pdf(frequency_result, relative_result, frequency_graph, relative_graph):
    html_string = "<!DOCTYPE html><head><meta charset = \"UTF-8\"></head><body><h1>Result Page</h1><div>"
    html_string+="<img width=500 src=\'data:image/png;base64,{0}".format(frequency_graph)
    html_string+="\'/><br><br><img width=500 src=\'data:image/png;base64,{0}".format(relative_graph)
    html_string+="\'/></body></html>"
    path_wkhtmltopdf = r'C:\Users\kimjiwoo\Desktop\Ireland\2individual_project\TwitAnlayse\static\wkhtmltox\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf = path_wkhtmltopdf)
    pdfkit.from_string(html_string, 'example.pdf', configuration=config)
    return True

def analyze_data(data, keyword):
    # filtering text data
    data[keyword] = data.apply(lambda data: frequency_validation(data, keyword), axis=1)
    is_valid = data[keyword]==True
    valid_set = data[is_valid]

    # frequency analyze
    counts = valid_set["date"].value_counts().sort_index()
    plt.title("Frequency of Keywords by date")
    plt.ylabel("number of tweets")
    counts.plot(kind='bar')
    frequency_fig = plt.gcf()
    plt.show()
    frequency_fig.savefig('./resource/frequency_graph.png', dpi=600)
    with open("./resource/frequency_graph.png", "rb") as imageFile:
        frequency_graph = base64.b64encode(imageFile.read()).decode('ascii')
    print(counts)

    valid_set.is_copy = None
    # relation analyze
    valid_set["raw_data"] = valid_set.apply(lambda valid_set: re.sub('[^a-zA-z]', ' ', valid_set["text"]), axis=1)
    valid_set["raw_data_edited"] = valid_set.apply(lambda valid_set: valid_set["raw_data"].lower().split(), axis=1)

    # nltk.download('stopwords')
    stop = set(stopwords.words('english'))
    def word_set(rawset):
        result = []
        for word in rawset:
            if not word in stop:
                result.append(word)
        return result
    valid_set["valid_words"] = valid_set.apply(lambda valid_set: word_set(valid_set["raw_data_edited"]), axis=1)

    stemmer = nltk.stem.SnowballStemmer('english')
    def stemmer_set(wordset):
        result = []
        for word in wordset:
            result.append(stemmer.stem(word))
        return result

    valid_set["stemmer_set"] = valid_set.apply(lambda valid_set: stemmer_set(valid_set["valid_words"]), axis=1)

    relative_list=[]
    def relative_set(wordset, keyword):
        for word in wordset:
            if word != keyword:
                relative_list.append(word)
        return True

    valid_set.apply(lambda valid_set: relative_set(valid_set["stemmer_set"], keyword), axis=1)
    fd_list = FreqDist(relative_list[:50])

    # drawing WordCloud
    wc = WordCloud(width=1000, height=600, background_color="#1DA1F2", random_state=0)
    plt.imshow(wc.generate_from_frequencies(fd_list))
    plt.axis("off")
    relative_fig = plt.figure()
    plt.show()
    wc.to_file("./resource/relative_graph.png")
    with open("./resource/relative_graph.png", "rb") as imageFile:
        relative_graph = base64.b64encode(imageFile.read()).decode('ascii')

    print(fd_list.most_common(20))

    return counts, fd_list, frequency_graph, relative_graph

def frequency_validation(data, keyword):
    text = data["text"]
    if keyword in text:
        return True
    return False


def mail_send(ObjectID):
    smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp.login('yourmail@gmail.com', 'password')
    msg = MIMEMultipart()
    msg['Subject'] = 'TEST'
    msg['From'] = 'yourmail@gmail.com'

    with open("C:/Users/kimjiwoo/Desktop/Ireland/2individual_project/TwitAnlayse/example.pdf", "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        "attachment; filename= result.pdf"
    )

    msg.attach(part)
    receiver = collection.find_one({"_id": ObjectID[0]}, {"email": 1})['email']

    smtp.sendmail('yourmail@gmail.com', receiver, msg.as_string())
    smtp.quit()
    return True

if __name__ == '__main__':
    app.run(debug=True)
