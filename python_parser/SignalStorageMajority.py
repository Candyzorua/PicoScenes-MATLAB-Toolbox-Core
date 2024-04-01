from enum import Enum

class SignalStorageMajority(Enum):
    RowMajor = 'R'
    ColumnMajor = 'C'
    Undefined = 'U'