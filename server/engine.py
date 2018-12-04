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

def get_verbs_from_db():
    sql = "SELECT verb_weight.verb_n, verb_weight.weight FROM verb_weight"
    return db.query(sql)

def get_nouns_from_db():
    sql = "SELECT object_weight.name_rel, object_weight.weight_rel FROM object_weight"
    return db.query(sql)

def get_connectors_from_db():
    sql = "SELECT rusmarker2.markername FROM rusmarker2 WHERE rusmarker2.relname IN " \
          "('aa', 'Restatement', 'Elaboration', 'Concession', 'Evidence')"
    return db.query(sql)

# # Counts weight of sentence by formula.
# def count_weight(sent, use_miss=False):
#     stem = Mystem()
#     lemmas = stem.analyze(sent)
#     final_weight = 0
#     final_obj = 0
#     final_verb = 0
#     count_obj = 0
#     count_verb = 0
#     phrases = {}
#     for lemma in lemmas:
#         if "analysis" in lemma:
#             if len(lemma['analysis']) <= 0:
#                 continue
#             type = (lemma['analysis'][0]['gr'].split(','))[0]
#             if type == 'V':
#                 to_lookup = lemma['analysis'][0]['lex']
#                 if to_lookup[len(to_lookup) - 2:] == 'ся':
#                     to_lookup = to_lookup[:len(to_lookup) - 2]
#             else:
#                 to_lookup = lemma['text']
#         else:
#             continue
#         if to_lookup in self.weights_verb:
#             final_verb += self.weights_verb[to_lookup]
#             phrases[to_lookup] = self.weights_verb[to_lookup]
#             count_verb += 1
#         elif to_lookup in self.weights_obj:
#             final_obj += self.weights_obj[to_lookup]
#             phrases[to_lookup] = self.weights_obj[to_lookup]
#             count_obj += 1
#     for name in self.weights_obj:
#         weight = self.weights_obj[name]
#         if name in sent and len(name.split(' ')) > 1:
#             final_obj += weight
#             phrases[name] = weight
#             count_obj += 1
#     local_obj = 0
#     if use_miss:
#         for word in self.miss:
#             if word in sent:
#                 final_obj -= self.miss[word]
#                 local_obj += 1
#     if count_verb != 0:
#         final_weight += float(final_verb) / len(self.weights_verb)
#     if count_obj != 0:
#         final_weight += float(final_obj) / (len(self.weights_obj) + local_obj)
#     return final_weight, phrases
