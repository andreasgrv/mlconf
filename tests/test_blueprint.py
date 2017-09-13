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
