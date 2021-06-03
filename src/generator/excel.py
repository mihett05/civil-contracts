import openpyxl
from datetime import datetime

from people.models import Worker
from periods.models import Period


def load_people(filename):
    wb = openpyxl.load_workbook(filename)
    sheet = wb.active

    for row in sheet["A3":f"F{sheet.max_row}"]:
        if len(row) == 6:
            values = [col.value for col in row]
            if all(values):
                name, birth, address, passport, sum_price, dates = values

                sum_price = int(sum_price)
                if isinstance(birth, datetime):
                    birth = birth.strftime("%d.%m.%Y")

                passport_data = passport.split(",", 2)
                date = passport_data[1].strip()
                serial = int(passport_data[0].replace("№", "").replace(" ", ""))
                issuer = passport_data[2].strip()

                worker = Worker.objects.filter(name=name.strip()).first()
                if not worker:
                    worker = Worker(
                        name=name,
                        birth=birth,
                        address=address,
                        passport_serial=serial,
                        passport_date=date,
                        passport_issuer=issuer
                    )
                    worker.save()

                Period(
                    worker=worker,
                    price=float(sum_price),
                    start=datetime.strptime(dates.split("-")[0], "%d.%m.%Y"),
                    end=datetime.strptime(dates.split("-")[1], "%d.%m.%Y"),
                    service="информационно-библиографические"
                ).save()


