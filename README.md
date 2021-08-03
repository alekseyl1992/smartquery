# smartquery
[![GitHub Actions](https://github.com/alekseyl1992/smartquery/workflows/release/badge.svg)](https://github.com/alekseyl1992/smartquery/actions?query=workflow%3Arelease)
[![PyPI](https://img.shields.io/pypi/v/smartquery.svg)](https://pypi.org/project/smartquery)

SmartQuery is a simple interpreted programming language designed to be easily embedded in other programs.
It aims to safely run untrusted third-party code.

It is based on [ply](https://github.com/dabeaz/ply) library and uses Python runtime to implement all the functions and operations.

## Documentation
https://docs.smartbot-vk.ru/smartquery

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
pip install smartquery[repl]
python -m smartquery
```


## Have questions?
Please contact me via [email](mailto:alekseyl@list.ru)
