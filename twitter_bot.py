from tweepy import API
from tweepy import Cursor
from tweepy import OAuthHandler

import json

from collections import Counter

import twitter_credentials
import db_connector


# # # TWITTER AUTHENTICATOR # # #
class TwitterAuthenticator():
    """
    Esegue il processo di autenticazione con il client di Twitter usando le credenziali legate all'account.
    """

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth


# # # TWITTER CLIENT # # #
class TwitterClient():
    """
    Definisce un Twitter Client su cui svolgere metodi di tweepy.api.
    """

    def __init__(self):
        # Esegue l'autenticazione.
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        # Accede alle API di Tweepy.
        self.twitter_client = API(self.auth, wait_on_rate_limit=True)
        # Crea un connettore per il database MongoDB Atlas.
        self.connector = db_connector.Connector("***", "***")
        # Apre la connessione con il database.
        self.client = self.connector.open_connection()

    def get_tweet_by_hashtag(self, hashtag_to_search, file, num_tweets):
        # Serve per contare le occorrenze degli hashtag con una classe Counter.
        word_list = []
        # Contatore - Serve per numerare i tweet presi.
        c = 0
        for tweet in Cursor(self.twitter_client.search, q=hashtag_to_search, tweet_mode='extended').items(num_tweets):
            # Lista che contiene il record da caricare. Corrisponde ad un tweet.
            tweet_db = {}
            # Contatore - Serve per prendere gli hashtag dal tweet.
            j = 0
            # Se il tweet è stato ritwittato viene scartato.
            if not tweet.retweeted:
                # Se il tweet ha una hashtag list viene preso.
                if tweet.entities['hashtags']:
                    c += 1
                    # Viene stampato nel file .txt.
                    # L'oggetto Status di Tweepy non è serializzabile con JSON, ma ha la proprietà _json
                    # che contiene dati che possono essere serializzati con JSON.
                    json_data = json.dumps(tweet._json)
                    # Scrive il tweet in formato JSON nel file .txt.
                    with open(file, 'a', encoding='utf-8') as hl:
                        hl.write('Tweet n. (' + str(c) + ')' + '\n' + json_data + '\n' + '\n')
                    # Print su console
                    print('Tweet n. (' + str(c) + ')' + '\n')
                    # # # created_at # # #
                    # Crea l'elemento "created_at".
                    tweet_db['created_at'] = tweet._json['created_at']
                    # # # id_str # # #
                    # Crea l'elemento "id_str".
                    tweet_db['id_str'] = tweet._json['id_str']
                    # # # full_text # # #
                    # Crea l'elemento "full_text".
                    tweet_db['full_text'] = tweet._json['full_text']
                    # # # hashtags # # #
                    # Variabile per ciclare gli hashtag di ogni tweet.
                    hashtags = tweet._json['entities']['hashtags']
                    # Lista che contiene gli hashtag per ogni tweet.
                    hashtag_list = []
                    for i in hashtags:
                        j += 1
                        # Inserisce gli hashtag in hashtag_list.
                        hashtag_list.append(tweet._json['entities']['hashtags'][j - 1]['text'])
                    # hashtag_list_json contiene coppie {"Chiave" : "Valore"} per gli hashtag raccolti.
                    hashtag_list_json = []
                    for hashtag in hashtag_list:
                        # Crea la coppia {"name" : "hashtag"}.
                        hashtag_list_json.append({'name': hashtag})
                        # Inserisce tutti gli hashtag di tutti i tweet dentro la lista delle occorrenze.
                        word_list.append(hashtag)
                    # Crea l'elemento "hashtags".
                    tweet_db['hashtags'] = hashtag_list_json
                    # # # screen_name # # #
                    # Crea l'elemento "screen_name".
                    tweet_db['screen_name'] = tweet._json['user']['screen_name']
                    # # # tweet_link # # #
                    # Crea il link del tweet.
                    link = "https://twitter.com/{}/status/{}".format(tweet_db['screen_name'], tweet_db['id_str'])
                    # Crea l'elemento "tweet_link".
                    tweet_db['tweet_link'] = link
                    # Scrive il record che verrà caricato nel database sul file .txt.
                    with open(file, 'a', encoding='utf-8') as hl:
                        hl.write(json.dumps(tweet_db, ensure_ascii=False) + '\n' + '\n')
                    # Print su console.
                    print(str(j) + ' hashtag trovati' + '\n' + '*************' + '\n')
                    # Esegue l'upload del record sul database.
                    self.connector.upload_record(self.client, "twitter_bot_db", "tweet", tweet_db)
        # Print su console.
        print("Hai letto tutti i tweet!" + '\n')
        # Scrive le occorrenze degli hashtag nel file .txt.
        with open("hashtag_occurrences.txt", 'w', encoding='utf-8') as ho:
            ho.write("Hashtags occurrences for " + hashtag_to_search + ": " + str(Counter(word_list)))
        # Esegue la query per contare le occorrenze degli hashtag sui record del database.
        self.connector.get_hashtag_occurrences(self.client, "twitter_bot_db", "tweet")

        return word_list, self.connector, self.client
