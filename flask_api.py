from werkzeug.wrappers import Request, Response
from flask import Flask, jsonify
from flask_cors import CORS
import json

consumer_key = ''
consumer_secret = ''
access_token = ''
access_secret = ''

app = Flask(__name__)
CORS(app)


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/api/twitter', methods=['GET'])
def get_twitter_data():
    import tweepy
    from tweepy import OAuthHandler

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)
    user = api.me()

    data = {
        'screen_name': user.screen_name,
        'name': user.name,
        'location': user.location,
        'followers': str(user.followers_count),
        'created': str(user.created_at),
        'description': str(user.description),
        'profile_image': str(user.profile_image_url)
    }

    return jsonify(data)


@app.route('/api/twitter/datafrequency', methods=['GET'])
def process_twitter_data():
    import operator
    from collections import Counter
    from lab3_utils import preprocess, stop

    fname = 'Lab3.CaseStudy.json'
    with open(fname, 'r') as f:
        count_all = Counter()
        for line in f:
            tweet = json.loads(line)
            # Create a list with all the terms
            terms_hash = [term for term in preprocess(tweet['text']) if term.startswith('#') and term not in stop]
            count_all.update(terms_hash)
    # Print the first 10 most frequent words
    data = {
        'file_name': fname,
        'words': count_all.most_common(15)
    }
    return jsonify(data)


@app.route('/api/twitter/datamap', methods=['GET'])
def process_twitter_data_map():
    fname = 'Lab3.CaseStudy.json'
    with open(fname, 'r') as f:
        geo_data = {
            "type": "FeatureCollection",
            "features": []
        }
        for line in f:
            tweet = json.loads(line)
            if tweet['coordinates']:
                geo_json_feature = {
                    "type": "Feature",
                    "geometry": tweet['coordinates'],
                    "properties": {
                        "text": tweet['text'],
                        "created_at": tweet['created_at']
                    }
                }
                geo_data['features'].append(geo_json_feature)
    return jsonify(geo_data)


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 8954, app)