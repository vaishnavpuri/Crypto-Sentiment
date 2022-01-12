from datetime import datetime, date, timedelta
from types import new_class
import requests, json, re, os, time
from itertools import count

sentiment_key = "api key"
websearch_key = "api key"

#search keywords
crypto_key_pairs = {"BTCUSD":"Bitcoin", "ETHUSD":"Ethereum", "LTCUSD":"Litecoin", "ADAUSD":"Cardano", "SOLUSD":"Solana", "AVAXUSD":"Avalanche"}

date_since = date.today() - timedelta(days=1)

cryptocurrencies = []
crypto_keywords = []

#store keys and values in separate lists
for i in range(len(crypto_key_pairs)):
    cryptocurrencies.append(list(crypto_key_pairs.keys())[i])
    crypto_keywords.append(list(crypto_key_pairs.values())[i])

#search the news headlines based on keywords
def get_news_headlines():
    news_output = {}

    for crypto in crypto_keywords:
        #create empty dict 
        news_output["{0}".format(crypto)] = {"description": [], "title": []}
        url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/search/NewsSearchAPI"
        #adjust size to increase or decrease articles searched
        querystring = {"q":str(crypto),"pageNumber":"1","pageSize":"30","autoCorrect":"true","fromPublishedDate":date_since,"toPublishedDate":"null"}
        headers = {
            'x-rapidapi-key': websearch_key,
            'x-rapidapi-host': "contextualwebsearch-websearch-v1.p.rapidapi.com"
        }
        #getting response
        response = requests.request("GET", url, headers=headers, params=querystring)
        result = json.loads(response.text)

        #store headline and descrip into dict
        for news in result["value"]:
            news_output[crypto]["description"].append(news["description"])
            news_output[crypto]["title"].append(news["title"])

    return news_output

#analyze each headline 
def sentiment_analysis():
    news_output = get_news_headlines()

    for crypto in crypto_keywords:
        #empty list to store sent value
        news_output[crypto]["sentiment"] = {"pos": [], "mid": [], "neg": []}
        #analyze description sentiment
        if len(news_output[crypto]["description"]) > 0:
            for title in news_output[crypto]["title"]:
                #clean up
                titles = re.sub("[^A-Za-z0-9]+", " ", title)

                import http.client
                connect = http.client.HTTPSConnection('text-sentiment.p.rapidapi.com')
                #formatting and send request
                payload = "text="+titles
                headers = {
                    'content-type': 'application/x-www-form-urlencoded',
                    'x-rapidapi-host': 'text-sentiment.p.rapidapi.com',
                    'x-rapidapi-key': sentiment_key,
                }
                connect.request("POST", "/analyze", payload, headers)
                #get response and format
                res = connect.getresponse()
                data = res.read()
                title_sentiment = json.loads(data)

                #assign each sentiment to a list 
                if not isinstance(title_sentiment, int):
                    if title_sentiment["pos"] == 1:
                        news_output[crypto]["sentiment"]["pos"].append(title_sentiment["pos"])
                    elif title_sentiment["mid"] == 1:
                        news_output[crypto]["sentiment"]["mid"].append(title_sentiment["mid"])
                    elif title_sentiment["neg"] == 1:
                        news_output[crypto]["sentiment"]["neg"].append(title_sentiment["neg"])
                    else:
                        print(f"Sentiment not found for {crypto}")

    return news_output

#using sentiment returned, calulcate percentage
def sentiment_calc():
    news_output = sentiment_analysis()

    #reassign sentiment list value to single percentage 
    for crypto in crypto_keywords:
        if len(news_output[crypto]["title"]) > 0:
            news_output[crypto]["sentiment"]["pos"] = len(news_output[crypto]["sentiment"]["pos"])*100/len(news_output[crypto]["title"])
            news_output[crypto]["sentiment"]["mid"] = len(news_output[crypto]["sentiment"]["mid"])*100/len(news_output[crypto]["title"])
            news_output[crypto]["sentiment"]["neg"] = len(news_output[crypto]["sentiment"]["neg"])*100/len(news_output[crypto]["title"])

            print(crypto, news_output[crypto]["sentiment"])

    return news_output 


if __name__ == '__main__':
    for i in count():
        sentiment_calc()
        print(f"Iteration {i}")
        time.sleep(900)
