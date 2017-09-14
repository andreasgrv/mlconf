import mlconf

parser = mlconf.ArgumentParser(description='A text classifier.')
parser.add_argument('-i', '--input_file', default='README.md',
                    dest='infile') # default for convenience
parser.add_argument('--load_blueprint', action=mlconf.YAMLLoaderAction)
bp = parser.parse_args() # This returns a Blueprint instance with . access

# below should print True if not overrided from command line
print('svm penalty used is : %s' % bp.model.penalty)

# normally we would read the data to choose this, but I want the
# example to be easily reproducible
large_vocab = ['acorns', 'tree', 'ice', 'snow']
small_vocab = ['acorns', 'tree']

with open(bp.infile, 'r') as f:
    lines = f.readlines()
    num_lines = len(lines)
    if num_lines > bp.threshold:
        print('%d > %d, using vocab: %r'
              % (num_lines, bp.threshold, large_vocab))
        bp.vectorizer.vocabulary = large_vocab
    else:
        print('%d <= %d, using vocab: %r'
              % (num_lines, bp.threshold, small_vocab))
        bp.vectorizer.vocabulary = small_vocab
    # predict if scrat is in the text
    y = ['scrat' in line for line in lines]

built_bp = bp.build() # instantiate the classes on a copy of the blueprint
print(built_bp.vectorizer) # this is now an instance of CountVectorizer
built_bp.model.fit(built_bp.vectorizer.fit_transform(lines), y)
print(built_bp.model) # this is now a fit instance of LinearSVC
# do stuff with bp.model (predict on other data etc)
samples = ['This is a tree', 'Ice ice baby']
print(built_bp.model.predict(built_bp.vectorizer.transform(samples)))
