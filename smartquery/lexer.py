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
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA = r','
t_DOT = r'\.'
t_PIPE = r'\|'
t_COLON = r':'

t_LBRACKET = r'\['
t_RBRACKET = r'\]'

t_LBRACE = r'{'
t_RBRACE = r'}'

t_NEWLINE = r'\r\n|\n|;'


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
