import typing

Value = typing.Union[int, str, float]
Row = typing.Dict[str, Value]
RowGenerator = typing.Generator[Row, None, None]
