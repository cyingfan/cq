from io import BytesIO
import tokenize
import typing

allowed_tokens = (
    1,  # name
    2,  # number
    3,  # string
    53  # operator
)
operators = {
    '<': '__lt__',
    '<=': '__le__',
    '==': '__eq__',
    '!=': '__ne__',
    '>': '__gt__',
    '>=':  '__ge__',
}
operand_tokens = [1, 2, 3]
TokenTuple = typing.Tuple[tokenize.TokenInfo, ...]
NormalizedTokenTuple = typing.Tuple[tokenize.TokenInfo, tokenize.TokenInfo, tokenize.TokenInfo]
TokenGroup = typing.NamedTuple('TokenGroup', operand=TokenTuple, operator=TokenTuple)


def get_condition_tokens(condition: str) -> typing.Optional[NormalizedTokenTuple]:
    tuples = tuple(filter(
        lambda token: token.type in allowed_tokens,
        tokenize.tokenize(BytesIO(condition.encode('utf-8')).readline)
    ))
    return normalize_operands(tuples)


def normalize_operands(tokens: TokenTuple) -> typing.Optional[NormalizedTokenTuple]:
    if len(tokens) <= 3:
        return None

    operator_position = get_operator_position(tokens)
    if operator_position is None:
        return None

    left_operand = group_operand(tokens[:operator_position])
    if left_operand is None:
        return None
    right_operand = group_operand(tokens[operator_position+1:])
    if right_operand is None:
        return None

    return left_operand, tokens[operator_position], right_operand


def get_operator_position(tokens: TokenTuple) -> typing.Optional[int]:
    for index, value in enumerate(tokens):
        if value.type == 53 and value.string in operators:
            return index
    return None


def group_operand(tokens: TokenTuple) -> typing.Optional[tokenize.TokenInfo]:
    token_length = len(tokens)
    if token_length == 0:
        return None
    if token_length == 1:
        return tokens[0]

    first_char_position = tokens[0].start[1]
    last_char_position = tokens[token_length - 1].end[1]
    column_name = tokens[0].line[first_char_position:last_char_position]
    return tokenize.TokenInfo(
        type=1,
        string=column_name,
        start=(1, first_char_position),
        end=(1, last_char_position),
        line=tokens[0].line
    )







