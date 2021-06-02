from datetime import timedelta


class PeriodUnion:
    def __init__(self, start, end, price):
        self.start = start
        self.end = end
        self.price = price

    def in_range(self, date):
        return self.start <= date <= self.end

    def can_be_added(self, period):
        next_day = self.end + timedelta(1) == period.start or period.end + timedelta(1) == self.start
        intersection = any([
            self.in_range(period.start) and self.in_range(period.end),
            period.end >= self.end and self.in_range(period.start),
            self.in_range(period.end) and period.start <= self.start,
            period.end >= self.end and self.start >= period.start
        ])

        return next_day or intersection

    def add(self, period):
        if self.start >= period.start:
            self.start = period.start

        if period.end >= self.end:
            self.end = period.end

        self.price += period.price


def group_periods_by_services(periods):
    groups = dict()

    for period in periods:
        if period.service not in groups:
            groups[period.service] = []
        groups[period.service].append(period)

    return groups


def unite_by_date(periods):
    if not periods:
        return []
    periods = sorted(periods, key=lambda x: x.start)
    unions = []

    for period in periods:
        added = False
        for union in unions:
            if union.can_be_added(period):
                union.add(period)
                added = True
                break
        if not added:
            unions.append(PeriodUnion(period.start, period.end, period.price))

    return unions


def format_date(date):
    return '.'.join(reversed(str(date).split('-')))


def unite_contracts(groups):
    contracts = []
    for group in groups:
        unions = unite_by_date(groups[group])
        for union in unions:
            contracts.append({
                "range": f"с {format_date(union.start)}г. по {format_date(union.end)}г.",
                "price": union.price,
                "service": group
            })

    return contracts
