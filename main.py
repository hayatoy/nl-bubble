# -*- coding: utf-8 -*-
from google.appengine.api import urlfetch
from google.appengine.api.app_identity import get_application_id
from flask import Flask, render_template, request, abort
from google.cloud import language
from google.cloud import bigquery
import json
import logging
app = Flask(__name__)


@app.route('/')
def mainpage():
    return render_template("main.html")


@app.route('/post', methods=['POST'])
def action():
    message = request.form.get('message', '')
    team = request.form.get('team', '')
    logging.info(u'Team:{}, {}'.format(team, message))

    if message != '' and team in ['A', 'B']:
        nl_client = language.Client()

        document = nl_client.document_from_text(message)
        sentiment_response = document.analyze_sentiment()
        score = sentiment_response.sentiment.score
        magnitude = sentiment_response.sentiment.magnitude

        insert_row_to_fb(message, team, score)
        insert_row_to_bq(message, team, score, magnitude)

        score_text = 'Positive!' if score > 0.2 else 'Neutral' if score > -0.2 else 'Negative..'

        return u'Score:{} {}'.format(score, score_text)
    else:
        return abort(400)


def insert_row_to_bq(message, team, score, magnitude):
    # initialize client and load table schema
    bq_client = bigquery.Client()
    dataset = bq_client.dataset('bubbles')
    table = dataset.table('devfest2017')
    table.reload()

    # insert rows into table
    table.insert_data([(message, team, score, magnitude)])


def insert_row_to_fb(message, team, score):
    app_id = get_application_id()
    url = 'https://{}.firebaseio.com/bubbles.json'.format(app_id)
    payload = json.dumps({'message': message,
                          'team': team,
                          'score': score,
                          'time': {'.sv': 'timestamp'}
                          })
    response = urlfetch.fetch(url=url,
                              method=urlfetch.POST,
                              payload=payload)
    logging.info(response.content)
