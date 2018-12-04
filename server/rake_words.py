import os
import re
from rake_nltk import Rake
from nltk.corpus import stopwords
from pymystem3 import Mystem
from string import punctuation

from util import RESOURCE_DIR

adj_endings_male_hard = ['ый']
adj_endings_male_soft = ['ий']
adj_endings_female_hard = ['ая']
adj_endings_female_soft = ['яя']
adj_endings_neuter_hard = ['ое']
adj_endings_neuter_soft = ['ее']
adj_endings_many_hard = ['ые']
adj_endings_many_soft = ['ие']

class RakeRussian:
    stem = Mystem()

    def __init__(self):
        self.stops = []
        self.phrases = []
        self.right_phrases = []
        self.counter = None

        with open(os.path.join('..', RESOURCE_DIR, 'rake_stops.txt'), 'r', encoding='utf-8') as f:
            line = f.readline()
            while line is not None and len(line) != 0:
                self.stops.append(line.strip("\n"))
                line = f.readline()
        with open(os.path.join('..', RESOURCE_DIR, 'simple_words.txt'), 'r', encoding='utf-8') as f:
            self.simple_words = [s.strip() for s in f.readlines()]

        todel = []
        todel.extend(self.stops)
        todel.extend(list(stopwords.words("russian")))
        todel = list(set(todel))
        self.r = Rake(todel, punctuations=punctuation, language="russian")

    def get_words(self, text: str, n=1, k=float('inf')):
        self.r.extract_keywords_from_text(text)
        phrases = self.r.get_ranked_phrases()
        todel = []
        todel.extend(self.stops)
        todel.extend(list(stopwords.words("russian")))
        todel = list(set(todel))
        todel = [" " + w + " " for w in todel if w != '']
        phr = ''
        n_phrases = []
        for phrase in phrases:
            for word in phrase.split(" "):
                analysis = self.stem.analyze(word)
                if ('analysis' in analysis[0] and len(analysis[0]['analysis']) != 0
                        and (('gr' in analysis[0]['analysis'][0] and analysis[0]['analysis'][0]['gr'][0] == 'V')
                             or ('lex' in analysis[0]['analysis'][0] and (
                                        analysis[0]['analysis'][0]['lex'] == "суть" or
                                        analysis[0]['analysis'][0]['lex'] == "наличие")))):  # search verbs
                    if phr != '':
                        n_phrases.append(phr.strip())
                    phr = ''
                    continue
                if 'analysis' in analysis[0]:
                    phr += ' ' + word
            if phr != '':
                n_phrases.append(phr.strip())
            phr = ''
        self.phrases = [phrase for phrase in n_phrases if k >= len(phrase.split(" ")) >= n]

        texxt = text
        for elem in punctuation:
            texxt = texxt.replace(elem, " ")
        for elem in todel:
            texxt = texxt.replace(elem, " ")
        texxt = re.sub(" +", " ", texxt)
        texxt = texxt.replace("\n", " ")
        texxt = texxt.lower()
        self.clear_words(texxt)

    def clear_words(self, texxt):
        phrases = []
        for phrase in self.phrases:
            correct = True
            size = len(phrase.split(" "))
            for word in phrase.split(" "):
                analysis = self.stem.analyze(word)
                if 'analysis' in analysis[0] \
                        and len(analysis[0]['analysis']) != 0 \
                        and 'gr' in analysis[0]['analysis'][0] \
                        and ((analysis[0]['analysis'][0]['gr'][0] != 'S' and analysis[0]['analysis'][0]['gr'][0] != 'A')
                             or analysis[0]['analysis'][0]['gr'][:3] == "ADV"
                             or analysis[0]['analysis'][0]['gr'][:3] == "APR"
                             or (size == 1 and analysis[0]['analysis'][0]['gr'][0] != 'S')):
                    correct = False
                    break
            if correct:
                phrases.append(phrase)
        counter = [0] * len(self.phrases)
        for phrase in enumerate(phrases):
            counter[phrase[0]] = texxt.count(phrase[1])

        self.counter = counter
        self.phrases = phrases
        self.stem_phrases()

    def stem_phrases(self):
        new_phrases = []
        for phrase in self.phrases:
            words = phrase.split(" ")
            words2 = [''] * len(words)
            wor = [''] * len(words)
            objn = 0
            adjn = 0
            finw = [''] * len(words)
            for word in enumerate(words):
                a = self.stem.analyze(word[1])
                if len(a[0]['analysis']) > 0:
                    if "муж" in a[0]['analysis'][0]['gr']:
                        words2[word[0]] = (a[0]['analysis'][0]['lex'], "м")
                    elif "жен" in a[0]['analysis'][0]['gr']:
                        words2[word[0]] = (a[0]['analysis'][0]['lex'], "ж")
                    elif "сред" in a[0]['analysis'][0]['gr']:
                        words2[word[0]] = (a[0]['analysis'][0]['lex'], "с")
                    if "мн" in a[0]['analysis'][0]['gr']:
                        words2[word[0]] = (a[0]['analysis'][0]['lex'], "мн")
                    if "A=" in a[0]['analysis'][0]['gr']:
                        wor[word[0]] = 'A'
                        adjn += 1
                    elif "S," in a[0]['analysis'][0]['gr']:
                        wor[word[0]] = 'S'
                        objn += 1
                else:
                    words2[word[0]] = (a[0]['text'], None)
                    wor[word[0]] = 'N'
            if objn == 1:
                for w in enumerate(wor):
                    if w[1] == "S":
                        finw[w[0]] = words2[w[0]][0]
                    else:
                        finw[w[0]] = self.adj_to_gender(words2[w[0]][0], words2[w[0]][1])
            else:
                meet_s = False
                for i in range(len(words)):
                    if not meet_s:
                        if wor[i] != 'S':
                            finw[i] = self.adj_to_gender(words2[i][0], words2[i][1])
                        else:
                            finw[i] = words2[i][0]
                        if wor[i] == 'S':
                            meet_s = True
                    else:
                        finw[i] = words[i]
            new_phrases.append(" ".join(finw))
        self.right_phrases = new_phrases

    def get_clear_phrases(self):
        return self.phrases

    @staticmethod
    def is_ending(ending):
        if (ending in adj_endings_female_hard
                or ending in adj_endings_female_soft
                or ending in adj_endings_male_hard
                or ending in adj_endings_male_soft
                or ending in adj_endings_neuter_hard
                or ending in adj_endings_neuter_soft
                or ending in adj_endings_many_hard
                or ending in adj_endings_many_soft):
            return True
        else:
            return False

    def stemm(self, adjective):
        if len(adjective) < 3:
            return adjective
        if self.is_ending(adjective[-3:]):
            return adjective[:-3]
        if self.is_ending(adjective[-2:]):
            return adjective[:-2]
        return adjective

    def adj_to_gender(self, adjective, gender):
        stem = self.stemm(adjective)
        ending = adjective[len(stem):]
        if gender is None:
            return adjective
        if gender == 'м':
            return adjective
        if ending in adj_endings_male_hard:
            if gender == 'ж':
                return stem + adj_endings_female_hard[0]
            elif gender == 'с':
                return stem + adj_endings_neuter_hard[0]
            else:
                return stem + adj_endings_many_hard[0]
        if ending in adj_endings_male_soft:
            if stem[-1:] in ['г', 'к', 'х', 'ц']:
                if gender == 'ж':
                    return stem + adj_endings_female_hard[0]
                elif gender == 'с':
                    return stem + adj_endings_neuter_hard[0]
                else:
                    return stem + adj_endings_many_soft[0]
            if gender == 'ж':
                return stem + adj_endings_female_soft[0]
            elif gender == 'с':
                return stem + adj_endings_neuter_soft[0]
            else:
                return stem + adj_endings_many_soft[0]
        return adjective
