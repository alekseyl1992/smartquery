from smartquery import lexer
from smartquery.ast_ops import ValueOp, UnaryOp, NameOp, AssignOp, CallOp, LambdaOp, BinOp, IfExprOp, NoOp, \
    SliceOp, Op, DictOp, CodeOp, ShortOp
from smartquery.exceptions import ParserError


tokens = lexer.tokens
precedence = lexer.precedence


def p_code(p):
    """ code : line
             | code NEWLINE line"""
    p[0] = p[1]

    if len(p) == 2:
        p.lexer.ast = CodeOp([p[1]]) if p[1] is not None else CodeOp([])
    else:
        if p[3] is not None:
            p.lexer.ast.lines.append(p[3])


def p_line(p):
    """ line : statement """
    p[0] = p[1]


def p_statement_expr(p):
    """ statement : expression"""
    p[0] = p[1]


def p_statement_empty(p):
    """ statement : """
    pass


def p_statement_comment(p):
    """ statement : COMMENT """
    p[0] = NoOp()


def p_expression_reserved_unused(p):
    """ expression : FOR
                   | WHILE
                   | ELIF
                   | BREAK
                   | CONTINUE
                   | DEF
                   | RAISE"""
    raise ParserError(f'{p[1]} is reserved keyword')


def p_expression_number(p):
    """ expression : NUMBER """
    p[0] = ValueOp(p[1])


def p_expression_string(p):
    """ expression : STRING """
    p[0] = ValueOp(p[1])


def p_statement_assign(p):
    """ statement : NAME ASSIGN expression """
    p[0] = AssignOp(p[1], p[3])


def p_statement_short_op(p):
    """ statement : NAME SHORT_OP expression """
    p[0] = ShortOp(p[1], p[2], p[3])


def p_expression_call(p):
    """ expression : NAME LPAREN arglist RPAREN
                   | NAME LPAREN arglist COMMA RPAREN
                   | NAME LPAREN RPAREN
    """
    if len(p) >= 5:
        p[0] = CallOp(p[1], args=p[3])
    else:
        p[0] = CallOp(p[1], args=[])


def p_expression_method_call(p):
    """ expression : expression DOT NAME LPAREN arglist RPAREN
                   | expression PIPE NAME LPAREN arglist RPAREN
                   | expression DOT NAME LPAREN arglist COMMA RPAREN
                   | expression PIPE NAME LPAREN arglist COMMA RPAREN
                   | expression DOT NAME LPAREN RPAREN
                   | expression PIPE NAME
    """
    len_p = len(p)
    if len_p == 7:
        p[0] = CallOp(p[3], args=[p[1], *p[5]])
    elif len_p == 8:
        p[0] = CallOp(p[3], args=[p[1], *p[5][:-1]])
    else:
        p[0] = CallOp(p[3], args=[p[1]])


def p_expression_lambda(p):
    """ expression : NAME LAMBDA expression
                   | LPAREN arglist_def RPAREN LAMBDA expression
    """
    if len(p) == 4:
        p[0] = LambdaOp(args=[NameOp(p[1])], expr=p[3])
    else:
        p[0] = LambdaOp(args=p[2], expr=p[5])


def p_dict_item(p):
    """ dict_item : dict_item COMMA dict_item
                  | expression COLON expression
    """
    if p.slice[1].type == 'dict_item':
        p[0] = p[1] + p[3]
    else:
        p[0] = [(p[1], p[3])]


def p_expression_binop(p):
    """ expression : expression PLUS expression
                   | expression MINUS expression
                   | expression TIMES expression
                   | expression POWER expression
                   | expression DIVIDE expression
                   | expression EQ expression
                   | expression NE expression
                   | expression GT expression
                   | expression LT expression
                   | expression GTE expression
                   | expression LTE expression
                   | expression NOT IN expression
                   | expression IN expression
                   | expression AND expression
                   | expression OR expression
    """
    if p.slice[3].type == 'IN':
        p[0] = BinOp('not in', p[1], p[4])
    else:
        p[0] = BinOp(p[2], p[1], p[3])


def p_list_literal(p):
    """ expression : LBRACKET RBRACKET
                   | LBRACKET arglist RBRACKET
                   | LBRACKET arglist COMMA RBRACKET
    """
    if len(p) == 3:
        p[0] = CallOp(name='list', args=[])
    else:
        p[0] = CallOp(name='list', args=p[2])


def p_dict_literal(p):
    """ expression : LBRACE RBRACE
                   | LBRACE dict_item RBRACE
                   | LBRACE dict_item COMMA RBRACE
    """
    if len(p) == 3:
        p[0] = CallOp(name='dict', args=[])
    else:
        p[0] = DictOp(p[2])


def p_slice(p):
    """ slice : expression
              | COLON
              | expression COLON expression
              | expression COLON
              | COLON expression
              | expression COLON COLON
              | COLON expression COLON
              | COLON COLON expression
    """
    p[0] = p[1:]


def p_getitem(p):
    """ expression : expression LBRACKET slice RBRACKET
                   | expression LBRACKET expression RBRACKET
    """
    key = p[3]
    if isinstance(key, Op):
        # just a single index
        p[0] = CallOp(name='__getitem__', args=[p[1], key])
    else:
        # slice
        args = []
        was_arg = False
        for el in key:
            if el == ':':
                if not was_arg:
                    args.append(ValueOp(None))
                else:
                    was_arg = False
            else:
                args.append(el)
                was_arg = True

        p[0] = CallOp(name='__getitem__', args=[p[1], SliceOp(*args)])


def p_delitem(p):
    """ statement : DEL expression LBRACKET expression RBRACKET
    """
    p[0] = CallOp(name='__delitem__', args=[p[2], p[4]])


def p_setitem(p):
    """ statement : expression LBRACKET expression RBRACKET ASSIGN expression
    """
    p[0] = CallOp(name='__setitem__', args=[p[1], p[3], p[6]])


def p_setitem_with_op(p):
    """ statement : expression LBRACKET expression RBRACKET SHORT_OP expression
    """
    p[0] = CallOp(name='__setitem_with_op__', args=[p[1], p[3], ValueOp(p[5]), p[6]])


def p_if_expr(p):
    """ expression : expression IF expression ELSE expression
    """
    p[0] = IfExprOp(cond=p[3], op1=p[1], op2=p[5])


def p_expression_uminus(p):
    """ expression : MINUS expression %prec UMINUS """
    p[0] = UnaryOp('-', p[2])


def p_expression_group(p):
    """ expression : LPAREN expression RPAREN"""
    p[0] = p[2]


def p_expression_true(p):
    """ expression : TRUE """
    p[0] = ValueOp(True)


def p_expression_false(p):
    """ expression : FALSE """
    p[0] = ValueOp(False)


def p_expression_none(p):
    """ expression : NONE """
    p[0] = ValueOp(None)


def p_expression_not(p):
    """ expression : NOT expression """
    p[0] = UnaryOp('not', p[2])


def p_expression_name(p):
    """ expression : NAME """
    p[0] = NameOp(p[1])


def p_arglist(p):
    """ arglist : arglist COMMA expression
                | expression
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_arglist_def(p):
    """ arglist_def : arglist COMMA NAME
                    | NAME
    """
    if len(p) == 4:
        p[0] = p[1] + [NameOp(p[3])]
    else:
        p[0] = [NameOp(p[1])]


def p_error(p):
    raise ParserError(f'Syntax error: {p.value} at line {p.lexer.lineno}')
