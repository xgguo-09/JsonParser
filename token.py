from enum import Enum, unique


@unique
class TokenType(Enum):
    # Signal token
    BEGIN_OBJECT = 1
    BEGIN_ARRAY = 2
    END_OBJECT = 4
    END_ARRAY = 8

    # variable token
    NULL = 16
    NUMBER = 32
    STRING = 64
    BOOL = 128

    # separator token
    COLON = 256
    COMMA = 512

    # end signal
    END_JSON = 65536

    def __repr__(self):
        return f'{self.__class__.__name__}.{self.name}'
