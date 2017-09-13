## mlconf

Because in machine learning sensible defaults don't last long.

![Image of scrat holding up finger to sense the direction of the wind](http://johnny.overfit.xyz/scrat-air.jpg)

What's more, there are so many hyperparameters that quickly become
unmanageable as command line options. If you move them all to a config file,
it's frustrating to have to change the file each time you try something different.
So why not enjoy the best of both worlds?

**Dynamic argparse arguments with sensible defaults
that can be overrided easily from the command line when needed.**

### What does mlconf do?

* Easily set a lot of sane defaults from a [YAML](http://yaml.org) file.
* Be able to override any number of the defaults from the command line.
* Make the returned object easily accessible using . notation.
* Allows for instantiation of classes using reflection using the _classname
and _module parameters at a later time by calling the build command.

### Why did you write this?

Machine learning has a *lot* of parameters one needs to set. Most importantly,
once you have found which parameters work well, you usually only modify few of
them. You need good defaults but also want the ability to change parameters
on the fly.

### Tests

Tests are run using tox. Clone the repository, change directory to the root directory and:

>   
	pip install requirements.txt
	pip install .
	tox

### Credits

Image is a [neural styled](https://tenso.rs/demos/fast-neural-style)
portrait of Ice Age celebrity sabre-squirrel, scrat.
