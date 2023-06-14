import sqlite3, re, bs4
from time import sleep
import requests
import urllib.request
dbconn = sqlite3.connect("db/scraper.db")
cur = dbconn.cursor()
twitter_username="pup_hime"
forker_url="http://forker:8080"
forker_secret="1234"
cur.execute("create table if not exists posts(tweet_id int, primary key(tweet_id))")

req = urllib.request.Request(
    f"https://nitter.net/{twitter_username}",
    data=None,
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
)
print("starting")
cur.execute("select max(tweet_id) from posts")
res = cur.fetchone()
if res[0]:
    last_tweet = res[0]
else:
    html = urllib.request.urlopen(req).read().decode("utf-8")
    soup = bs4.BeautifulSoup(html, 'html.parser')
    page_ids=[]
    for tweet in soup.find_all(class_="tweet-link"):
        if twitter_username in tweet['href']:
            page_ids.append(int(tweet['href'].replace("#m", '').split('/')[-1]))
    last_tweet = max(page_ids)

print(f"got last tweet id {last_tweet}")
while True:
    print("checking tweets")
    req = urllib.request.Request(
        f"https://nitter.net/{twitter_username}",
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    html = urllib.request.urlopen(req).read().decode("utf-8")
    soup = bs4.BeautifulSoup(html, 'html.parser')
    page_ids = []
    for tweet in soup.find_all(class_="tweet-link"):
        if twitter_username in tweet['href']:
            page_ids.append(int(tweet['href'].replace("#m", '').split('/')[-1]))
    if max(page_ids) > last_tweet:
        print("found some tweets")
        for id in sorted(page_ids):
            if id > last_tweet:
                requests.get(
                    f'{forker_url}/u?secret={forker_secret}&url=https://twitter.com/{twitter_username}/status/{id}&services=mastodon',
                )
                cur.execute("insert into posts(tweet_id) values (?)", (id,))
                dbconn.commit()
                sleep(15)
        last_tweet = max(page_ids)
    sleep(60)

