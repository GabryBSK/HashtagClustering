import twitter_bot
import graph_maker


if __name__ == '__main__':

    tweets = "tweets.txt"
    twitter_client = twitter_bot.TwitterClient()
    results = twitter_client.get_tweet_by_hashtag('#drone', tweets, 500)
    maker = graph_maker.Maker()
    maker.calculate_distance(results[0], results[1], results[2])
