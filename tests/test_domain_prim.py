from dataclasses import FrozenInstanceError
from domain_primitives import domain_prim, validator, field
import pytest


@domain_prim(eq=False, order=False, match_args=False)
class A:
    a: int = validator(gt=0, lt=10)


@domain_prim
class B:
    b: str = validator(len_min=3, len_max=10, regex=r"^[a-z]+$")


@domain_prim
class C:
    c: list[int] = validator(len_min=3, len_max=10)


def is_odd(x):
    return x % 2 == 1


@domain_prim
class D:
    odd: int = validator(
        custom_fn=is_odd, field=field(repr=False, compare=False, hash=False)
    )
    even: int = validator(custom_fn=lambda x: x % 2 == 0)
    keyword: int = validator(field=field(kw_only=True, default=0))


def test_frozen():
    a = A(1)
    with pytest.raises(FrozenInstanceError):
        a.a = 2


def test_type_checking():
    with pytest.raises(TypeError):
        A("a")

    with pytest.raises(TypeError):
        B(1)

    with pytest.raises(TypeError):
        C("a")


def test_less_than():
    with pytest.raises(AssertionError):
        A(-1)


def test_greater_than():
    with pytest.raises(AssertionError):
        A(11)


def test_len_min():
    with pytest.raises(AssertionError):
        B("a")

    with pytest.raises(AssertionError):
        C([])


def test_len_max():
    with pytest.raises(AssertionError):
        B("abcdefghijklmnopqrstuvwxyz")

    with pytest.raises(AssertionError):
        C([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])


def test_regex():
    with pytest.raises(AssertionError):
        B("123")


def test_custom_fn():
    with pytest.raises(ValueError):
        D(2, 2)

    with pytest.raises(ValueError):
        D(1, 1)


def test_field():
    d1 = D(1, 2)
    d2 = D(3, 2)
    d3 = D(1, 4)

    assert str(d1) == "D(even=2, keyword=0)"
    assert d1 == d2
    assert d1 != d3
    assert d1 < d3
    assert d3 > d1
    assert d1 <= d3
    assert d3 >= d1
    assert hash(d1) == hash(d2)
    assert hash(d1) != hash(d3)
    with pytest.raises(TypeError):
        D(1, 2, 3)


def test_dataclass_options():
    a1 = A(1)
    a2 = A(2)
    assert a1.__eq__(a2) == NotImplemented
    assert a1.__lt__(a2) == NotImplemented
    assert a1.__le__(a2) == NotImplemented
    assert a1.__gt__(a2) == NotImplemented
    assert a1.__ge__(a2) == NotImplemented
    with pytest.raises(AttributeError):
        a1.__match_args__()
