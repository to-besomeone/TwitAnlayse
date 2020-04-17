from flask import Flask, render_template, url_for, request
import tweepy
import pandas as pd
import matplotlib.pyplot as plt
import GetOldTweets3 as got
import pymongo
import datetime, time
import re
import nltk
from nltk.corpus import stopwords


app = Flask(__name__)

# keys
consumer_key = "gkMzEcz5kOrNnv6CIjvSFZTVk"
consumer_secret = "dPvaQsqdUwAmVsYDJO55tqtys3JfBO7Y1TLwqJ5Zdg1LfF4stg"
access_token = "1236798377465196545-UmW0J0bfIO7udunJL3TYsfTllRbzar"
access_secret = "rB0fo5jaPu3n6HD4GIVqm8jSp6VQZS9rYwEUquAMa79l9"

# 1. Make Handler and request identify personal info
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# 2. Request for Access
auth.set_access_token(access_token, access_secret)
# 3. Make Twitter API
api = tweepy.API(auth)

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

        processed_list = pd.DataFrame(tweets, columns = ["userID", "text", "date", "time"])

        analyze_data(processed_list, keyword)
        # 1. 데이터분석이 완료되면 def draw_html()
        # 4.if (def draw_html) : def send_mail(ObjectId)


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
    plt.show()
    print(counts)

    # relation analyze
    valid_set["raw_data"] = valid_set.apply(lambda valid_set: re.sub('[^a-zA-z]', ' ', valid_set["text"]), axis=1)
    valid_set["raw_data_edited"] = valid_set.apply(lambda valid_set: valid_set["raw_data"].lower().split(), axis=1)

    print(valid_set)
    # stop = set(stopwords.words('english'))
    # processed_data = [word for word in valid_set["raw_data"] if not word in stop]
    #
    # stemmer = nltk.stem.SnowballStemmer('english')
    # stemmer_words = [stemmer.stem(word) for word in processed_data]
    #

    return True

def frequency_validation(data, keyword):
    text = data["text"]
    if keyword in text:
        return True
    return False

# def draw_html():
# 2. html 다 그리면 if(def save_to_pdf(htmlstring):) return true

#def save_to_pdf(htmlstring):
#  3. import pdfkit
#   pdfkit.from_string(string, 'pdf')
#   return true


#def send_mail():
#

if __name__ == '__main__':
    app.run()
