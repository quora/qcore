import qcore
from qcore.asserts import AssertRaises
import six


class Foo(six.with_metaclass(qcore.DisallowInheritance)):
    pass


def test_disallow_inheritance():
    with AssertRaises(TypeError):
        class Bar(Foo):
            pass
