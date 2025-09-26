from src.categorise import categorise
from src.csv_functions import format_CSV
from src.spreadsheet_functions import update_spreadsheet


def main():
    data = categorise(format_CSV())
    update_spreadsheet(data)


if __name__ == "__main__":
    main()
