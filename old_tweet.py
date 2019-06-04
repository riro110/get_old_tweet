from requests_oauthlib import OAuth1Session
import json
import time
from datetime import datetime
import calendar

# ファイルにはConsumer Key、Consumer Key Secret、Access Token、Access Token Secretの順で記入
TOKEN_PATH = "アクセストークンを記述したファイルのパス"
CK = ""
CS = ""
AK = ""
AS = ""


def read_token(file_path):
    """ファイルからトークンを読み込む

    Arguments:
        file_path {string} -- ファイルのパス
    """
    global CK, CS, AK, AS
    with open(file_path, "r") as f:
        for i, line in enumerate(f):
            line = line.replace("\n", "")
            # print(type(line))
            if i == 0:
                CK = line
            elif i == 1:
                CS = line
            elif i == 2:
                AK = line
            else:
                AS = line
    print("CK =", CK)
    print("CS =", CS)
    print("AK =", AK)
    print("AS =", AS)


def get_user_timeline(screen_name, since_id=None, max_id=None):
    """ユーザータイムラインを取得

    Arguments:
        screen_name {string} -- twitterのユーザー名 

    Keyword Arguments:
        since_id {string} -- このidのツイート以降のツイートを取得 (default: {None})
        max_id {string} -- このidのツイート以前のツイートを取得 (default: {None})

    Returns:
        timeline {list} -- ツイートのリスト
    """
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    params = {"screen_name": screen_name, "count": 200,
              "include_rts": "false", "exclude_replies": "true",
              "since_id": since_id, "max_id": max_id}
    req = twitter.get(url, params=params)
    if req.status_code == 200:
        timeline = json.loads(req.text)
        return timeline
    else:
        print("Error: %d failed to get user timeline" % req.status_code)


def time_convert(src_time):
    """UTCを日本時間に変換

    Arguments:
        src_time {string} -- '%a %b %d %H:%M:%S +000 %Y'
    Returns:
        local_time {datetime} -- 日本時間
    """
    time_utc = time.strptime(src_time, '%a %b %d %H:%M:%S +0000 %Y')
    unix_time = calendar.timegm(time_utc)
    local_time = time.localtime(unix_time)
    return local_time


def search(screen_name, since, until):
    """ツイートを検索

    Arguments:
        since {time.struct_time} -- since この日のツイートは含まれる
        until {time.struct_time} -- until この日のツイートは含まれない

    Returns:
        tweets {list} -- 取得したツイート
    """
    is_continue = True
    tweets = list()
    max_id = None
    while is_continue:
        timeline = get_user_timeline(screen_name, max_id=max_id)
        if len(timeline) == 1:
            print("昔すぎてたどれない")
            break
        #print("Now the most recent tweet in timeline is on",timeline[0]["created_at"])
        # print(timeline[0]["text"],timeline[0]["id_str"])
        for tweet in timeline:
            japan_time = time_convert(tweet["created_at"])
            if since < japan_time <= until:
                tweets.append(tweet)
            elif japan_time < since:
                is_continue = False
                break
        max_id = timeline[-1]["id_str"]
    return tweets


if __name__ == "__main__":
    read_token(TOKEN_PATH)

    twitter = OAuth1Session(CK, CS, AK, AS)
    # 場合によって以下を変更
    since = datetime(2019, 6, 1, 0, 0, 0).timetuple()
    until = datetime(2019, 6, 3, 0, 0, 0).timetuple()
    tweets = search("ユーザー名", since, until)
    for tweet in tweets:
        tw_time = time_convert(tweet["created_at"])
        print(tweet["text"], "{}-{}-{}".format(tw_time.tm_year,
                                               tw_time.tm_mon, tw_time.tm_mday))
