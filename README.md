# Jsonparser
A json parser written in python3.

## Install
```commandline
pip3 install -e .
```

## Usage
```python
>>> import jsonparser
>>>
>>> input_data = '[null, false, {"a": [true, 1], "b": 2e3}]'
>>> r = jsonparser.from_string(input_data)
>>> r
[None, False, {'a': [True, 1], 'b': 2000.0}]
>>>
>>> local_file = 'test.json'
>>> r = jsonparser.from_file(local_file)
>>> r
[None, False, {'a': [True, 1], 'b': 2000.0}]
```
