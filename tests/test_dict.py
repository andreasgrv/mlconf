import mlconf

nested = {'a':{'c': 1, 'd': (2, {'a': 3}), 'e': {'f': 3, 'g': 4}}, 'b': 5}
flat = {'a.c': 1, 'a.d': (2, {'a': 3}), 'a.e.f': 3, 'a.e.g': 4, 'b': 5}


def test_to_flat_dict():
    f = mlconf.to_flat_dict(nested)
    assert(f == flat)


def test_to_flat_on_flat():
    f = mlconf.to_flat_dict(flat)
    assert(f == flat)


def test_to_flat_no_copy():
    flat_copy = dict(flat)
    mlconf.to_nested_dict(flat_copy, copy=False)
    assert(flat_copy == nested)


def test_to_nested_dict():
    n = mlconf.to_nested_dict(flat)
    assert(n == nested)


def test_to_nested_on_nested():
    n = mlconf.to_nested_dict(nested)
    assert(n == nested)


def test_to_nested_no_copy():
    flat_copy = dict(flat)
    mlconf.to_nested_dict(flat_copy, copy=False)
    assert(flat_copy == nested)


def test_to_and_from():
    assert(flat == mlconf.to_flat_dict(mlconf.to_nested_dict(flat)))
    assert(nested == mlconf.to_nested_dict(mlconf.to_flat_dict(nested)))
