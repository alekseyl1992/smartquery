from smartquery.sq_parser import SqParser


def repl():
    from prompt_toolkit import PromptSession

    session = PromptSession()

    parser = SqParser()
    names = {}

    while True:
        try:
            expr = session.prompt('>>> ', enable_history_search=True)
        except KeyboardInterrupt:
            print()
            return 0

        if not expr:
            continue

        try:
            res = parser.eval(expr=expr, names=names)
            if res is not None:
                print(repr(res))
        except Exception as e:
            print(repr(e))


if __name__ == '__main__':
    exit(repl())
