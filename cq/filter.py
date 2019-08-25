from cq.common_types import RowGenerator, Value, Row
from cq import tokenizer
import tokenize
import typing


def group_tokens(tokens: tokenizer.TokenTuple) -> tokenizer.TokenGroup:
    return tokenizer.TokenGroup(
        operand=tuple(filter(
            lambda token: token.type in tokenizer.operand_tokens,
            tokens
        )),
        operator=tuple(filter(
            lambda token: token.string in tokenizer.operators,
            tokens
        ))
    )


def validate_token(token_group: tokenizer.TokenGroup):
    return len(token_group.operand) == 2 and len(token_group.operator) == 1


class Comparable:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

    def __repr__(self):
        return str(self.value)


def operand_value(operand: tokenize.TokenInfo, row: typing.Dict):
    if operand.type == 1:
        property_name = operand.string
        target_type = ''
        if ':' in property_name:
            property_name, target_type = property_name.split(':')
        value = cast_type(target_type, row.get(property_name))

    elif operand.type == 2:
        value = float(operand.string)
    else:
        value = operand.string.strip('\'"')
    return Comparable(value)


def cast_type(type_name: str, value):
    if type_name == 'str' or type_name == 'string':
        return str(value)
    if type_name == 'float':
        return float(value)
    if type_name == 'int' or type_name == 'integer':
        return int(value)
    return value


def execute_token_condition(token_group: tokenizer.TokenGroup, row: Row) -> bool:
    operand1 = operand_value(token_group.operand[0], row)
    operand2 = operand_value(token_group.operand[1], row)
    operator = tokenizer.operators.get(token_group.operator[0].string, '')
    return getattr(operand1, operator, lambda x: False)(operand2)


def execute_condition(condition: str, row: Row) -> bool:
    tokens = tokenizer.get_condition_tokens(condition)
    token_group = group_tokens(tokens)

    if not validate_token(token_group):
        raise Exception('Invalid condition')

    return execute_token_condition(token_group, row)


class LogicalOperator:
    def __call__(self, *args, **kwargs) -> bool:
        raise Exception('Method not implemented')


class OrOperator(LogicalOperator):
    def __call__(self, *args, **kwargs) -> bool:
        return any(*args, **kwargs)


class AndOperator(LogicalOperator):
    def __call__(self, *args, **kwargs) -> bool:
        return all(*args, **kwargs)


def execute_conditions(conditions: typing.Sequence[str], row: Row, join: LogicalOperator) -> bool:
    return join(map(
        execute_condition,
        conditions,
        list(row for x in conditions)
    ))


def filter_lines(lines: RowGenerator, conditions: typing.Sequence[str], join: LogicalOperator) -> RowGenerator:
    return (line for line in lines if execute_conditions(conditions, line, join))
