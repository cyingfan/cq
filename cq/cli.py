import argparse
from cq import csvops
from cq import filter


def main():
    parser = argparse.ArgumentParser(description='CSV Query')
    parser.add_argument('file')
    parser.add_argument('--whereor', action='store_const', const=filter.OrOperator(), default=filter.AndOperator())
    parser.add_argument('--where', action='append')

    args = parser.parse_args()
    lines = csvops.with_open_action(
        args.file,
        csvops.read
    )
    if args.where:
        lines = filter.filter_lines(lines, args.where, args.whereor)

    csvops.print_csv(lines)
