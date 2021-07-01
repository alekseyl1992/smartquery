# smartquery

SmartQuery is a simple interpreted programming language designed to be easily embedded in other programs.
It aims to safely run untrusted third-party code.

It is based on `ply` library and uses Python runtime to implement all the functions and operations.

## Documentation
https://docs.smartbot-vk.ru/smartquery/vvedenie

## Installation
```bash
pip install smartquery
```

## Usage example
```python
from smartquery import SqParser
parser = SqParser()
data = {
    'x': 2,
    'y': 3,
}
parser.eval('x * y', names=data)
```

## Run REPL
```bash
python -m smartquery
```
