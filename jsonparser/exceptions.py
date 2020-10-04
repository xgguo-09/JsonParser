
__all__ = [
    'ParseError', 'ParseStringError', 'ParseBoolError',
    'ParseNumberError', 'ParseNULLError', 'ParseJSONArrayError',
    'ParseJSONObjectError', 'TokenError'
]


class ParseError(Exception):
    def __init__(self, data, pos, *args, **kwargs):
        self.data = data
        self.pos = pos

    def __repr__(self):
        return f'{self.__class__}({self.data}, {self.pos})'


class ParseStringError(ParseError):
    """Error parsing string"""


class ParseBoolError(ParseError):
    """Error parsing bool type"""


class ParseNumberError(ParseError):
    """Error parsing number"""


class ParseNULLError(ParseError):
    """Error parsing null"""


class TokenError(Exception):
    """Unexpected token"""


class ParseJSONObjectError(TokenError):
    """Error parsing json object"""


class ParseJSONArrayError(TokenError):
    """Error parsing json array"""
