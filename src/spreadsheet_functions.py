import gspread
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1

from src.api.constants import auth_scope, service_acc_path
from src.constants import amt_col, cat_col, desc_col, month_col, spreadsheet_name


def fetch_google_sheet(spreadsheet_name):
    # Creates a credentials object using the service account credential from the JSON file generated from Google scoped to the specified APIs
    creds = Credentials.from_service_account_file(service_acc_path, scopes=auth_scope)

    # Creates a "logged in" client using the credentials object
    client = gspread.authorize(creds)
    try:
        # Opens the specified Google spreadsheet and returns it to be used
        spreadsheet = client.open(spreadsheet_name)
        return spreadsheet
    except Exception as e:
        print("❌ Access denied or insufficient permissions")
        print("Error:", e)


def update_spreadsheet(dataframe):
    # Retrieve Google spreadsheet
    finances_spreadsheet = fetch_google_sheet(spreadsheet_name)

    # Group the dataframe by the month column and each month dataframe has the description, amount, and category columns, then loop through each group extracting the month name and the month datafram
    for month, month_df in dataframe.groupby([month_col])[[desc_col, amt_col, cat_col]]:
        # Retrieve the month sheet from the Google spreadsheet.
        # NOTE: month is a tuple thus month[0]
        month_sheet = finances_spreadsheet.worksheet(month[0])  # pyright: ignore

        # Retrieve the first column of the sheet which has the categories
        headers = month_sheet.row_values(1)

        # This list will contain the data to be sent to the sheet
        requests = []

        # For each month dataframe group by category and each category dataframe has the description and amount columns, then loop through each group extracting the category and the category dateframe
        for category, category_df in month_df.groupby([cat_col])[[desc_col, amt_col]]:
            # Find the starting column for each category and adds one for 1-based rows and columns for gspread library
            # NOTE: category is a tuple thus month[0]
            start_col = headers.index(category[0]) + 1

            # Computes the length of the category column and adds 1 to find the next available row
            col_data = month_sheet.col_values(start_col)
            start_row = len(col_data) + 1

            # Computes the last row by starting at start_row adding the length of the category dataframe then subtracting 1
            end_row = start_row + len(category_df) - 1

            # Computes the starting cell and ending cell by converting the (row, col) pair into a spreadsheet cell location
            start_cell = rowcol_to_a1(start_row, start_col)
            end_cell = rowcol_to_a1(end_row, start_col + 1)
            cell_range = f"{start_cell}:{end_cell}"

            # Creates a list[][] where the outer index is the row and the inner index are the values [desc, amt
            values = category_df.values.tolist()

            # Creates a dict that gspread expects and appends to the requests list
            requests.append({"range": cell_range, "values": values})

        # Send the data off to the Google Sheet
        month_sheet.batch_update(requests)
