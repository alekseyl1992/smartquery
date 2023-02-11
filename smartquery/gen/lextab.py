# lextab.py. This file automatically created by PLY (version 3.11). Don't edit!
_tabversion   = '3.10'
_lextokens    = set(('AND', 'ASSIGN', 'BREAK', 'COLON', 'COMMA', 'COMMENT', 'CONTINUE', 'DEF', 'DEL', 'DIVIDE', 'DOT', 'ELIF', 'ELSE', 'EQ', 'FALSE', 'FOR', 'GT', 'GTE', 'IF', 'IN', 'LAMBDA', 'LBRACE', 'LBRACKET', 'LPAREN', 'LT', 'LTE', 'MINUS', 'NAME', 'NE', 'NEWLINE', 'NONE', 'NOT', 'NUMBER', 'OR', 'PIPE', 'PLUS', 'POWER', 'RAISE', 'RBRACE', 'RBRACKET', 'RPAREN', 'SHORT_OP', 'STRING', 'TIMES', 'TRUE', 'WHILE'))
_lexreflags   = 64
_lexliterals  = ''
_lexstateinfo = {'INITIAL': 'inclusive'}
_lexstatere   = {'INITIAL': [('(?P<t_NEWLINE>\\r\\n|\\n|;)|(?P<t_LPAREN>\\()|(?P<t_RPAREN>\\))|(?P<t_LBRACKET>\\[)|(?P<t_RBRACKET>\\])|(?P<t_LBRACE>{)|(?P<t_RBRACE>})|(?P<t_STRING> (r?\\"([^\\\\\\n]|(\\\\.))*?\\") | (r?\\\'([^\\\\\\n]|(\\\\.))*?\\\') )|(?P<t_NUMBER> \\d+(\\.\\d+)? )|(?P<t_NAME> (%.*?%) | ([^\\W\\d][\\w0-9_]*([\\w_][\\w0-9_]*)*) )|(?P<t_COMMENT> \\043.* )|(?P<t_SHORT_OP>[+\\-\\*/]=)|(?P<t_POWER>\\*\\*)|(?P<t_DOT>\\.)|(?P<t_EQ>==)|(?P<t_GTE>>=)|(?P<t_LAMBDA>=>)|(?P<t_LTE><=)|(?P<t_NE>!=)|(?P<t_PIPE>\\|)|(?P<t_PLUS>\\+)|(?P<t_TIMES>\\*)|(?P<t_ASSIGN>=)|(?P<t_COLON>:)|(?P<t_COMMA>,)|(?P<t_DIVIDE>/)|(?P<t_GT>>)|(?P<t_LT><)|(?P<t_MINUS>-)', [None, ('t_NEWLINE', 'NEWLINE'), ('t_LPAREN', 'LPAREN'), ('t_RPAREN', 'RPAREN'), ('t_LBRACKET', 'LBRACKET'), ('t_RBRACKET', 'RBRACKET'), ('t_LBRACE', 'LBRACE'), ('t_RBRACE', 'RBRACE'), ('t_STRING', 'STRING'), None, None, None, None, None, None, ('t_NUMBER', 'NUMBER'), None, ('t_NAME', 'NAME'), None, None, None, ('t_COMMENT', 'COMMENT'), (None, 'SHORT_OP'), (None, 'POWER'), (None, 'DOT'), (None, 'EQ'), (None, 'GTE'), (None, 'LAMBDA'), (None, 'LTE'), (None, 'NE'), (None, 'PIPE'), (None, 'PLUS'), (None, 'TIMES'), (None, 'ASSIGN'), (None, 'COLON'), (None, 'COMMA'), (None, 'DIVIDE'), (None, 'GT'), (None, 'LT'), (None, 'MINUS')])]}
_lexstateignore = {'INITIAL': ' \t'}
_lexstateerrorf = {'INITIAL': 't_error'}
_lexstateeoff = {}
