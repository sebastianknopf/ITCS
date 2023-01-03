from dataclasses import dataclass
from dataclasses import fields


def construct_dataclass(cls: type, src):

    field_types_lookup = {
        field.name: field.type
        for field in fields(cls)
    }

    constructor_inputs = {}
    for field_name, value in src.items():
        try:
            constructor_inputs[field_name] = construct_dataclass(field_types_lookup[field_name], value)
        except TypeError as e:
            # type error from fields() call in recursive call
            # indicates that field is not a dataclass, this is how we are
            # breaking the recursion. If not a dataclass - no need for loading
            constructor_inputs[field_name] = value
        except KeyError:
            # similar, field not defined on dataclass, pass as plain field value
            constructor_inputs[field_name] = value

    return cls(**constructor_inputs)


@dataclass
class Stop:
    name: str
    node: int


@dataclass
class Route:
    id: str
    length: float
    stops: list[Stop]
    nodes: list


@dataclass
class Deviation:
    length: float
    nodes: list
