from collections import Counter
import yaml
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


def test_order_preservation_as_flat_dict(tmp_path):
    filename = str(tmp_path / 'myyaml.yaml')

    data = {'r': 1,
            'k': dict(a=5, c=dict(a=5, b=1, c=3), b=(3, 1), d=2),
            'b': (20, 3, 5),
            'z': dict(a=dict(a=5, b=1, c=3), b=1, c=2, d=5),
            'd': 1,
            'e': 1}

    with open(filename, 'w') as f:
        f.write(yaml.safe_dump(data, sort_keys=False, default_flow_style=False))

    bp = mlconf.Blueprint.from_file(filename)
    loaded_key_order = list(bp.as_flat_dict().keys())
    expected_order = ['r',
                      'k.a',
                      'k.c.a',
                      'k.c.b',
                      'k.c.c',
                      'k.b.0',
                      'k.b.1',
                      'k.d',
                      'b.0',
                      'b.1',
                      'b.2',
                      'z.a.a',
                      'z.a.b',
                      'z.a.c',
                      'z.b',
                      'z.c',
                      'z.d',
                      'd',
                      'e']
    assert loaded_key_order == expected_order


def test_order_preservation_to_flat_dict(tmp_path):
    filename = str(tmp_path / 'myyaml.yaml')

    data = {'r': 1,
            'k': dict(a=5, c=dict(a=5, b=1, c=3), b=(3, 1), d=2),
            'b': (20, 3, 5),
            'z': dict(a=dict(a=5, b=1, c=3), b=1, c=2, d=5),
            'd': 1,
            'e': 1}

    with open(filename, 'w') as f:
        f.write(yaml.safe_dump(data, sort_keys=False, default_flow_style=False))

    # NOTE: This calls to_flat_dict which doesn't collapse lists/tuples
    d = mlconf.flat_dict_from_file(filename)
    loaded_key_order = list(d.keys())
    expected_order = ['r',
                      'k.a',
                      'k.c.a',
                      'k.c.b',
                      'k.c.c',
                      'k.b',
                      'k.d',
                      'b',
                      'z.a.a',
                      'z.a.b',
                      'z.a.c',
                      'z.b',
                      'z.c',
                      'z.d',
                      'd',
                      'e']
    assert loaded_key_order == expected_order


def test_load_order_preservation(tmp_path):
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
