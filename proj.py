import tweepy
import json
import sys
import warnings
from textblob import TextBlob
from imdb import IMDb
import sentiment_mod as senti
import mysql.connector as db  # Python 3 compatible

warnings.filterwarnings('ignore')

# ---------------------------------------------------
# 1. Read credentials from the properties file
# ---------------------------------------------------
def readPropertyFile():
    with open('properties', 'r') as f:
        auth = json.load(f)
        return auth

propertie = readPropertyFile()

# ---------------------------------------------------
# 2. Twitter authentication using Bearer Token
# ---------------------------------------------------
def getAuth():
    try:
        client = tweepy.Client(
            bearer_token=propertie['bearer_token'],
            wait_on_rate_limit=True
        )
        print("✅ Twitter API authentication successful.")
        return client
    except Exception as e:
        print("❌ Twitter authentication failed:", e)
        sys.exit(-1)

api = getAuth()

# ---------------------------------------------------
# 3. MySQL Database connection
# ---------------------------------------------------
def dbConnection():
    try:
        conn = db.connect(
            host=propertie['db_host'],
            user=propertie['db_user'],
            password=propertie['db_passwd'],
            database=propertie['db_name'],
            charset="utf8"
        )
        print("✅ Database connection successful.")
        return conn
    except Exception as e:
        print("❌ Database connection failed:", e)
        sys.exit(-1)

conn = dbConnection()

# ---------------------------------------------------
# 4. Database utility functions
# ---------------------------------------------------
def saveData(searchQuery, textblobRating, nltkRating, imdbRating, nltkPos, nltkNeg, textblobPos, textblobNeg):
    cursor = conn.cursor()
    sql = """
        INSERT INTO movies(name,textblobRating,nltkRating,imdbRating,nltkPosCount,nltkNegCount,textblobPosCount,textblobNegCount)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (searchQuery, textblobRating, nltkRating, imdbRating, nltkPos, nltkNeg, textblobPos, textblobNeg))
    conn.commit()
    return cursor.rowcount

def saveTweets(name, tweetList):
    data = [(name, str(t.id), t.text) for t in tweetList]
    cursor = conn.cursor()
    sql = "INSERT IGNORE INTO tweets(name,id,description) VALUES (%s, %s, %s)"
    cursor.executemany(sql, data)
    conn.commit()
    return cursor.rowcount

def getTweets(hashTag, offset, count):
    cursor = conn.cursor()
    sql = "SELECT * FROM tweets WHERE name=%s LIMIT %s,%s"
    cursor.execute(sql, (hashTag, offset, count))
    return cursor.fetchall()

def getDBCount(searchQuery):
    cursor = conn.cursor()
    sql = "SELECT COUNT(1) FROM tweets WHERE name=%s"
    cursor.execute(sql, [searchQuery])
    return cursor.fetchone()[0]

# ---------------------------------------------------
# 5. Sentiment calculations
# ---------------------------------------------------
def calculateSentiment(tweet):
    return TextBlob(tweet).sentiment.polarity

def processTweets(searchQuery):
    print("🔄 Processing tweets...")
    count = 50
    offset = 0
    posTweets = 0
    negTweets = 0
    nltkPos = 0
    nltkNeg = 0
    totalCount = getDBCount(searchQuery)

    while offset < totalCount:
        tweets = getTweets(searchQuery, offset, count)
        for each in tweets:
            polarity = round(calculateSentiment(each[2]), 1)
            nltkRes = senti.sentiment(each[2])
            if nltkRes:
                if nltkRes[1] > 0.5:
                    if nltkRes[0] == "pos":
                        nltkPos += 1
                    elif nltkRes[0] == "neg":
                        nltkNeg += 1
            if polarity > 0:
                posTweets += 1
            elif polarity < 0:
                negTweets += 1
        offset += count

    rating = (posTweets/(posTweets + negTweets))*10 if (posTweets + negTweets) > 0 else 0
    nltkRating = (nltkPos/(nltkPos + nltkNeg))*10 if (nltkPos + nltkNeg) > 0 else 0
    return round(rating,1), round(nltkRating,1), nltkPos, nltkNeg, posTweets, negTweets

# ---------------------------------------------------
# 6. IMDB movie rating
# ---------------------------------------------------
imdb = IMDb()
def getLatestMovieByNameFromIMDB(searchQuery):
    actual_movies = []
    maxYear = 0
    rating = 0
    try:
        movies = imdb.search_movie(searchQuery)
        for each in movies:
            if searchQuery.lower() == each["title"].lower():
                actual_movies.append((each.movieID, each["title"], each.get("year", 0)))
        id = None
        for each in actual_movies:
            if each[2] > maxYear:
                maxYear = each[2]
                id = each[0].strip()
        if id:
            movie = imdb.get_movie(id)
            rating = movie.get("rating", 0)
    except Exception as e:
        print("⚠️ Exception in fetching movie data:", e)
    return rating

# ---------------------------------------------------
# 7. Fetching and saving tweets
# ---------------------------------------------------
def searchTwitter(searchQuery):
    print(f"🔍 Searching Twitter for '{searchQuery}' ...")
    maxTweets = 200  # limit to 200 recent tweets
    tweetCount = 0
    tweetList = []

    try:
        response = api.search_recent_tweets(
            query=searchQuery,
            max_results=100,
            tweet_fields=["id", "text", "lang"]
        )

        if response.data:
            for tweet in response.data:
                if tweet.lang == "en":
                    tweetList.append(tweet)
            savedCount = saveTweets(searchQuery, tweetList)
            tweetCount += savedCount
            print(f"✅ Saved {savedCount} tweets to DB.")
        else:
            print("⚠️ No tweets found.")
    except Exception as e:
        print("❌ Error fetching tweets:", e)

    # Process sentiments
    textblobRating, nltkRating, nltkPos, nltkNeg, textblobPos, textblobNeg = processTweets(searchQuery)
    imdbRating = getLatestMovieByNameFromIMDB(searchQuery)
    saveData(searchQuery, textblobRating, nltkRating, imdbRating, nltkPos, nltkNeg, textblobPos, textblobNeg)
    print("✅ Processing completed.")
# ---------------------------------------------------
# 8. Get movie data from the database
# ---------------------------------------------------
def getMovieFromDB(searchQuery):
    try:
        cursor = conn.cursor()
        sql = "SELECT * FROM movies WHERE name=%s"
        cursor.execute(sql, [searchQuery])
        return cursor.fetchall()
    except Exception as e:
        print("⚠️ Error fetching movie from DB:", e)
        return []

# ---------------------------------------------------
# 9. Run test (optional)
# ---------------------------------------------------
if __name__ == "__main__":
    movie_name = input("Enter a movie name to analyze: ")
    searchTwitter(movie_name)
