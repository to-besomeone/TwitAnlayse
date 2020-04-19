from flask import Flask, render_template, request
import pandas as pd
import GetOldTweets3 as got
import pymongo
import datetime, time

import analyze

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

        processed_list = pd.DataFrame(tweets, columns = ["userID", "text", "date", "time"])

        (frequency_result, relative_result) = analyze.analyze_data(processed_list, keyword)



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
