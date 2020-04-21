from .token import TokenType as Tk
from .exceptions import (ParseJSONArrayError, ParseJSONObjectError, TokenError)


class Parser:
    def __init__(self, token_gen=None):
        """参数 ``token_gen`` 是包含token (TokenType, value) 键值对的 iterable 对象"""
        self._token_gen = token_gen
        self.obj, self.array = dict, list

    def parse(self):
        try:
            token_type, token_value = next(self._token_gen)
        except StopIteration:
            return self.obj
        if token_type == Tk.BEGIN_OBJECT:
            return self.parse_json_object()
        elif token_type == Tk.BEGIN_ARRAY:
            return self.parse_json_array()
        else:
            raise Exception('Illegal token at beginning', token_value)

    def _check_token(self, current, expected):
        if current not in expected:
            raise TokenError(self._token_gen.prev[0], current, expected)

    def parse_json_object(self):
        obj = self.obj()
        expected = (Tk.STRING, Tk.END_OBJECT)
        key = None
        for _type, _value in self._token_gen:
            self._check_token(_type, expected)

            if _type == Tk.STRING:
                prev_type, _ = self._token_gen.prev
                if prev_type == Tk.COLON:  # value
                    value = _value
                    obj[key] = value
                    expected = (Tk.COMMA, Tk.END_OBJECT)
                else:  # key
                    key = _value
                    expected = (Tk.COLON,)
            elif _type in (Tk.NULL, Tk.BOOL, Tk.NUMBER):
                obj[key] = _value
                expected = (Tk.COMMA, Tk.END_OBJECT)
            elif _type == Tk.COMMA:
                expected = (Tk.STRING,)
            elif _type == Tk.COLON:
                expected = (Tk.NULL, Tk.NUMBER, Tk.BOOL, Tk.STRING,
                            Tk.BEGIN_OBJECT, Tk.BEGIN_ARRAY)
            elif _type == Tk.END_OBJECT:
                return obj
            elif _type == Tk.END_JSON:
                return obj
            elif _type == Tk.BEGIN_ARRAY:
                obj[key] = self.parse_json_array()  # 调用
                expected = (Tk.COMMA, Tk.END_OBJECT)
            elif _type == Tk.BEGIN_OBJECT:
                obj[key] = self.parse_json_object()  # 递归
                expected = (Tk.COMMA, Tk.END_OBJECT)
            else:
                raise ParseJSONObjectError(_type, _value)

    def parse_json_array(self):
        array = self.array()
        expected = (Tk.BEGIN_ARRAY, Tk.END_ARRAY, Tk.BEGIN_OBJECT, Tk.STRING,
                    Tk.NULL, Tk.BOOL, Tk.NUMBER)
        for _type, _value in self._token_gen:
            self._check_token(_type, expected)

            if _type == Tk.BEGIN_ARRAY:
                array.append(self.parse_json_array())  # 递归
                expected = (Tk.COMMA, Tk.END_ARRAY)
            elif _type == Tk.BEGIN_OBJECT:
                array.append(self.parse_json_object())  # 调用
                expected = (Tk.COMMA, Tk.END_ARRAY)
            elif _type == Tk.STRING:
                array.append(_value)
                expected = (Tk.END_ARRAY, Tk.COMMA)
            elif _type in (Tk.NULL, Tk.BOOL, Tk.NUMBER):
                array.append(_value)
                expected = (Tk.END_ARRAY, Tk.COMMA)
            elif _type == Tk.COMMA:
                expected = (Tk.STRING, Tk.BOOL, Tk.BEGIN_ARRAY, Tk.NUMBER,
                            Tk.BEGIN_OBJECT, Tk.NULL)
            elif _type == Tk.END_ARRAY:
                return array
            elif _type == Tk.END_JSON:
                return array
            else:
                raise ParseJSONArrayError(_type, _value)
