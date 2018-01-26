from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from collections import Counter
from lab3_utils import preprocess, stop
import tweepy
from tweepy import OAuthHandler
import urllib.request
import base64
import googleapiclient.discovery

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


@app.route('/api/image', methods=['POST'])
def process_data_image():
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    urllib.request.install_opener(opener)
    url_image = request.form['url']
    print(url_image)
    img_path = '/tmp/image'
    urllib.request.urlretrieve(url_image, img_path)
    service = googleapiclient.discovery.build('vision', 'v1')

    data = []
    with open(img_path, 'rb') as image:
        image_content = base64.b64encode(image.read())
        service_request = service.images().annotate(body={
            'requests': [{
                'image': {
                    'content': image_content.decode('UTF-8')
                },
                'features': [{
                    'type': 'LABEL_DETECTION',
                    'maxResults': 5
                }]
            }]
        })
        # [END construct_request]
        # [START parse_response]
        response = service_request.execute()
        for result in response['responses'][0]['labelAnnotations']:
            data.append({'description': result['description'], 'score': result['score']})

    return jsonify(data)


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 8954, app)