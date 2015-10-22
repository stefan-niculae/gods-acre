import json
from random import randint
from datetime import date


class Row:
    def __init__(self, id, parcel, row, column, year, value, receipt):
        self.id = id
        self.parcel = parcel
        self.row = row
        self.column = column
        self.year = year
        self.value = value
        self.receipt = receipt
    
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def generate_rows(n):
    rows = []
    
    letter_suffixes = ['', 'A', 'B', 'C', 'bis']
    m = len(letter_suffixes) - 1
    
    for i in range(n):
        year = randint(1990, date.today().year)
        
        row = Row(
            id=i,
            parcel=str(randint(1, n//5)) + letter_suffixes[randint(0, m)],
            row=str(randint(1, n//5)) + letter_suffixes[randint(0, m)],
            column=str(randint(1, n//5)) + letter_suffixes[randint(0, m)],
            year=year,
            value=randint(100 // 5, 200 // 5) * 5,
            receipt=str(randint(1, n // 5)) + '/' + str(randint(year - 5, year + 5)))
        rows.append(row)
            
    print('[\n' + ',\n'.join(row.to_JSON() for row in rows) + '\n]')
    
generate_rows(100)
    