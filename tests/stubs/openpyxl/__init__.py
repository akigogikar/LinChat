import json
import re

class Worksheet:
    def __init__(self):
        self.data = {}

    def __setitem__(self, key, value):
        self.data[key] = value

    def iter_rows(self, values_only=True):
        cells_by_row = {}
        for cell, val in self.data.items():
            m = re.match(r"([A-Z]+)(\d+)", cell)
            if not m:
                continue
            col, row = m.group(1), int(m.group(2))
            cells_by_row.setdefault(row, {})[col] = val
        rows = []
        for row_idx in sorted(cells_by_row):
            row = cells_by_row[row_idx]
            rows.append([row[c] for c in sorted(row)])
        return rows

class Workbook:
    def __init__(self):
        self.active = Worksheet()
        self.sheetnames = ["Sheet1"]

    def __getitem__(self, name):
        if name in self.sheetnames:
            return self.active
        raise KeyError(name)

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.active.data, f)

def load_workbook(path, data_only=True):
    wb = Workbook()
    try:
        with open(path, "r", encoding="utf-8") as f:
            wb.active.data = json.load(f)
    except FileNotFoundError:
        pass
    return wb
