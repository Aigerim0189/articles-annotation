from flask import Blueprint, render_template, request

from engine import split_text_into_sentences, \
    delete_background_sentences, \
    group_sentences, detailing
from rake_words import RakeRussian
from util import OUTPUT_DIR, RESOURCE_DIR
from util import get_indexed_dict_with

import os
import json
import collections

blueprint = Blueprint('blueprint', __name__,
                      static_folder="../client/dist",
                      template_folder="../client/static")

@blueprint.route('/', defaults={'path': ''})
@blueprint.route('/<path:path>')
def index(path):
    return render_template('index.html')

@blueprint.route('/process-initial-text', methods=['POST'])
def process_initial_text():
    text = request.json.get('text')
    with open(os.path.join('..', OUTPUT_DIR, 'initial_text.txt'), 'w', encoding='utf-8') as file:
        file.write(text)
    raw_sentences = get_indexed_dict_with(split_text_into_sentences(text))
    sentences = detailing(raw_sentences)
    sentences = delete_background_sentences(sentences)
    sentences = group_sentences(sentences)
    return json.dumps(sentences), 200

@blueprint.route('/process-rake', methods=['POST'])
def process_rake():
    text = request.json.get('text')
    rake_russian = RakeRussian()
    rake_russian.get_words(text)
    right_phrases = set(rake_russian.right_phrases)

    with open(os.path.join('..', RESOURCE_DIR, 'rake_key_stop.txt'), 'r', encoding='utf-8') as f:
        stop_keywords = f.readlines()
        result = [x for x in right_phrases if x not in stop_keywords]

    return json.dumps(result), 200
