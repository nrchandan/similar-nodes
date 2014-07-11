import json
from pprint import pprint
from collections import Counter, defaultdict

from stopwords import ignore_keys
from settings import MIN_DISTINCT, MAX_DISTINCT_PCT, SEARCH_TERMS, \
    SEARCH_TYPE, THRESHOLD_SIMILARITY_SCORE


def reduce_dimensions(instances):
    '''Remove attributes that are too common or too rare (e.g. unique IDs
       are too rare, account info are too common.)
    '''
    filter_out = []
    # size = len(instances)
    size = Counter()
    all_values = defaultdict(set)
    for instance in instances:
        for key, value in instance.items():
            all_values[key].add(value)
            size.update([key])
    for key, value in all_values.items():
        if key == 'instanceId':
            continue
        if 100 * len(value) // size[key] > MAX_DISTINCT_PCT or \
           len(value) < MIN_DISTINCT:
            filter_out.append(key)
    for instance in instances:
        for key in filter_out:
            instance.pop(key, None)


def flatten(instances):
    '''Return a flat and cleaned up copy of instances dictionary. Assuming
    depth level 2 (at most 1 dictionary/list present)
    '''
    flat_list = []
    for instance in instances:
        flat = {}
        for i in instance.keys():
            if i in ignore_keys:
                continue
            if isinstance(instance[i], dict):
                for key in instance[i].keys():
                    flat[(i, key)] = instance[i][key]
            elif i == 'tags':
                for d in instance[i]:
                    if d['key'] != 'kseq':
                        flat[('tags', d['key'])] = d['value']
            elif i == 'blockDeviceMappings':
                d = summarize_block_devices(instance[i])
                for key, value in d.items():
                    flat[key] = value
            else:
                flat[i] = instance[i]
        flat_list.append(flat)
    return flat_list


def summarize_block_devices(blocks):
    '''Roll up information of block devices into two key, value pairs.
    Round off the results to reduce spread. Rounding off mechanism needs to be
    smarter (use statistical approach).'''
    count = len(blocks)
    count = roundoff(count)
    size = sum([block['volume']['size'] for block in blocks])
    size = roundoff(size)
    return {'blockDevicesCount': count, 'blockDevicesSize': size}


def roundoff(n):
    '''Custom roundoff function.
    >>> roundoff(12)
    10
    >>> roundoff(137)
    140
    >>> roundoff(1310)
    1300
    '''
    if n <= 10:
        return n
    if 10 < n <= 1000:
        return int(round(n, -1))
    elif 1000 < n < 10000:
        return int(round(n, -2))
    else:
        return int(round(n, -3))


def TF(instances):
    '''Returns a counter object representing Terms Frequency'''
    tf = Counter()
    for instance in instances:
            tf.update(instance.items())
    return tf


def search(instances, terms, kind='all'):
    '''Returns subset of instances matching search terms. Search can be 'all'
    (AND) or 'any' (OR).
    '''
    def all_terms_matched(instance):
        def term_matched(term):
            return term in instance.values()
        return kind(map(term_matched, terms))
    kind = all if kind == 'all' else any
    return filter(all_terms_matched, instances)


def IDF(corpus_freq, search_freq):
    '''Apply Inverse Document Frequency approach for normalization'''
    result = {}
    for key in search_freq.keys():
        result[key] = round(search_freq[key] * 100.0 / corpus_freq[key], 2)
    return result


def score(instance, group):
    '''Rate an instance against a group of instances (represented by TFIDF).
    Higher absolute score means closely related.
    '''
    #return sum([group[item] for item in instance.items()
    #if item in group.keys()])
    score = 0
    cause = []
    for item in instance.items():
        if item in group.keys():
            score += group[item]
            if group[item] > 10:
                cause.append({item: group[item]})
    return (round(score, 2), cause)


def similar_nodes(instances):
    flat_ins = flatten(instances)
    reduce_dimensions(flat_ins)
    kind = 'all' if SEARCH_TYPE == 'ALL' else 'any'
    search_result = search(flat_ins, SEARCH_TERMS, kind=kind)
    norm = IDF(TF(flat_ins), TF(search_result))
    scores = [(score(instance, norm), instance['instanceId'])
              for instance in flat_ins]
    scores.sort(reverse=True)

    result = []
    for instance in scores[len(search_result):len(search_result) + 5]:
        if instance[0][0] < THRESHOLD_SIMILARITY_SCORE:
            break
        result.append(instance)
    return result


def main():
    d = json.loads(open('instances.json').read())
    instances = d['success']['body']['objects']
    pprint(similar_nodes(instances))

if __name__ == '__main__':
    main()
