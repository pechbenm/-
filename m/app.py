import sys
import re
from datetime import datetime
from tinydb import TinyDB

db = TinyDB('db.json')

def is_valid_date(value: str) -> bool:
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            pass
    return False

def is_valid_phone(value: str) -> bool:
    return bool(re.fullmatch(r'\+7 \d{3} \d{3} \d{2} \d{2}', value))

def is_valid_email(value: str) -> bool:
    return bool(re.fullmatch(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', value))

def detect_field_type(value: str) -> str:
    if is_valid_date(value):
        return "date"
    if is_valid_phone(value):
        return "phone"
    if is_valid_email(value):
        return "email"
    return "text"

def parse_args(args):
    res = {}
    for arg in args:
        if arg.startswith("--"):
            parts = arg[2:].split("=", 1)
            if len(parts) == 2:
                res[parts[0]] = parts[1]
    return res

def find_best_match(input_fields):
    best_match = None
    max_score = 0

    for template in db.all():
        name = template.get("name")
        if not name:
            continue

        score = 0
        valid = True

        for field_name, value in input_fields.items():
            if field_name in template:
                expected_type = template[field_name]
                actual_type = detect_field_type(value)
                if actual_type == expected_type:
                    score += 1
                else:
                    valid = False
                    break

        if not valid:
            continue

        if score > max_score:
            max_score = score
            best_match = name

    return best_match if max_score > 0 else None

def main():
    if len(sys.argv) < 2 or sys.argv[1] != "get_tpl":
        print("Usage: app.py get_tpl --field=value ...")
        sys.exit(1)

    inputs = parse_args(sys.argv[2:])
    if not inputs:
        print("{}")
        return

    matched = find_best_match(inputs)

    if matched:
        print(matched)
    else:
        detected = {k: detect_field_type(v) for k, v in inputs.items()}
        lines = [f'"{k}": "{v}"' for k, v in detected.items()]
        print("{\n" + ",\n".join(lines) + "\n}")

if __name__ == "__main__":
    main()
#python app.py get_tpl --customer=John Smith --order_date=27.05.2025