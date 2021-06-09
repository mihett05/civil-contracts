from datetime import timedelta, date
from docxtpl import DocxTemplate
from .num_to_text import num2text

from periods.models import services


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


def make_word(contract, worker, dir_name):
    worker_text = f"{worker.name}, именуем(ая)ый в дальнейшем «Исполнитель», {worker.birth}г. рождения, " \
                  f"проживающ(ая)ый по адресу: {worker.address}, паспорт: {str(worker.passport_serial)[:2]} " \
                  f"{str(worker.passport_serial)[2:4]} №{str(worker.passport_serial)[4:]}, {worker.passport_date}," \
                  f"{worker.passport_issuer}"
    price_text = num2text(int(contract["price"]), (("рубль", "рубля", "рублей"), "m")).capitalize().split()
    price_num = "{:,}".format(int(contract["price"])).replace(",", " ")
    start = date(*reversed(list(map(int, contract["range"].split("по")[0][1:].strip()[:-2].split(".")))))
    date_text = f"«{start.strftime('%d')}» m {start.year}г.".replace("m", {
        1: "января",
        2: "февраля",
        3: "марта",
        4: "апреля",
        5: "мая",
        6: "июня",
        7: "июля",
        8: "августа",
        9: "сентября",
        10: "октября",
        11: "ноября",
        12: "декабря",
    }[start.month])

    doc = DocxTemplate("templates/template.docx")
    doc.render({
        "worker": worker_text,
        "service_name": contract["service"],
        "service_list": services[contract["service"]]["list"],
        "service_paragraph_2": services[contract["service"]]["2"],
        "range": contract["range"],
        "price": f"{price_num} ({' '.join(price_text[:-1])}) {price_text[-1]}",
        "date": date_text
    })
    file = f"{dir_name}/{contract['range']}_{contract['service']}_{worker.name}.docx"
    doc.save(file)

    return file
