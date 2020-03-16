import os
import random
import re
import tweepy
import time
import sys
from collections import defaultdict
import numpy as np

auth = tweepy.OAuthHandler(
    os.environ.get("CONSUMER_KEY"),
    os.environ.get("CONSUMER_SECRET")
)
auth.set_access_token(
    os.environ.get("ACCESS_KEY"),
    os.environ.get("ACCESS_SECRET")
)

api = tweepy.API(auth)

master_list = []

def filter_mentions(user_names):
    filterd_list = []
    for user_name in user_names:
        timeline = api.user_timeline(screen_name=user_name, count=200)
        for tweet in timeline:
            if not contains_mention(tweet.text):
                filterd_list.append(tweet.text)
            
    return filterd_list
            

def contains_mention(tweet):
    if "@" in tweet:
        return True
    if "https://" in tweet:
        return True
    return False

master_list = filter_mentions([
    os.environ.get("ACCOUNT_1"),
    os.environ.get("ACCOUNT_2"),
    os.environ.get("ACCOUNT_3"),
    os.environ.get("ACCOUNT_4")
])
print("total tweets sourced: ", len(master_list))
tokenized_master = []

for tweet in master_list:
    for word in re.split("\s+", tweet):
        if word != '':
            tokenized_master.append(word.lower())

# word dictionary will contain every word in every tweet, with the value being every word that has ever followed it
# and these follow up words will have weighted values

# follow up word dictionary will contain the words that "naturally" follow words before it, with weighted value

word_graph = defaultdict(lambda: defaultdict(int)) 
last_word = tokenized_master[0]
for word in tokenized_master[1:]:
  word_graph[last_word][word] += 1
  last_word = word
  
def walk_graph(graph, distance=5, start_node=None):
  if distance <= 0:
    return []
  
  if not start_node:
    start_node = random.choice(list(graph.keys()))
  
  
  weights = np.array(
      list(word_graph[start_node].values()),
      dtype=np.float64)
  weights /= weights.sum()

  choices = list(word_graph[start_node].keys())
  chosen_word = np.random.choice(choices, None, p=weights)
  
  return [chosen_word] + walk_graph(
      graph, distance=distance-1,
      start_node=chosen_word)

non_suffix = ["the", "i", "a", ",", "i'll", "i'm"] 
while True:
    rand_num = random.randint(4, 21)
    tweet = ' '.join(walk_graph(word_graph, distance=rand_num))
    for ns in non_suffix:
        if tweet.endswith(ns):
            tweet = tweet[:-len(ns)]
    api.update_status(tweet)
    time.sleep(3600)