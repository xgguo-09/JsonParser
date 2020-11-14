"""实现了json反序列化功能：json -> py_obj

json 数据与 python 数据结构转换如下：
        +---------------+-------------------+
        | JSON          | Python            |
        +===============+===================+
        | object        | dict              |
        +---------------+-------------------+
        | array         | list              |
        +---------------+-------------------+
        | string        | str               |
        +---------------+-------------------+
        | number (int)  | int               |
        +---------------+-------------------+
        | number (real) | float             |
        +---------------+-------------------+
        | true          | True              |
        +---------------+-------------------+
        | false         | False             |
        +---------------+-------------------+
        | null          | None              |
        +---------------+-------------------+

Example:
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
"""

__all__ = ['from_string', 'from_file']


from .lexer import Lexer
from .parser import Parser
from .reader import FileReader


def from_string(s):
    """Deserialize `s`( `str` instance) to a Python object"""
    token_gen = Lexer.get_tokens(s)
    return Parser(token_gen).parse()


def from_file(filename, encoding=None, errors=None):
    """Deserialize json file to a Python object"""
    with FileReader(filename, encoding, errors) as rd:
        token_gen = Lexer(rd).parse()
        return Parser(token_gen).parse()
