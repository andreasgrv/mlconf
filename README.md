## [![Build Status](https://api.travis-ci.org/andreasgrv/mlconf.svg?branch=master)](https://travis-ci.org/andreasgrv/mlconf) mlconf 

Because in machine learning sensible defaults don't last long. Especially when choosing
hyperparameters:

![Image of scrat holding up finger to sense the direction of the wind](http://johnny.overfit.xyz/scrat-air.jpg)
<!-- scrat loves acorns -->

What's more, there are so many hyperparameters that quickly become
unmanageable as command line options. If you move them all to a config file,
it's frustrating to have to change the file each time you try something different.
So why not enjoy the best of both worlds?

**Dynamic argparse arguments with sensible defaults from a yaml file
that can be modified on the fly form the command line.**

### mlconf in a nutshell

* Dynamically set a lot of sane defaults from a [YAML](http://yaml.org) file.
* Be able to override any number of the defaults from the command line.
* Make the returned object easily accessible using . notation.
* Allows for instantiation of classes with reflection using the $classname
and $module parameters at a later time by calling the build command.
<!-- scrat lived in a tree during the ice age -->

### Installation
>
	pip install mlconf

### Example

Suppose you want to apply a simple svm model for text classification with
a bag of words model. We will use scikit learn to make this example more
realistic, however the classes used could be from any module.
Here are some toy settings:

``` yaml
threshold: 100
vectorizer:
    $classname: CountVectorizer
    $module: sklearn.feature_extraction.text
    strip_accents: 'unicode'
    lowercase: False
    vocabulary: '?' # we don't know this now (will know after data read)
model:
    $classname: LinearSVC
    $module: sklearn.svm
    penalty: 'l2'
    loss: 'hinge'
    C: 10
```

Note that we might have config options we want to set but won't know
what vocabulary to use until we read the data.

``` python
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
```

Run the above with the following command. Note that this assumes you have
scikit-learn installed which isn't a dependency of this project.

>
	python tests/example.py --load_blueprint tests/data/model.yaml

Output on my machine:

>
	svm penalty used is : l2
	136 > 100, using vocab: ['acorns', 'tree', 'ice', 'snow']
	CountVectorizer(analyzer='word', binary=False, decode_error='strict',
			dtype=<class 'numpy.int64'>, encoding='utf-8', input='content',
			lowercase=False, max_df=1.0, max_features=None, min_df=1,
			ngram_range=(1, 1), preprocessor=None, stop_words=None,
			strip_accents='unicode', token_pattern='(?u)\\b\\w\\w+\\b',
			tokenizer=None, vocabulary=['acorns', 'tree', 'ice', 'snow'])
	LinearSVC(C=10.0, class_weight=None, dual=True, fit_intercept=True,
		 intercept_scaling=1, loss='hinge', max_iter=1000, multi_class='ovr',
		 penalty='l2', random_state=None, tol=0.0001, verbose=0)
	[False  True]

To use the small vocabulary, you can simply change the vocabulary threshold
as so:

>
	python tests/example.py --load_blueprint tests/data/model.yaml --threshold 1000

Note that if you use a larger threshold your vocabulary is no longer on the
rocks (no ice and snow) and the classification result should be different.

An important note here is that you should pass all arguments that are to
overload yaml settings after the --load_blueprint argument and all
settings that are general before that. Eg. --input_file should be set
before --load_blueprint and --model.C after.

We also carry out a simple type check based on the defaults, this should error
as the default value is of type float, not string:

>
	python tests/example.py --load_blueprint tests/data/model.yaml --model.C string

While the following will change the svm C to 0.1

>
	python tests/example.py --load_blueprint tests/data/model.yaml --model.C 0.1

### Tests

Tests are run using tox. Versions of pythont tested are Python 2.7, 3.4 and 3.6.
To run tests, clone the repository, change directory to the root directory and:

>   
	pip install requirements.txt
	pip install .
	tox

### License

3 clause BSD, see LICENSE.txt file

### Credits

Image is a [neural styled](https://tenso.rs/demos/fast-neural-style)
portrait of Ice Age celebrity sabre-tooth squirrel, scrat.
