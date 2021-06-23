import qcore
from qcore.asserts import AssertRaises


class Foo(metaclass=qcore.DisallowInheritance):
    pass


def test_disallow_inheritance():
    with AssertRaises(TypeError):

        class Bar(Foo):
            pass
