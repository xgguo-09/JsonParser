import re
from functools import wraps
from collections.abc import Iterator, Generator

from .token import TokenType as Tk
from .exceptions import *
from .reader import Reader

__all__ = ['Lexer']


class _TokenContext:
    """接收一个包含 (Tokentype, value) 键值的 generator 对象或者 Iterator 对象

    由于generator只能遍历一次，所以无法记录前一个状态与后一个状态
    本类的目的是记录前一个token状态"""

    def __init__(self, gen):
        if isinstance(gen, (Iterator, Generator)):
            self._gen = gen
        else:
            raise TypeError("parameter ``gen`` type error, must be "
                            "``generator`` or ``Iterator`` object")
        self._stack = []

    def __repr__(self):
        return f'{self.__class__.__name__}(prev: {self.prev})'

    def __iter__(self):
        return self

    def __next__(self):
        try:
            k, v = next(self._gen)
        except StopIteration as e:
            raise e
        else:
            if len(self._stack) >= 2:
                self._stack.pop(0)
            self._stack.append((k, v))
        return k, v

    @property
    def prev(self):
        return self._stack[0] if len(self._stack) >= 2 else (None, None)


def token_context(func):
    @wraps(func)
    def wrapper(self):
        token_gen = _TokenContext(func(self))
        return token_gen
    return wrapper


number_re = re.compile(r'(^[+-]?[0-9]+$)'
                       r'|'
                       r'(^[+-]?[0-9]+\.[0-9]+$)'
                       r'|'
                       r'(^[-+]?[0-9]+[eE]+[+-]?[0-9]+$'
                       r'|'
                       r'^[-+]?[0-9]+\.[0-9]+[eE]+[+-]?[0-9]+$)')


class Lexer:
    """json token 标记，调用类方法 ``get_token`` (参数 ``text`` 须是 string 类型）
    会返回包含 (Tokentype, value) 键值的 Iterator 对象"""

    def __init__(self, reader=None):
        self._reader = reader

    def __repr__(self):
        return f'{self.__class__.__name__}({self._reader})'

    @classmethod
    def get_tokens(cls, text):
        scanner = Reader(text)
        return cls(scanner).parse()

    @token_context
    def parse(self):
        _s = ''
        while self._is_space(_s) and self._reader.has_next():
            _s = self._reader.read(1)
        self._reader.prev_pos(1)  # back one step

        while self._reader.has_next():
            char = self._reader.read(1)
            if char == '{':
                yield Tk.BEGIN_OBJECT, char
            elif char == '}':
                yield Tk.END_OBJECT, char
            elif char == '[':
                yield Tk.BEGIN_ARRAY, char
            elif char == ']':
                yield Tk.END_ARRAY, char
            elif char == ':':
                yield Tk.COLON, char
            elif char == ',':
                yield Tk.COMMA, char
            elif char == 'n':
                yield self.read_null()
            elif char in ('f', 't'):
                yield self.read_bool(char)
            elif char == '"':
                yield self.read_string()
            elif self._is_number(char):
                yield self.read_number(char)
            elif self._is_space(char):
                pass
            else:
                raise ParseError(char, self._reader.pos)
        else:
            # end
            yield Tk.END_JSON, None

    @staticmethod
    def _is_space(char):
        return char in ('\n', '\t', '\r', ' ', '')

    @staticmethod
    def _is_number(char):
        return char in map(str, range(10)) or char in ('+', '-')

    @staticmethod
    def _is_unicode_str(char):
        return char in map(str, range(0, 10)) or char in 'abcdefABCDEF'

    @staticmethod
    def escape_map(char):
        d = {'\"': '"', 'r': '\r', 'n': '\n', 't': '\t',
             '\\': '\\', 'b': '\x08', 'f': '\x0c', '/': '/'}

        return d.get(char)

    def read_null(self):
        # null
        result = self._reader.read(3)
        if result != 'ull':
            raise ParseNULLError('n', self._reader.pos)
        return Tk.NULL, None

    def read_bool(self, char):
        # false, true
        part = ''
        if char == 'f':
            part = self._reader.read(4)
        elif char == 't':
            part = self._reader.read(3)
        if part not in ('alse', 'rue'):
            raise ParseBoolError(char, self._reader.pos)
        result = char + part
        return Tk.BOOL, {'true': True, 'false': False}.get(result)
    
    def read_number(self, char):
        # integer, fraction, exponent
        # 数字1-9，0和正负数, 如， 1，+1，-1, 0
        # 浮点数如：1.3
        # 指数如：（1e2，1e+2，1.2e-2，1E2，1E+2，1.2E-2)
        chunk = ''
        number = None
        while self._reader.has_next():
            next_char = self._reader.read(1)
            if next_char in (',', ']', '}'):
                self._reader.prev_pos()
                break
            chunk += next_char

        chunk = (char+chunk).rstrip()
        m = number_re.match(chunk)
        try:
            i, f, exp = m.groups()
        except AttributeError:
            raise ParseError(chunk, self._reader.pos)

        if i:
            number = int(i)
        if f:
            number = float(f)
        if exp:
            number = float(exp)
        assert number is not None, ParseNumberError(chunk, self._reader.pos)
        return Tk.NUMBER, number

    def read_string(self):
        # 任意字符串还有转义的
        # 转义字符处理有两种
        # 第一种： \", \/, \\, \b, \f, \n, \r, \t
        # 第二种：\u[0-9][A-Fa-f]，U+0000到U+001F
        data = []
        char = self._reader.read(1)
        while True:
            if not self._reader.has_next():
                break
            if char == '"':
                data.append('')
                break

            if char == '\\':
                # 转义字符 \
                flag = self._reader.read(1)

                if flag in ('b', 'n', 't', '"', '/', 'r', 'f', '\\'):
                    # 第一种
                    r = self.escape_map(flag)
                    data.append(r)
                elif flag == 'u':
                    # 第二种
                    chunk = char + flag
                    for i in range(4):
                        _next = self._reader.read(1)
                        if self._is_unicode_str(_next):
                            chunk += _next
                        else:
                            raise ParseStringError(char, self._reader.pos)
                    data.append(chunk)
                else:
                    raise ParseStringError(char, self._reader.pos)
            else:
                data.append(char)
            char = self._reader.read(1)
        return Tk.STRING, ''.join(data)
