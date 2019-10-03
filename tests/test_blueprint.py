from collections import Counter
import mlconf


def test_pre_build():
    bp = mlconf.Blueprint.from_file('tests/data/example.yaml')
    assert(isinstance(bp.foo.counter, mlconf.Blueprint))


def test_build():
    bp = mlconf.Blueprint.from_file('tests/data/example.yaml')
    bp = bp.build()
    assert(isinstance(bp.foo.counter, Counter))


def test_build_no_copy():
    bp = mlconf.Blueprint.from_file('tests/data/example.yaml')
    bp.build(copy=False)
    assert(isinstance(bp.foo.counter, Counter))


def test_object_expansion():
    bp = mlconf.Blueprint.from_file('tests/data/example.yaml')
    contents = dict(**bp.foo.counter)
    assert(contents['a'] == 5)
    assert(contents['b'] == 3)
    assert(contents['$classname'] == 'Counter')
    assert(contents['$module'] == 'collections')
    contents = dict(**bp.foo)
    assert(isinstance(contents['counter'], mlconf.Blueprint))

def test_dict_equality():
    data = {'smoke': 3, 'on': ['t', 'h', 'e'], 'water': True}
    bp = mlconf.Blueprint.from_dict(data)
    assert(bp == data)
    data.pop('smoke')
    assert(bp != data)
