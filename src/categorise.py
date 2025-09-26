import re

import numpy as np

from src.constants import amt_col, cat_col, desc_col, keywords


def categorise(dataframe):
    # Holds the categories, choices[i] is the category assigned to conditions[i]
    categories = list(keywords.keys())

    # Will hold boolean masks determine which row will recieve their category
    conditions = []

    # Loop through the keywords dict and grabs the values (list of keywords)
    for words in list(keywords.values()):
        # Create a regex pattern from each list of values
        pattern = "|".join(map(re.escape, words))

        # Create a mask based on the regex pattern and append the mask to the list -> rows that have TRUE receive the category
        conditions.append(dataframe[desc_col].str.contains(pattern))

    # Inserts the respective category in the approprate cell based off conditions and choices
    dataframe[cat_col] = np.select(conditions, categories, default="MISC")

    # Edge case: COSTCO and amount < 30
    # Edge case: IKEA and amount < 50
    mask = (
        (dataframe[desc_col].str.contains("COSTCO")) & (dataframe[amt_col] < 30)
    ) | ((dataframe[desc_col].str.contains("IKEA")) & (dataframe[amt_col] < 50))
    dataframe.loc[mask, cat_col] = "TAKEAWAY"

    # Edge case: COUNRTY ROAD and amount < 50
    # Edge case: CR ROUSE HILL and amount < 50
    mask = (
        (dataframe[desc_col].str.contains("COUNTRY ROAD"))
        | (dataframe[desc_col].str.contains("CR ROUSE HILL"))
    ) & (dataframe[amt_col] < 50)
    dataframe.loc[mask, cat_col] = "CHILDREN"

    # Edge case: APPLE.COM and amount = 4.49
    # Edge case: APPLE.COM and amount != 4.49
    mask = dataframe[desc_col].str.contains("APPLE.COM")
    dataframe.loc[mask & (dataframe[amt_col] == 4.49), cat_col] = "PHONE"
    dataframe.loc[mask & (dataframe[amt_col] != 4.49), cat_col] = "MISC"

    # Edge case: Op shop
    mask = dataframe[desc_col].str.contains("LIFELINEWESTERNSYDNEY")
    dataframe.loc[mask, cat_col] = "CHILDREN"

    # Edge case: CAR and amount < 30
    mask = (dataframe[cat_col] == "CAR") & (dataframe[amt_col] < 30)
    dataframe.loc[mask, cat_col] = "TAKEAWAY"

    # Edge case: Father's Day
    mask = dataframe[desc_col].str.contains("FATHERS DAY")
    dataframe.loc[mask, cat_col] = "MISC"

    # Edge case: Bank transfers
    mask = (
        dataframe[desc_col].str.contains("3622")
        | dataframe[desc_col].str.contains("2798")
        | dataframe[desc_col].str.contains("PAYMENT RECEIVED")
    )
    dataframe.loc[mask, cat_col] = ""

    # Edge case: Rent
    mask = dataframe[desc_col].str.contains("ATM") & (
        (dataframe[amt_col] == 1800)
        | (dataframe[amt_col] == 1850)
        | (dataframe[amt_col] == 1600)
        | (dataframe[amt_col] == 50)
    )
    dataframe.loc[mask, cat_col] = "RENT"

    dataframe[cat_col] = dataframe["category"].replace("nan", "MISC")
    dataframe = dataframe[dataframe[cat_col] != ""]

    return dataframe
