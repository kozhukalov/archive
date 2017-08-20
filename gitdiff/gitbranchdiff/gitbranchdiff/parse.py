import string

import ply.lex as lex
import ply.yacc as yacc

from . import config


tokens = (
    'TITLE',
    'CHANGE_ID',
    'IMPLEMENTS',
    'CLOSES_BUG',
    'RELATED_BUG',
    'PARTIAL_BUG',
    'LINE',
    'NEWLINE',
)

t_CHANGE_ID = r'(?i)Change-Id:[^\n]+'
t_IMPLEMENTS = r'(?i)Implements:[^\n]+'
t_CLOSES_BUG = r'(?i)Closes-Bug:[^\n]+'
t_RELATED_BUG = r'(?i)Related-Bug:[^\n]+'
t_PARTIAL_BUG = r'(?i)Partial-Bug:[^\n]+'
t_TITLE = r'^[^\n]+'
t_LINE = r'[^\n]+'


def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.value = '\n'
    return t


def t_error(t):
    pass


def debug(func):
    def _func(p):
        if config.DEBUG:
            print func.__name__
            for i, item in enumerate(p):
                print("before p[%s] = %s" % (i, item))
        result = func(p)
        if config.DEBUG:
            for i, item in enumerate(p):
                print("after p[%s] = %s" % (i, item))
        return result
    _func.__doc__ = func.__doc__
    return _func


@debug
def p_commit_message_title_no_description(p):
    """commit_message : title refs"""
    p[0] = {'title': p[1], 'refs': p[2]}


@debug
def p_commit_message_title_only(p):
    """commit_message : title"""
    p[0] = {'title': p[1]}


@debug
def p_commit_message_no_refs(p):
    """commit_message : title lines"""
    p[0] = {'title': p[1], 'description': p[2]}


@debug
def p_commit_message_description_refs(p):
    """commit_message : title lines refs"""
    p[0] = {'title': p[1], 'description': p[2], 'refs': p[3]}


@debug
def p_title(p):
    """title : TITLE
             | TITLE NEWLINE"""
    p[0] = p[1]


@debug
def p_lines(p):
    """lines : line
             | line lines"""
    if len(p) == 3:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]


@debug
def p_line(p):
    """line : LINE
            | LINE NEWLINE"""
    p[0] = p[1]


@debug
def p_refs(p):
    """refs : ref
            | ref refs"""
    if len(p) == 3:
        # p[1] is (reftype, refvalue)
        # p[2] is [(reftype1, refvalue1), (reftype2, refvalue2)]
        p[0] = p[2]
        p[0].append(p[1])
    else:
        # p[0] should be a list of refs
        p[0] = [p[1]]

@debug
def p_refs_lines(p):
    """refs : ref lines
            | ref lines refs"""
    if len(p) == 4:
        p[0] = p[3]
        p[0].append(p[1])
    else:
        p[0] = [p[1]]


@debug
def p_ref(p):
    """ref : CHANGE_ID
           | CHANGE_ID NEWLINE
           | IMPLEMENTS
           | IMPLEMENTS NEWLINE
           | CLOSES_BUG
           | CLOSES_BUG NEWLINE
           | RELATED_BUG
           | RELATED_BUG NEWLINE
           | PARTIAL_BUG
           | PARTIAL_BUG NEWLINE"""
    try:
        reftype, refvalue = p[1].split(':', 1)
    except ValueError:
        return
    p[0] = (string.strip(reftype).lower(), string.strip(refvalue, '# '))


def parse_commit_message(data):
    lexer = lex.lex()
    parser = yacc.yacc()

    if config.DEBUG:
        print("=============================")
        print("raw commit message: \n%s" % data)
        lexer.input(data)
        for tok in lexer:
            print tok
        parsed = parser.parse(data, debug=config.DEBUG_YACC)
        print("parsed commit message: \n%s" % parsed)
        return parsed
    return parser.parse(data)
