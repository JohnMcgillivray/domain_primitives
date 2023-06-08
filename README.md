# domain_primitives
A python library that provides a quick and convenient syntax for creating domain primitives. Creates frozen dataclasses with validation.

## Installation
1. Clone the repository
2. Run `pip install .` in the root directory

## Usage
```
from domain_primitives import domain_prim, validator

@domain_prim
class Order:
    quantity: int = validator(gt=0, lt=100)
```
Declare a domain primitive by decorating a class with `@domain_prim`. All dataclass options besides `frozen` and `init` may be passed to the decorator to control behavior of the class. The `validator` function is used to declare validation rules for the field, which are checked on each object's instantiation. Options for the validator function are:
- `check_type`: whether to check the type of the field. True by default.
- `gt`: greater than for numerics
- `lt`: less than for numerics
- `min_length`: minimum length of a string or collection
- `max_length`: maximum length of a string or collection
- `regex`: regex pattern to match
- `custom_fn`: custom function that takes the field value as an argument and returns a boolean
- `field`: a dataclasses field object
