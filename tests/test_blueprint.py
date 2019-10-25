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

def test_order_preservation(tmp_path):
    filename = str(tmp_path / 'myyaml.yaml')

    data = {'d': 1,
            'e': 1,
            'b': 1,
            'f': 1,
            'a': 1,
            'c': 1}
    key_order = tuple(data.keys())

    bp = mlconf.Blueprint.from_dict(data)

    bp.to_file(filename)

    bp = mlconf.Blueprint.from_file(filename)
    loaded_key_order = tuple(bp.as_dict().keys())
    assert key_order == loaded_key_order
