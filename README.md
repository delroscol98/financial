# Financial Tracker

## The Problem

Before I build this project my wife and I would manage our finances in a VERY slow way. We would:

1. Open the banking app
2. Look through each transaction in our debit accound and our credit account that was not already recorded
3. Categorise each transaction based off keywords or phrases in the description
4. Manually enter each description and transaction amount into a monthly spreadsheet under the respective category
5. Sum up the totals for each category
6. Manually enter the totals in a final yearly spreadsheet to see our income and expenses on a monthly/yearly basis

Call me lazy... but it's a lot of time spent for a little thing. So this program does this process automagically.

## The Solution

NOTE: The only manual thing that still needs to be done is downloading the CSVs and manually putting them in the `./data/` directory, after that just run `uv run main.py`

## How does this happen?

As stated above the CSVs from the debit and credit accound need to downloaded and put into the `./data/` directory

Everything after Step 1 happens by the program.

### Formatting

1. Each CSV is given a header row which are the label names of the CSV, then merged into a workable dataframe. NOTE: It's imperative that each CSV has similar column structure such as: "date", "amount", "description"
2. The dataframe is formatted throught the following process, then returned to be categorised
   - The `category` column is mutated to empty strings
   - The `description` column is mutated to uppercase strings
   - The `date` column is mutated to `datetime64` objects, which then mutates the `month` column to strings values of the approprate month
   - The dataframe is sorted according to the date column

### Categorisation

The categorisation algorithm rests on a `keywords` hashmap where each key is a `category` which points to a `list[]` of keywords and phrases

1. Create a `list[]` of categories from the `keywords` hashmap
2. Create a `list[]` of boolean masks which determine which rows receive their respective category
3. Handles edge cases through bitwise operations

### Updating

At this point the dataframe is categorised! Now we just need to send the data to the Google Sheet

1. Retrieve the whole Google spreadsheet
2. Create smaller dataframes based on the month category
3. For each month category create smaller dataframes based on category
4. Using the month to access the month sheet and the category to determine the correct column, build up the data into a `list[]`, then batch update the Google Sheet with the data - One API call per sheet

### Communication

Now the monthly spreadsheet is updated! All that is left to do is import values from the monthly spreadsheet into the yearly spreadsheet using the following formula for each row:

```
=IFERROR(
  CHOOSECOLS(
    IMPORTRANGE(
      "https://example.url.com"
      "SheetName!A2:Z2"
    ),
    1,3,5,7,9,11,13,15,17,19,21,23,25
  ),
  0
)
```

This formula does the following:

1. Imports the values from the monthly spreadsheet from the second row
2. Get every odd value (for my sheet odd or even doesn't matter) to insert in the yearly spreadsheet
3. If there are any errors the cell value is 0, otherwise the cell value is the imported value

### Cleanup

Once the sheets have been updated the program deletes the raw CSV files since they are not needed.

## About Google

As a tool primarily built for my own personal use, the Google Service Account is connected to my own Google account and thus only works for my own Sheets, Drive, Google platforms.

To learn more about Google Service Accounts go [here](https://cloud.google.com/iam/docs/service-account-overview)

## Future Development

In it's current state, the part that's still annoying is manually uploading CSVs, I want to find a solution to have the program automatically listen for transactions and update the Google sheet on the fly.

## Final Thoughts

This was my first ORIGINAL project that I built myself! So yeah... super proud. For the majority of the project I read... and read... and read a lot of documentation. I used a fair bit of ChatGPT to help me when dealing with the Google APIs and trying to make the Python code as fast as possible. But instead of just copying and pasting everything, I made a conscious effort to understand everything that was happening in my code.

I learned so much. Had so much fun. And have so many ideas for small personal projects that make my life easier!

Thanks for reading!
