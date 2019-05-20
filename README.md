## [![Build Status](https://api.travis-ci.org/andreasgrv/mlconf.svg?branch=master)](https://travis-ci.org/andreasgrv/mlconf) mlconf 

Because in machine learning, sensible defaults don't last long. Especially when choosing hyperparameters:

![Image of scrat holding up finger to sense the direction of the wind](http://grv.overfit.xyz/scrat-air.jpg)
<!-- scrat loves acorns -->

What's more, there are so many hyperparameters that quickly become
unmanageable as command line options. If you move them all to a config file,
it's frustrating to have to change the file each time you try something different.
So why not enjoy the best of both worlds?

**Dynamic argparse arguments with sensible defaults from a yaml file
that can be modified on the fly from the command line.**

### mlconf in a nutshell

* Dynamically set a lot of sane defaults from a [YAML](http://yaml.org) file.
* Be able to override any number of the defaults from the command line.
* Make the returned object easily accessible using . notation.
* Allows for instantiation of classes with reflection using the $classname
and $module parameters at a later time by using the blueprint's *build()* command.
<!-- scrat lived in a tree during the ice age -->

### Installation
>
	pip install mlconf

### Example

For example usage see [my post](http://grv.overfit.xyz/posts/mlconf).

### Tests

Tests are run using tox. Versions of python tested are Python 2.7, 3.4 and 3.6.
To run the tests, run the following:

>   
	git clone https://github.com/andreasgrv/mlconf
	cd mlconf
	pip install -r requirements.txt
	pip install .
	tox

### License

3 clause BSD, see LICENSE.txt file

### Credits

Image is a [neural styled](https://tenso.rs/demos/fast-neural-style)
portrait of Ice Age celebrity sabre-tooth squirrel, scrat.
