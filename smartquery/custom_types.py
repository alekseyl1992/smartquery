from decimal import Decimal as Decimal_


class Decimal(Decimal_):
    def __repr__(self):
        return super().__str__()
