from dataclasses import Field, field, dataclass, _create_fn


@dataclass(kw_only=True)
class Validator:
    check_type: bool = True
    lt: float = None
    gt: float = None
    len_max: int = None
    len_min: int = None
    regex: str = None
    custom_fn: callable = None
    field: Field = None


def _create_validations(name: str, type: type, validator: Validator):
    body = []

    for k, v in validator.__dict__.items():
        if v is None:
            continue

        match k, v:
            case "check_type", True:
                # check if the type is correct, for lists can only confirm the value in question is a list
                # type of list elements is not checked
                body.append(
                    (
                        f"if not isinstance(self.{name}, {type.__name__}):\n"
                        f"    raise TypeError(f'Expected {type.__name__} but got ' + str(type(self.{name}).__name__))"
                    )
                )
            case "lt", v:
                body.append(
                    (f"assert self.{name} < {v}, 'Expected {name} to be less than {v}'")
                )
            case "gt", v:
                body.append(
                    (
                        f"assert self.{name} > {v}, 'Expected {name} to be greater than {v}'"
                    )
                )
            case "len_max", v:
                body.append(
                    (
                        f"assert len(self.{name}) <= {v}, 'Expected {name} to have a length no greater than {v}'"
                    )
                )
            case "len_min", v:
                body.append(
                    (
                        f"assert len(self.{name}) >= {v}, 'Expected {name} to have a length no less than {v}'"
                    )
                )
            case "regex", v:
                body.append(
                    (
                        f"assert re.match(r'{v}', self.{name}), 'Expected {name} to match the regex {v}'"
                    )
                )
            case "custom_fn", v:
                body.append(
                    (
                        f"if _{name}_validator_fn(self.{name}) == False:\n"
                        f"    raise ValueError(f'Expected {name} to pass the custom validator')"
                    )
                )

    return body


def _create_post_init(cls):
    body = []
    locals = {}

    # find fields assigned validators and create validation code
    annotations = cls.__annotations__
    for name, type in annotations.items():
        value = cls.__dict__.get(name)
        if isinstance(value, Validator):
            validator = value
            body.extend(_create_validations(name, type, validator))

            # add closure for custom validator to local namespace
            if validator.custom_fn is not None:
                locals[f"_{name}_validator_fn"] = validator.custom_fn

    # create the __post_init__ method if there is any validation code
    if body:
        f = _create_fn("__post_init__", ["self"], body, locals=locals)
        f.__qualname__ = f"{cls.__qualname__}.{f.__name__}"
        setattr(cls, "__post_init__", f)


def _remove_validator_defaults(cls):
    dict = cls.__dict__
    for k, v in dict.copy().items():
        if isinstance(v, Validator):
            if v.field is not None:
                setattr(cls, k, v.field)
            else:
                delattr(cls, k)


def domain_prim(cls=None, *, kw_only=False, slots=False, weakref_slot=False):
    def decorator(cls):
        # construct the __post_init__ method where validation occurs
        _create_post_init(cls)

        # remove the validator default values from the class
        _remove_validator_defaults(cls)

        # create the dataclass
        return dataclass(
            cls,
            init=True,
            repr=True,
            eq=True,
            order=True,
            frozen=True,
            match_args=True,
            kw_only=kw_only,
            slots=slots,
            weakref_slot=weakref_slot,
        )

    # check if decorator was used with or without parenthesis
    if cls is None:
        # parenthesis were used
        return decorator

    # no parenthesis
    return decorator(cls)


def test():
    @domain_prim
    class Abcd:
        a: int = Validator(custom_fn=lambda x: x % 2 == 0, field=field(repr=False))
        b: int = Validator(gt=4, lt=10)
        c: str = Validator(len_min=3, len_max=10, regex=r"^[a-z]+$")
        d: list[int] = Validator(len_min=3, len_max=5)

    abcd = Abcd(2, 6, "apple", [1,2,4,5])
    print(type(abcd.d))
    abcd = Abcd(2, 6, "apple", ['a', 'b', 'c', 'd', 'e'])


if __name__ == "__main__":
    test()
