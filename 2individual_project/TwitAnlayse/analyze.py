import re
import nltk
from nltk.corpus import stopwords
from nltk import FreqDist
from wordcloud import WordCloud
import matplotlib.pyplot as plt

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
    fd_list = FreqDist(relative_list)

    # drawing WordCloud
    wc = WordCloud(width=1000, height=600, background_color="#1DA1F2", random_state=0)
    plt.imshow(wc.generate_from_frequencies(fd_list))
    plt.axis("off")
    plt.show()
    print(fd_list.most_common(20))

    return (counts, fd_list)

def frequency_validation(data, keyword):
    text = data["text"]
    if keyword in text:
        return True
    return False
