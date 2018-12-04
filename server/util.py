OUTPUT_DIR = 'output'
RESOURCE_DIR = 'resource'

def pick_first_if_exists(row):
    if len(row) > 0:
        return row[0]
    else:
        return row

def group_sentences_by_markers(sentences, markers, flag=False):
    # Create copy to delete items from sentences while iterating
    copy = dict(sentences)
    if flag:
        s_keys = sorted(list(map(lambda x: int(x), copy.keys())))
    else:
        s_keys = copy.keys()
    prev_key = None
    marker_found = False
    for key in s_keys:
        key = str(key)
        for marker in markers:
            if sentences[key].startswith(marker) and prev_key is not None:
                new_key = prev_key + ', ' + key
                sentences[new_key] = sentences[prev_key] + ' ' + sentences[key]
                del sentences[prev_key]
                del sentences[key]
                prev_key = new_key
                marker_found = True
                break
        if not marker_found:
            prev_key = key
        marker_found = False

    return sentences

def get_indexed_dict_with(sentences):
    return dict((str(i + 1), sentences[i]) for i in range(len(sentences)))
