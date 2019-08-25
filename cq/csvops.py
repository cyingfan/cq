from cq.common_types import RowGenerator
import csv
from os import path
import sys
import typing


def read(io: typing.IO) -> RowGenerator:
    reader = csv.DictReader(io)
    for row in reader:
        yield row


def with_open_action(filepath: str, function: typing.Callable[[typing.IO], typing.Any]):
    if path.isfile(filepath):
        fd = open(filepath)
        yield from function(fd)
        fd.close()

    elif filepath == '-':
        return function(sys.stdin)

    else:
        raise Exception('Invalid input ' + filepath)


def print_csv(rows: RowGenerator):
    try:
        row = next(rows)
    except StopIteration:
        return
    writer = csv.DictWriter(sys.stdout, fieldnames=row.keys())
    writer.writeheader()
    writer.writerow(row)
    for row in rows:
        writer.writerow(row)
