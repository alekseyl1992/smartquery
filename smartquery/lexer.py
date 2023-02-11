from smartquery.custom_types import Decimal
from smartquery.exceptions import ParserError


reserved_unused = {
    'for': 'FOR',
    'while': 'WHILE',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'def': 'DEF',
    'raise': 'RAISE',
    'elif': 'ELIF',
}

reserved = {
    'and': 'AND',
    'or': 'OR',
    'in': 'IN',
    'not': 'NOT',
    'if': 'IF',
    'else': 'ELSE',
    'True': 'TRUE',
    'False': 'FALSE',
    'None': 'NONE',
    'del': 'DEL',

    **reserved_unused,
}

tokens = (
    'NAME', 'NUMBER', 'STRING',
    'EQ', 'NE', 'GT', 'LT', 'LTE', 'GTE',
    'PLUS', 'MINUS', 'TIMES', 'POWER', 'DIVIDE',
    'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'COMMA', 'DOT', 'PIPE',
    'ASSIGN', 'SHORT_OP', 'LAMBDA', 'COMMENT', 'COLON', 'LBRACE', 'RBRACE', 'NEWLINE',
    *reserved.values()
)

# Tokens
t_ASSIGN = r'='
t_SHORT_OP = r'[+\-\*/]='
t_EQ = r'=='
t_NE = r'!='
t_GT = r'>'
t_LT = r'<'
t_GTE = r'>='
t_LTE = r'<='

t_LAMBDA = r'=>'

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_POWER = r'\*\*'
t_DIVIDE = r'/'
t_COMMA = r','
t_DOT = r'\.'
t_PIPE = r'\|'
t_COLON = r':'


def t_NEWLINE(t):
    r"""\r\n|\n|;"""
    if t.value == ';' or t.lexer.paren_count == 0:
        t.lexer.lineno += 1
        return t
    else:
        # ignore newlines inside of parens, braces and brackets
        return None


def t_LPAREN(t):
    r"""\("""
    t.lexer.paren_count += 1
    return t


def t_RPAREN(t):
    r"""\)"""
    t.lexer.paren_count -= 1
    return t


def t_LBRACKET(t):
    r"""\["""
    t.lexer.paren_count += 1
    return t


def t_RBRACKET(t):
    r"""\]"""
    t.lexer.paren_count -= 1
    return t


def t_LBRACE(t):
    r"""{"""
    t.lexer.paren_count += 1
    return t


def t_RBRACE(t):
    r"""}"""
    t.lexer.paren_count -= 1
    return t


def t_STRING(t):
    r""" (r?\"([^\\\n]|(\\.))*?\") | (r?\'([^\\\n]|(\\.))*?\') """

    if t.value[0] != 'r':
        t.value = t.value[1:-1] \
            .replace(r'\n', '\n') \
            .replace(r'\t', '\t') \
            .replace(r'\'', "'") \
            .replace(r'\"', '"')
    else:
        t.value = t.value[2:-1]

    return t


def t_NUMBER(t):
    r""" \d+(\.\d+)? """
    t.value = Decimal(t.value)
    return t


# vars with %% can contain dots in name
# others - cant
def t_NAME(t):
    r""" (%.*?%) | ([^\W\d][\w0-9_]*([\w_][\w0-9_]*)*) """
    t.type = reserved.get(t.value, 'NAME')
    return t


def t_COMMENT(t):
    r""" \043.* """
    return None


# Ignored characters
t_ignore = " \t"


def t_error(t):
    raise ParserError(f'Illegal character {t.value[0]}')


# precedence rules for the arithmetic operators
precedence = (
    ('left', 'ASSIGN'),
    ('left', 'SHORT_OP'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQ', 'NE', 'GT', 'LT', 'GTE', 'LTE', 'IN'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'POWER'),
    ('left', 'PIPE'),
    ('left', 'DOT'),
    ('right', 'NOT'),
    ('right', 'UMINUS'),
    ('left', 'LBRACKET'),
)
