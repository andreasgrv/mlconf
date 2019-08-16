import mlconf
import pytest


def test_yaml_loader():
    parser = mlconf.ArgumentParser()
    parser.add_argument('--value')
    parser.add_argument('--load_blueprint',
                        action=mlconf.YAMLLoaderAction)
    bp = parser.parse_args(['--value', '5', '--load_blueprint',
                            'tests/data/example.yaml',
                            '--foo.counter.b', '63'])
    assert(bp.value == '5')
    assert(bp.foo.counter.a == 5)
    assert(bp.foo.counter.b == 63)


def test_yaml_loader_wrong_order():
    parser = mlconf.ArgumentParser()
    parser.add_argument('--value')
    parser.add_argument('--load_blueprint',
                        action=mlconf.YAMLLoaderAction)
    with pytest.raises(SystemExit):
        bp = parser.parse_args(['--load_blueprint', 'tests/data/example.yaml',
                                '--value', '5'])


def test_yaml_loader_override_default():
    parser = mlconf.ArgumentParser()
    parser.add_argument('--value', default=29, type=int)
    parser.add_argument('--load_blueprint',
                        action=mlconf.YAMLLoaderAction)
    bp = parser.parse_args(['--value', '8', '--load_blueprint',
                            'tests/data/example.yaml',
                            '--foo.counter.b', '63'])
    assert(bp.value == 8)
    assert(bp.foo.counter.a == 5)
    assert(bp.foo.counter.b == 63)


def test_yaml_loader_check_type():
    parser = mlconf.ArgumentParser()
    parser.add_argument('--value', default=6)
    parser.add_argument('--load_blueprint',
                        action=mlconf.YAMLLoaderAction)
    with pytest.raises(SystemExit):
        bp = parser.parse_args(['--load_blueprint', 'tests/data/example.yaml',
                                '--foo.counter.b', 'a'])


def test_yaml_loader_bools():
    parser = mlconf.ArgumentParser()
    parser.add_argument('--value', default=6)
    parser.add_argument('--load_blueprint',
                        action=mlconf.YAMLLoaderAction)
    bp = parser.parse_args(['--load_blueprint', 'tests/data/example.yaml',
                            '--foo.boolstuff.a', 'false',
                            '--foo.boolstuff.d', 'true'])
    assert(bp.foo.boolstuff.a == False)
    assert(bp.foo.boolstuff.b == True)
    assert(bp.foo.boolstuff.c == False)
    assert(bp.foo.boolstuff.d == True)
