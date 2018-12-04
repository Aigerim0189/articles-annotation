import nltk.data
from database import db
from util import pick_first_if_exists, group_sentences_by_markers

def split_text_into_sentences(text):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = tokenizer.tokenize(text)

    return sentences

def detailing(sentences):
    sql = "SELECT rusmarker2.markername FROM rusmarker2 WHERE relname='Elaboration'"
    markers = list(map(pick_first_if_exists, db.query(sql)))
    sentences = group_sentences_by_markers(sentences, markers, flag=True)

    return sentences

def delete_background_sentences(sentences):
    markers = db.query("SELECT rusmarker2.markername FROM rusmarker2 WHERE relname='Background'")
    # Create copy to delete items from sentences while iterating
    copy = dict(sentences)
    s_keys = copy.keys()
    for key in s_keys:
        for marker in markers:
            if sentences[key].startswith(marker):
                del sentences[key]
                break

    return sentences

def group_sentences(sentences):
    sql = "SELECT rusmarker2.markername FROM rusmarker2 WHERE relname IN " \
          "('Contrast', 'Restatement')"
    markers = list(map(pick_first_if_exists, db.query(sql)))
    sentences = group_sentences_by_markers(sentences, markers)

    return sentences
