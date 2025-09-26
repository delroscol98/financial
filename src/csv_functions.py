import csv
import os
import shutil

import numpy as np
import pandas as pd


def add_header_to_CSV(csv_file_path, new_row=None):
    # if the CSV file does not exitst immediately return
    if not os.path.exists(csv_file_path):
        return

    # If the new row is not specified, then add the following new_row
    if new_row is None:
        new_row = ["date", "amount", "description", "category", "month"]

    # read the CSV file with the csv library which creates a reader object, converted into a list[][] where each index is each row and the inner index is the column
    with open(csv_file_path, "r", newline="") as infile:
        reader = csv.reader(infile)
        data = list(reader)

    # If the first row is already the wanted row, immediately return
    if data[0] == new_row:
        return

    # Insert the new row at the beginning of the list[][] shifting all other rows down
    data.insert(0, new_row)

    # Write the data to the CSV file with the csv library which creates a writer object, which overwrites the old CSV file with the new list[][] data
    with open(csv_file_path, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerows(data)


# Recursively grab all CSVs in ./data directory and put them in a list
def fetch_CSVs(csv_list=None, dir_name=None):
    if csv_list is None:
        csv_list = []

    if dir_name is None:
        dir_name = "./data"

    dir_path = os.path.abspath(dir_name)

    if not os.path.exists(dir_path):
        raise ValueError("Directory containing CSVs does not exist")

    dir_contents = os.listdir(dir_path)

    for item in dir_contents:
        item_path = f"{dir_path}/{item}"

        if os.path.isdir(item_path):
            fetch_CSVs(csv_list, item_path)

        if os.path.isfile(item_path):
            _, extension = os.path.splitext(item_path)
            if extension.lower() == ".csv":
                add_header_to_CSV(item_path)
                csv_list.append(item_path)

    return csv_list


def merge_CSVs(csv_list=None, merged_df=None):
    if csv_list is None:
        csv_list = fetch_CSVs()

    if len(csv_list) == 0:
        return merged_df

    if merged_df is None:
        merged_df = pd.read_csv(csv_list.pop())

    while len(csv_list) > 0:
        new_df = pd.read_csv(csv_list.pop())
        merged_df = pd.concat([merged_df, new_df], ignore_index=True)

        return merge_CSVs(csv_list, merged_df)


# function to merge debit CSV and credit CSV
def format_CSV():
    merged_df = merge_CSVs()

    if merged_df is None:
        raise ValueError("merged_df is None check if there are CSV files in ./data")

    # Set ALL the values of the category column to an empty string
    merged_df["category"] = ""

    # Convert ALL the values of the description column to uppercase
    merged_df["description"] = merged_df["description"].str.upper()

    # Change the type of the "DATE" column from string to datetime object, then grab the set the values of "MONTH" column to the corresponding month
    merged_df["date"] = pd.to_datetime(
        merged_df["date"], dayfirst=True, errors="coerce"
    )
    merged_df["month"] = merged_df["date"].dt.month_name()

    # Sort dataframe according to "DATE" column
    merged_df = merged_df.sort_values(by="date")

    # Convert each float into an unsigned float
    merged_df["amount"] = np.abs(merged_df["amount"])

    # Converts the dataframes columns into the appropriate types
    merged_df = merged_df.astype(
        {
            "date": "datetime64[ns]",
            "amount": "float",
            "description": "str",
            "category": "str",
            "month": "str",
        }
    )

    with pd.option_context("display.max_rows", None):
        print(merged_df)

    # Delete raw CSV data
    delete_CSVs()

    return merged_df


# function to delete CSVs once they've been parsed and merged
def delete_CSVs(dir_name=None):
    if dir_name is None:
        dir_name = "./data"

    dir_path = os.path.abspath(dir_name)

    if not os.path.exists(dir_path):
        raise ValueError("Directory containing CSVs does not exist")

    dir_contents = os.listdir(dir_path)

    for item in dir_contents:
        item_path = f"{dir_path}/{item}"

        if os.path.isdir(item_path):
            shutil.rmtree(item_path, ignore_errors=True)
            print(f"Directory {item_path} successfully deleted")

        if os.path.isfile(item_path):
            os.remove(item_path)
            print(f"File {item_path} successfully deleted")
