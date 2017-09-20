import mlconf

parser = mlconf.ArgumentParser(description='A text classifier.')
parser.add_argument('-i', '--input_file', default='README.md')
parser.add_argument('--load_blueprint', action=mlconf.YAMLLoaderAction)

conf = parser.parse_args() # This returns a Blueprint instance with . access

# set vocab for brevity, normally read from input
sm_vocab = ['acorns', 'tree']
lg_vocab = sm_vocab + ['ice', 'snow']

with open(conf.input_file, 'r') as f:
    lines = f.readlines()

conf.vectorizer.vocabulary = lg_vocab if len(lines) > conf.threshold else sm_vocab
print('Using vocab: %r\n' % conf.vectorizer.vocabulary)


print('%s\n' % conf.vectorizer)  # this is a Blueprint object
built_conf = conf.build()        # instantiate the classes on a copy

print('%s\n' % built_conf.vectorizer) # this is now an instance of CountVectorizer
X = built_conf.vectorizer.fit_transform(lines)

# target is to predict whether scrat is in the line of text
y = ['scrat' in line for line in lines]

built_conf.model.fit(X, y) # fit model

# Predict on other data
samples = ['This is a tree', 'Ice ice baby']
X_test = built_conf.vectorizer.transform(samples)
print('Predicted: %r' % built_conf.model.predict(X_test))
