import gensim
import logging
import numpy as np

# http://ling.go.mail.ru/static/models/ruscorpora.model.bin.gz
WORD2VEC_MODEL_FILE = 'C:/TEMP/data/ruscorpora.model.bin.gz'


def load_w2v_model(file_name: str):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    w2v_model = gensim.models.Word2Vec.load_word2vec_format(file_name, binary=True, encoding='utf-8')
    print("word2vec model '%s' loaded" % file_name)
    return w2v_model


def semantic_density(bag: list, w2v_model, unknown_coef=0.0) -> float:
    sim_sum = 0.0
    divisor = 0
    # weight_sum = 0.0
    for i in range(len(bag)):
        for j in range(i + 1, len(bag)):
            if bag[i] != bag[j]:
                divisor += 1
                # weight = 1 / (j - i)
                # weight_sum += weight
                try:
                    # sim_sum += w2v_model.similarity(bag[i], bag[j]) # * weight
                    sim_sum += np.dot(w2v_model[bag[i]], w2v_model[bag[j]]) # vectors already normalized
                except:
                    sim_sum += unknown_coef # * weight
    if divisor > 0:
        return sim_sum / divisor # / weight_sum
    else:
        return 0.0


def semantic_similarity_fast(bag1, bag2: list, w2v_model) -> float:
    mx1 = []
    for i in range(len(bag1)):
        try:
            mx1.append(w2v_model[bag1[i]])
        except:
            pass
    mx2 = []
    for i in range(len(bag2)):
        try:
            mx2.append(w2v_model[bag2[i]])
        except:
            pass
    if len(mx1) > 0 and len(mx2) > 0:
        return np.sum(np.dot(np.vstack(mx1), np.vstack(mx2).T)) / (len(bag1) * len(bag2))
    else:
        return 0.0


def semantic_similarity(bag1, bag2: list, w2v_model, unknown_coef=0.0) -> float:
    if len(bag1) == 0 or len(bag2) == 0:
        return 0.0
    sim_sum = 0.0
    for i in range(len(bag1)):
        for j in range(len(bag2)):
            try:
                # sim_sum += w2v_model.similarity(bag1[i], bag2[j])
                sim_sum += np.dot(w2v_model[bag1[i]], w2v_model[bag2[j]]) # vectors already normalized
            except:
                sim_sum += unknown_coef
    return sim_sum / (len(bag1) * len(bag2))


def semantic_association(bag: list, w2v_model, topn=10) -> list:
    positive_lst = [w for w in bag if w in w2v_model.vocab]
    if len(positive_lst) > 0:
        assoc_lst = w2v_model.most_similar(positive=positive_lst, topn=topn)
        return [a[0] for a in assoc_lst]
    else:
        print('empty association for bag:', bag)
        return ['пустота_S']






