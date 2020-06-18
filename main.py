import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class TwitterClient(object): 
	''' 
	Generic Twitter Class for sentiment analysis. 
	'''
	def __init__(self): 
		''' 
		Class constructor or initialization method. 
		'''
		# keys and tokens from the Twitter Dev Console 
		consumer_key = '<CONSUMER KEY>'
		consumer_secret = '<CONSUMER SECRET>'
		access_token = '<ACCESS TOKEN>'
		access_token_secret = '<TOKEN SECRET>'

		try: 
			# create OAuthHandler object 
			self.auth = OAuthHandler(consumer_key, consumer_secret) 
			# set access token and secret 
			self.auth.set_access_token(access_token, access_token_secret) 
			# create tweepy API object to fetch tweets 
			self.api = tweepy.API(self.auth) 
		except: 
			print("Error: Authentication Failed") 
			

	def new_tweet(self, tweet):
		return self.api.update_status(tweet)

	def clean_tweet(self, tweet): 
		''' 
		Utility function to clean tweet text by removing links, special characters 
		using simple regex statements. 
		'''
		tweet = re.sub('RT @[A-Za-z0–9]*:', '', tweet) # Removing RT
		tweet = re.sub('@[A-Za-z0–9]+', '', tweet) #Removing @mentions
		tweet = re.sub('#', '', tweet) # Removing '#' hash tag
		tweet = re.sub('https?:\/\/\S+', '', tweet) # Removing hyperlink
		return tweet

	def get_tweet_sentiment_textblob(self, tweet): 
		''' 
		Utility function to classify sentiment of passed tweet 
		using textblob's sentiment method 
		'''
		analysis = TextBlob(self.clean_tweet(tweet))
		# Set sentiment 
		if analysis.sentiment.polarity > 0: 
			return 'positive'
		elif analysis.sentiment.polarity == 0: 
			return 'neutral'
		else: 
			return 'negative'
			

	def get_tweet_sentiment_vader(self, tweet): 
		''' 
		Utility function to classify sentiment of passed tweet 
		using vader's sentiment method 
		'''
		analyser = SentimentIntensityAnalyzer()
		vader_score = analyser.polarity_scores(tweet)
		# Set sentiment 
		if vader_score["compound"] >= 0.05: 
			return 'positive'
		elif vader_score["compound"] > -0.05 and vader_score["compound"] < 0.05: 
			return 'neutral'
		elif vader_score["compound"] <= -0.05: 
			return 'negative'
		else:
			return 'They don\'t know what this feeling is like'

	def get_tweets(self, id, count = 10): 
		''' 
		Main function to fetch tweets and parse them. 
		'''
		tweets = [] 

		try: 
			# call twitter api to fetch tweets 
			# Visit API documentation for more query patterns - http://docs.tweepy.org/en/v3.5.0/api.html#API.user_timeline
			fetched_tweets = self.api.user_timeline(id = id, count = count) 
			print(fetched_tweets)

			for tweet in fetched_tweets: 
				parsed_tweet = {} 

				parsed_tweet['text'] = tweet.text 
				## Determining sentiment using TextBlob
				# parsed_tweet['sentiment'] = self.get_tweet_sentiment_textblob(tweet.text) 
				## Determining sentiment using Vader
				parsed_tweet['sentiment'] = self.get_tweet_sentiment_vader(tweet.text) 
				
				# appending parsed tweet to tweets list 
				if tweet.retweet_count > 0: 
					# if tweet has retweets, ensure that it is appended only once 
					if parsed_tweet not in tweets: 
						tweets.append(parsed_tweet) 
				else: 
					tweets.append(parsed_tweet) 

			return tweets 

		except tweepy.TweepError as e: 
			print("Error : " + str(e)) 

def main(): 
	api = TwitterClient() 
	tweets = api.get_tweets(id = '<Enter User ID here>', count = 25)
	
	ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 
	positive = len(ptweets)/len(tweets)
	tweet_status = "Positive tweets percentage: {} % \n".format(100*positive)
	
	
	ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
	negative = len(ntweets)/len(tweets)
	tweet_status += "Negative tweets percentage: {} % \n".format(100*negative)
	
	tweet_status += "Neutral tweets percentage: {} % \n".format(100*(len(tweets) -(len( ntweets )+len( ptweets)))/len(tweets))
	
	if (negative) >= 0.5:
		tweet_status = "I am being negative. Please send some positivity this way \n" + tweet_status
	elif (positive) >= 0.5:
		tweet_status = "I am feeling uber positive!\n" + tweet_status
	else:
		tweet_status = "No man's land \n" + tweet_status
		
	try:
		response = api.new_tweet(tweet_status)
	except Exception as e:
		print("Error creating tweet: " + str(e))

if __name__ == "__main__": 
	main() 
