from decimal import Decimal
from unittest import TestCase

import pytest

from smartquery.ast_ops import LambdaOp, NameOp
from smartquery.exceptions import ParserError
from smartquery.sq_parser import SqParser
from tests.utils import measure_for_tests


@pytest.fixture(scope='session')
def parser():
    return SqParser()


@pytest.mark.parametrize('expr, expected', [
    ('5 * 5 + 5 / 5', 26),
    ('5 * (20 - 10)', 50),
])
def test_arithmetic(parser, expr, expected):
    assert parser.eval(expr) == expected


@pytest.mark.parametrize('expr, expected', [
    ('-5', -5),
    ('-5 - -5', 0),
])
def test_unary_minus(parser, expr, expected):
    assert parser.eval(expr) == expected


@pytest.mark.parametrize('expr, expected', [
    ('0.1 + 0.1 + 0.1', Decimal('0.3')),
])
def test_decimal(parser, expr, expected):
    assert parser.eval(expr) == expected


@pytest.mark.parametrize('expr, expected', [
    ('2 == 2', True),
    ('2 == 3', False),

    ('2 != 3', True),
    ('3 != 3', False),

    ('2 < 3', True),
    ('3 < 2', False),

    ('3 > 2', True),
    ('2 > 3', False),

    ('2 <= 3', True),
    ('2 <= 3', True),
    ('2 <= 2', True),

    ('3 >= 2', True),
    ('2 >= 3', False),
    ('2 >= 2', True),
])
def test_rel(parser, expr, expected):
    assert parser.eval(expr) == expected


@pytest.mark.parametrize('expr, expected', [
    ('False and 1/0', False),
    ('True or 1/0', True),
])
def test_and_or_are_lazy(parser, expr, expected):
    assert parser.eval(expr) == expected


@pytest.mark.parametrize('expr, expected', [
    ('(0.2 + 0.8) * 5', Decimal('5')),
    ('5 * (0.2 + 0.8)', Decimal('5')),
    ('5 * 0.2 + 0.8', Decimal('1.8')),
])
def test_priority(parser, expr, expected):
    assert parser.eval(expr) == expected


@pytest.mark.parametrize('expr, expected', [
    ('round(2/3, 2)', Decimal('0.67')),
])
def test_round(parser, expr, expected):
    assert parser.eval(expr) == expected


@pytest.mark.parametrize('expr, expected', [
    ('', None),
    ('# asd', None),
    ('10  # asd', 10),
])
def test_comments(parser, expr, expected):
    assert parser.eval(expr) == expected


@pytest.mark.parametrize('expr, names, expected', [
    ('%сообщение% == "Привет" and %пол% == "мужской"', {
        '%сообщение%': 'Привет',
        '%пол%': 'мужской',
    }, True),
    ('%сообщение% == "Привет" and %пол% == "мужской"', {
        '%сообщение%': 'Привет',
        '%пол%': 'женский',
    }, False)
])
def test_vars(parser, expr, names, expected):
    assert parser.eval(expr, names=names) == expected


@pytest.mark.parametrize('expr, names, expected', [
    ('%сообщение% == "Привет" and %пол% == "мужской"'
     'or %сообщение% == "Пока" and %пол% == "женский"', {
        '%сообщение%': 'Привет',
        '%пол%': 'мужской',
    }, True),
    ('%сообщение% == "Привет" and %пол% == "мужской"'
     'or %сообщение% == "Пока" and %пол% == "женский"', {
        '%сообщение%': 'Привет',
        '%пол%': 'женский',
    }, False),
])
def test_complex_conditions(parser, expr, names, expected):
    assert parser.eval(expr, names=names) == expected


@pytest.mark.parametrize('expr, names, expected', [
    ('"Привет" in %сообщение% and %пол% == "мужской"', {
        '%сообщение%': 'Приветик',
        '%пол%': 'мужской',
    }, True),
    ('"Привет" in %сообщение% and %пол% == "мужской"', {
        '%сообщение%': 'Пока',
        '%пол%': 'женский',
    }, False),
])
def test_in(parser, expr, names, expected):
    assert parser.eval(expr, names=names) == expected


@pytest.mark.parametrize('expr, names, expected', [
    ('"Привет" not in %сообщение% and %пол% == "мужской"', {
        '%сообщение%': 'Тест',
        '%пол%': 'мужской',
    }, True),
    ('"Привет" not in %сообщение% and %пол% == "мужской"', {
        '%сообщение%': 'Привет',
        '%пол%': 'мужской',
    }, False),
])
def test_not_in(parser, expr, names, expected):
    assert parser.eval(expr, names=names) == expected


@pytest.mark.parametrize('expr, names, expected', [
    ('len(%сообщение%) > 3', {
        '%сообщение%': 'Приветик',
    }, True),
    ('len(%сообщение%) < 100', {
        '%сообщение%': 'Приветик',
    }, True),
])
def test_len(parser, expr, names, expected):
    assert parser.eval(expr, names=names) == expected


@pytest.mark.parametrize('expr, expected', [
    ('len(str(10)) == 2', True),
])
def test_nested_calls(parser, expr, expected):
    assert parser.eval(expr) == expected


@pytest.mark.parametrize('expr, names, expected', [
    ('x.lower() != x.lower()', {
        'x': 'test',
    }, False),
])
def test_methods_priority(parser, expr, names, expected):
    assert parser.eval(expr, names=names) == expected


@pytest.mark.parametrize('expr, expected', [
    ('True if 2 > 4 else False', False),
    ('True if 2 < 4 else False', True),
])
def test_if_expr(parser, expr, expected):
    assert parser.eval(expr) == expected


@pytest.mark.parametrize('expr, names, expected', [
    ('%сообщение%.startswith("привет")', {
        '%сообщение%': 'приветик',
    }, True),
    ('%сообщение%.endswith("ик")', {
        '%сообщение%': 'приветик',
    }, True),
    ('%сообщение%.startswith("привет")', {
        '%сообщение%': 'хуй',
    }, False),
    ('%сообщение%.endswith("ик")', {
        '%сообщение%': 'хуй',
    }, False),
])
def test_method_calls(parser, expr, names, expected):
    assert parser.eval(expr, names=names) == expected


@pytest.mark.parametrize('expr, names, expected', [
    ('%сообщение%.lower().startswith("привет")', {
        '%сообщение%': 'Приветик',
    }, True),
    ('%сообщение%.lower().endswith("ик")', {
        '%сообщение%': 'Приветик',
    }, True),
])
def test_nested_method_calls(parser, expr, names, expected):
    assert parser.eval(expr, names=names) == expected


@pytest.mark.parametrize('expr, names, expected', [
    ('" " in %сообщение%', {
        '%сообщение%': '1 2 3',
    }, True),
])
def test_space_string(parser, expr, names, expected):
    assert parser.eval(expr, names=names) == expected


def test_custom_python_functions(parser):
    assert parser.eval('test(2, 2)', names={
        'test': lambda a, b: a + b
    }) == 4


def test_custom_python_functions_override_priority(parser):
    assert parser.eval('lower("abc")', names={
        'lower': str.upper,
    }) == "ABC"


def test_custom_sq_functions(parser):
    assert parser.eval(
        r'''
        test = (a, b) => a + b
        test(2, 2)
        '''
    ) == 4


def test_custom_ast_functions(parser):
    f_body = parser.parse('\n'.join([
        'c = a + b',
        'c * 2',
    ]))

    f = LambdaOp(args=[
        NameOp('a'),
        NameOp('b'),
    ], expr=f_body)

    assert parser.eval(
        r'''
        f(1, 2)
        ''',
        ast_names={
            'f': f,
        },
    ) == 6


def test_call_multiline(parser):
    assert parser.eval('''
    len(
        [1, 2, 3]
    )
    ''') == 3


def test_list_multiline(parser):
    assert parser.eval('''
    [
        1, 2,
        3
    ]
    ''') == [1, 2, 3]


def test_dict_multiline(parser):
    assert parser.eval('''
    {
        'a': {
            'b': 20
        }
    }
    ''') == {
        'a': {
            'b': 20,
        },
    }


def test_trailing_comma_list(parser):
    assert parser.eval('[1, 2, 3,]') == [1, 2, 3, ]


def test_trailing_comma_dict(parser):
    assert parser.eval("{'a': 10,}") == {'a': 10, }


def test_trailing_comma_call(parser):
    assert parser.eval('max(1, 2, )') == max(1, 2, )


class TestSqParserFail(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = SqParser()

    def test_syntax_errors(self):
        for expr in [
            '5 * 5 + 5 // 5',
            '10 ++ 20',
            '10 % 20',
            'raise Exception',

            '5 in 2',
            'len()',
            'len(1, 2, 3)',
            'len(0)',

            'if = 1',
            'for = 1',
            'while = 1',
            'elif = 1',
            'raise = 1',
        ]:
            with self.subTest(expr):
                self.assert_raises(expr)

    def assert_raises(self, expr: str):
        with self.assertRaises(Exception):
            self.parser.eval(expr=expr)


class TestDicts(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = SqParser()

    def test_dict_literal(self):
        self.assertEqual(self.parser.eval('{}'), {})
        self.assertEqual(self.parser.eval('{"x": 10}'), {'x': 10})
        self.assertEqual(self.parser.eval('{"x": 10, "y": 20}'), {'x': 10, "y": 20})

    def test_dict_default_output(self):
        data = {
            'пончик': 1,
            'лазанья': 2,
        }

        self.assertEqual(self.parser.eval(
            '%корзина%', names={
                '%корзина%': data,
            }), data)

    def test_dict_pretty_output(self):
        data = {
            'пончик': 1,
            'лазанья': 2,
        }

        self.assertEqual(self.parser.eval(
            '%корзина% | pretty', names={
                '%корзина%': data,
            }), r'''
                пончик: 1
                лазанья: 2
            '''.replace('    ', '').strip())

    def test_dict_map(self):
        data = {
            'пончик': 1,
            'лазанья': 2,
        }

        self.assertEqual(self.parser.eval(
            '%корзина% | map((k, v) => k + ": " + v + " кг") | join', names={
                '%корзина%': data,
            }), r'''
                пончик: 1 кг
                лазанья: 2 кг
            '''.replace('    ', '').strip())

    def test_setitem(self):
        names = {
            '%корзина%': {},
            '%товар%': 'хлеб',
        }

        self.parser.eval(r'''%корзина%[%товар%] = 1''', names=names)
        self.assertEqual(names['%корзина%']['хлеб'], 1)

    def test_setitem_with_op(self):
        names = {
            'o': {
                'a': 10,
                'b': 10,
                'c': 10,
                'd': 10,
            },
        }

        self.parser.eval('o["a"] += 2', names=names)
        self.assertEqual(names['o']['a'], 12)

        self.parser.eval('o["b"] -= 2', names=names)
        self.assertEqual(names['o']['b'], 8)

        self.parser.eval('o["c"] *= 2', names=names)
        self.assertEqual(names['o']['c'], 20)

        self.parser.eval('o["d"] /= 2', names=names)
        self.assertEqual(names['o']['d'], 5)

    def test_getitem(self):
        names = {
            '%корзина%': {
                'хлеб': 10,
                'греча': 20,
            },
            '%товар%': 'греча',
        }

        res = self.parser.eval(r'''%корзина%[%товар%]''', names=names)
        self.assertEqual(res, 20)

    def test_getitem_slice(self):
        names = {
            'arr': [1, 2, 3, 4, 5],
        }

        self.assertEqual(self.parser.eval(r'''arr[1]''', names=names), 2)
        self.assertEqual(self.parser.eval(r'''arr[:]''', names=names), [1, 2, 3, 4, 5])

        self.assertEqual(self.parser.eval(r'''arr[1:2]''', names=names), [2])
        self.assertEqual(self.parser.eval(r'''arr[:2]''', names=names), [1, 2])
        self.assertEqual(self.parser.eval(r'''arr[3:]''', names=names), [4, 5])

        self.assertEqual(self.parser.eval(r'''arr[3::]''', names=names), [4, 5])
        self.assertEqual(self.parser.eval(r'''arr[:3:]''', names=names), [1, 2, 3])
        self.assertEqual(self.parser.eval(r'''arr[::2]''', names=names), [1, 3, 5])

        self.assertEqual(self.parser.eval(r'''arr[::-1]''', names=names), [5, 4, 3, 2, 1])

    def test_assign_ok(self):
        names = {}

        for value in [1, 'test', False, [], [1, 2, 3]]:
            with self.subTest(str(value)):
                if isinstance(value, str):
                    literal = f'"{value}"'
                else:
                    literal = value

                self.parser.eval(f'x = {literal}', names=names)
                self.assertEqual(names['x'], value)

    def test_short_op(self):
        names = {
            'a': 10,
            'b': 10,
            'c': 10,
            'd': 10,
        }
        self.parser.eval('a += 2', names=names)
        self.assertEqual(names['a'], 12)

        self.parser.eval('b -= 2', names=names)
        self.assertEqual(names['b'], 8)

        self.parser.eval('c *= 2', names=names)
        self.assertEqual(names['c'], 20)

        self.parser.eval('d /= 2', names=names)
        self.assertEqual(names['d'], 5)

    def test_assign_is_a_statement(self):
        with self.assertRaises(ParserError):
            self.parser.eval('x = y = 10')

    def test_assign_priority(self):
        names = {}

        self.parser.eval(f'x = 2 * 2', names=names)
        self.assertEqual(names['x'], 4)

    def test_assign_dict(self):
        names = {}

        self.parser.eval(r'''d = dict()''', names=names)
        self.assertEqual(names['d'], dict())

    def test_del(self):
        names = {
            'd': {
                'x': 10,
            }
        }

        self.parser.eval(r'''del d['x']''', names=names)
        self.assertEqual(names['d'], dict())


class TestArrays(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = SqParser()

    def test_array_defs(self):
        for value in [[], [1], [1, 2, 3], ['test']]:
            with self.subTest(str(value)):
                self.assertEqual(self.parser.eval(str(value)), value)

    def test_map(self):
        self.assertEqual(self.parser.eval('[1, 2, 3] | map(v => v * 2)'), [2, 4, 6])

    def test_reduce(self):
        self.assertEqual(self.parser.eval('[1, 2, 3] | reduce((acc, v) => acc + v)'), 6)

    def test_push(self):
        names = {
            'arr': [1, 2]
        }

        self.parser.eval('arr.push(3)', names=names)
        self.assertEqual(names['arr'], [1, 2, 3])

    def test_index_precedence(self):
        names = {
            'a': [2]
        }

        self.assertEqual(self.parser.eval('1 + a[0]', names=names), 3)
        self.assertEqual(self.parser.eval('1 + -a[0]', names=names), -1)

    def test_del_nested(self):
        names = {
            'a': [[1, 2, 3], [4, 5, 6]],
        }

        self.parser.eval(r'''del a[1][1]''', names=names)
        self.assertEqual(names['a'], [[1, 2, 3], [4, 6]])

    def test_methods(self):
        self.assertEqual(self.parser.eval('enumerate([1, 2, 3])'), list(
            enumerate([1, 2, 3])
        ))

        self.assertEqual(len(self.parser.eval('shuffle([1, 2, 3])')), 3)

    def test_index_of(self):
        self.assertEqual(self.parser.eval('[1, 2, 3] | index_of(2)'), 1)
        self.assertEqual(self.parser.eval('[1, 2, 3] | index_of(5)'), None)


class TestSafety(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = SqParser()

    def test_long_comp(self):
        res = self.parser.eval('int(1000) ** int(100000)')
        self.assertIsInstance(res, Decimal)

    def test_eval_limit(self):
        lst = [1] * 1000
        with self.assertRaises(ParserError):
            self.parser.eval('l | map(v => v)', names={
                'l': lst,
            })


class TestPretty(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = SqParser()

    def test_numbers(self):
        self.assertEqual(self.parser.eval('1234 | pretty'), '1234')
        self.assertEqual(self.parser.eval('-1234 | pretty'), '-1234')

        self.assertEqual(self.parser.eval('12345 | pretty'), '12 345')
        self.assertEqual(self.parser.eval('12345 | pretty'), '12 345')

        self.assertEqual(self.parser.eval('123456789 | pretty'), '123 456 789')
        self.assertEqual(self.parser.eval('-123456789 | pretty'), '-123 456 789')


class TestBuiltinFunctions(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = SqParser()

    def test_rand(self):
        res = self.parser.eval('rand()')
        self.assertGreaterEqual(res, 0)
        self.assertLess(res, 1)

    def test_rand_ab(self):
        res = self.parser.eval('rand(1, 10)')
        self.assertGreaterEqual(res, 1)
        self.assertLessEqual(res, 10)

    def test_rand_list(self):
        res = self.parser.eval('rand([1, 2, 3])')
        self.assertIn(res, [1, 2, 3])


class TestMultiline(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = SqParser()

    def test_ok(self):
        res = self.parser.eval(r'''
            x = 10
            y = 20
            x + y
        ''')
        self.assertEqual(res, 30)

    def test_empty(self):
        res = self.parser.eval('')
        self.assertEqual(res, None)

    def test_empty_line(self):
        res = self.parser.eval(r'''
            x = 10
            y = 20

            x + y
        ''')
        self.assertEqual(res, 30)

    def test_start_empty_line(self):
        res = self.parser.eval(r'''

            2 * 2
        ''')
        self.assertEqual(res, 4)

    def test_semicolon(self):
        assert self.parser.eval('2 * 2; 5 * 5') == 25

    def test_error(self):
        with self.assertRaisesRegex(ParserError, 'Syntax error: asd at line 5'):
            self.parser.eval(r'''
                x = 10
                y = 20

                x + y asd
            ''')
        assert self.parser.eval('2 * 2; 5 * 5') == 25


class TestRegex(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = SqParser()

    def test_match(self):
        self.assertEqual(self.parser.eval(
            r'"1234 test" | match(r"\d+")'), '1234')

        self.assertEqual(self.parser.eval(
            r'"1234 test" | match(r"(\d+)")'), '1234')

    def test_match_groups(self):
        self.assertEqual(self.parser.eval(
            r'"1234 test" | match_groups(r"\d+")'), ['1234'])

        self.assertEqual(self.parser.eval(
            r'"1234 test" | match_groups(r"(\d+)")'), ['1234', '1234'])

    def test_match_flags(self):
        self.assertEqual(self.parser.eval(
            r'"TEST" | match(r"test")'), None)

        self.assertEqual(self.parser.eval(
            r'"TEST" | match(r"test", "i")'), 'TEST')

    def test_match_all(self):
        self.assertEqual(self.parser.eval(
            r'"test 1234 test 256" | match_all(r"\d+")'), ['1234', '256'])


class TestPerf(TestCase):
    RUNS = 100

    def test_perf_no_cache(self):
        self.parser = SqParser()

        names = {
            '%сообщение%': 'Привет',
            '%пол%': 'мужской',
        }

        measure_for_tests(lambda: self.parser.eval(
            '%сообщение% == "Привет" and %пол% == "мужской"', names=names), iterations=self.RUNS)

    def test_perf(self):
        self.parser = SqParser(parse_cache={})

        names = {
            '%сообщение%': 'Привет',
            '%пол%': 'мужской',
        }

        measure_for_tests(lambda: self.parser.eval(
            '%сообщение% == "Привет" and %пол% == "мужской"', names=names), iterations=self.RUNS)
