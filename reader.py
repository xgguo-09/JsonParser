import os
from io import StringIO
from mmap import mmap, ACCESS_READ


class Reader:
    def __init__(self, string=''):
        if not isinstance(string, str):
            raise TypeError('parameter ``string`` must be ``str`` type')
        self.data = string
        self._size = len(self.data)
        self._reader = StringIO(self.data)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._size}, {self.pos})'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._reader.close()

    def read(self, size=1):
        return self._reader.read(size)

    def prev_pos(self, size=1):
        pos = self.pos - size
        self._reader.seek(pos, 0)

    def has_next(self):
        return self.pos < self.epos

    @property
    def pos(self):
        return self._reader.tell()

    @property
    def epos(self):
        return self._size


class FileReader(Reader):
    MMAP_START_SIZE = pow(1024, 2)  # 1M

    def __init__(self, filename, encoding=None, errors=None):
        self.encode = 'utf-8' if encoding is None else encoding
        self._size = os.path.getsize(filename)
        self._reader = open(filename, encoding=self.encode, errors=errors)
        if self._size > self.MMAP_START_SIZE:
            self._reader = mmap(self._reader.fileno(), 0, access=ACCESS_READ)

    def read(self, size=1):
        r = self._reader.read(size)
        if isinstance(self._reader, mmap):
            return r.decode(self.encode)
        return r

    @property
    def pos(self):
        if self._reader.tell() > self.epos:
            # 很奇怪，文件指针会指向未知的地方，指向 pow(2, 64) + 当前出错位置
            # 需要手动恢复当前指针位置
            self.read(1)
            self.prev_pos(1)
        return self._reader.tell()
