import json
import semantics as sem

# data model format
#   {'poems': [str, str, ...]
#    'bags': [list, list, ...]
#    'vocabulary': {word: count, ...}
#    'density': [float, float, ...]
#    'associations: [list, list, ...]
#    'rates': [float, float, ...]       <- markupform module


def read_data_model(file_name: str) -> dict:
    file = open(file_name, mode='r', encoding='utf-8')
    return json.load(file)


def write_data_model(file_name: str, data_model: dict):
    file = open(file_name, mode='w', encoding='utf-8')
    json.dump(data_model, file, separators=(',', ':'), ensure_ascii=False)


def read_poems(file_name: str) -> list:
    file = open(file_name, encoding='utf-8')
    lines = file.readlines()
    poems = []
    poem = ""
    for line in lines:
        if len(line.strip()) == 0:
            if len(poem.strip()) > 0:
                poems.append(poem.lower())
                poem = ""
        else:
            poem += line
    return poems


def make_bags(texts: list) -> (list, dict):
    bags = []
    vocabulary = {}
    for txt in texts:
        bag = []  # {}
        words = sem.canonize_words(txt.split())
        for w in words:
            if w not in bag:
                bag.append(w)  # bag[w] = bag.get(w, 0) + 1
            vocabulary[w] = vocabulary.get(w, 0) + 1
        bags.append(bag)
    return bags, vocabulary


def empty_model() -> dict:
    return {'poems'       : [],
            'bags'        : [],
            'vocabulary'  : {},
            'density'     : [],
            'associations': [],
            'rates'       : []}


def make_poems_model(file_name: str, semantics=True) -> dict:
    print("making poems model...")
    poems = read_poems(file_name)
    print('poem count:', len(poems))
    bags, voc = make_bags(poems)
    sa = []
    sd = []
    if semantics:
        print("loading w2v_model...")
        w2v_model = sem.load_w2v_model(sem.WORD2VEC_MODEL_FILE)
        print("adding semantics to model...")
        sd = [sem.semantic_density(bag, w2v_model, unknown_coef=-0.001) for bag in bags]
        sa = [sem.semantic_association(bag, w2v_model) for bag in bags]
    rates = [0.0 for _ in range(len(poems))]
    print("model created")
    return {'poems'       : poems,
            'bags'        : bags,
            'vocabulary'  : voc,
            'density'     : sd,
            'associations': sa,
            'rates'       : rates}


def append_model_to_model(head_model, tail_model):
    for w in tail_model['vocabulary'].keys():
        head_model['vocabulary'][w] = head_model['vocabulary'].get(w, 0) + tail_model['vocabulary'][w]

        poems_len = len(tail_model['poems'])
        dens_len = len(tail_model['density'])
        assoc_len = len(tail_model['associations'])
        rates_len = len(tail_model['rates'])
    for i in range(poems_len):
        if tail_model['bags'][i] not in head_model['bags']:
            head_model['poems'].append(tail_model['poems'][i])
            head_model['bags'].append(tail_model['bags'][i])
            if dens_len == poems_len:
                head_model['density'].append(tail_model['density'][i])
            if assoc_len == poems_len:
                head_model['associations'].append(tail_model['associations'][i])
            if rates_len == poems_len:
                head_model['rates'].append(tail_model['rates'][i])
        else:
            print('<!!!>\n', tail_model['poems'][i])


def print_poems_model(poems_model):
    print("poems: ", poems_model['poems'])
    print("bags: ", poems_model['bags'])
    print("vocabulary: ", poems_model['vocabulary'])
    print("density: ", poems_model['density'])
    print("associations: ", poems_model['associations'])
    print("rates: ", poems_model['rates'])


def load_poems_model(file_name, w2v_model, vectorize=True):
    pmodel = read_data_model(file_name)
    print("loading model...")
    if vectorize:
        print("vectorizing model...")
        pmodel['matrices'] = [sem.bag_to_matrix(bag, w2v_model) for bag in pmodel['bags']]
        pmodel['a_matrices'] = [sem.bag_to_matrix(bag, w2v_model) for bag in pmodel['associations']]
    print("poems model '%s' loaded" % file_name)
    return pmodel


def save_poems_to_file(poem_model, file_name):
    f_out = open(file_name, mode='w', encoding='utf-8')
    for poem in poem_model['poems']:
        f_out.write(poem + '\n')


if __name__ == "__main__":
    poems_model = make_poems_model("poems_33000.txt")
    # print(pm)
    pm_file = "poems_model_big.dat"
    write_data_model(pm_file, poems_model)
    print("model was saved to file '%s'" % pm_file)
    # print_poems_model(pm)

# import data_model as dm
# pm = dm.read_data_model("poems_model.dat")
# print_poems_by_density(pm)



