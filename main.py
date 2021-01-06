#!/usr/bin/env python
# coding: utf-8

import time
import datetime
import random

import requests
import tweepy
import schedule
import json

import settings

CONSUMER_KEY = settings.CONSUMER_KEY
CONSUMER_SECRET = settings.CONSUMER_SECRET
ACCESS_TOKEN = settings.ACCESS_TOKEN
ACCESS_TOKEN_SECRET = settings.ACCESS_TOKEN_SECRET

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
API = tweepy.API(auth)

now = datetime.datetime.now()
activate_time = now.strftime('%m月%d日 %H:%M')

# slackにエラーを通知する関数
def slack_to_error(error):
    WEB_HOOK_URL = settings.WEB_HOOK_URL
    requests.post(WEB_HOOK_URL, data=json.dumps({
        "text" : str(error),
        "icon_emoji" : ":fire:",
        "username" : "エラー報告"
    }))

# slackに動作報告をする関数
def slack_to_message():
    SLACK_OPERATION_REPORT = settings.SLACK_OPERATION_REPORT
    message = f'Twitter-Retweet Activate : {activate_time}'
    requests.post(SLACK_OPERATION_REPORT, data=json.dumps({
        "text" : message,
        "icon_emoji" : ":sunny:",
        "username" : "動作報告"
    }))


def retweet_tweet(search_list):

    # いいね件数
    FAB_COUNT = random.choice(range(3, 5))

    try:
        # ツイート上位100件を検索
        tweet_list = API.search(q=search_list, count=100)

        user_ids_for_add = []
        for tweet in tweet_list:
            """リスト除外条件

            ・既存フォロワー
            ・ターゲットのフォロワーが200人以下
            """
            user = tweet.user
            user_ids_for_add.append(user.id)

        cnt = 0
        error_list = []
        for tweet in tweet_list:
            user = tweet.user
            if ( user.id in user_ids_for_add ):
                try:
                    API.retweet(id=tweet.id)
                    cnt += 1
                    # 待機時間
                    time.sleep(random.randint(50, 110))
                    if ( cnt==FAB_COUNT ):
                        break
                except tweepy.TweepError:
                    if len(error_list) < 5:
                        pass
                    else:
                        break

                except Exception as e:
                    if len(error_list) < 5:
                        error_list.append(e)
                        pass
                    else:
                        break
        if error_list :
            slack_to_error(error_list)    
    except Exception as e:
        slack_to_error(e)

def main():
    slack_to_message()
    SEARCH_LIST = settings.SEARCH_LIST
    for word in SEARCH_LIST:
        tmp_list = [word]
        retweet_tweet(tmp_list)
    print(f'Twitter-retweet : {activate_time}')
    return

if __name__=="__main__":
    print("Retweet ... ")
    for i in range(8, 24, 4):
        schedule.every().day.at("{:02d}:37".format(i)).do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)