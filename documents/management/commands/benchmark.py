from django.core.management.base import BaseCommand, CommandError
import pandas as pd
from documents.search import search_documents

class Command(BaseCommand):
    help = "Run a query for a specific category and engines from an Excel file"

    def add_arguments(self, parser):
        parser.add_argument(
            "category_slug", type=str, help="Indicates the slug of the category"
        )
        parser.add_argument("excel_file", type=str, help="The path to the Excel file")
        parser.add_argument(
            "engines", nargs="+", type=str, help="List of engines to be used"
        )
        parser.add_argument(
            "--skip", type=int, default=0, help="Number of rows to skip from the start of the Excel file"
        )

    def handle(self, *args, **options):
        category_slug = options["category_slug"]
        excel_file = options["excel_file"]
        engines = options["engines"]
        skip_rows = options["skip"]

        self.stdout.write("Category ID: %s" % category_slug)
        self.stdout.write("Excel file: %s" % excel_file)
        self.stdout.write("Engines: %s" % ", ".join(engines))
        self.stdout.write("Skip: %d" % skip_rows)

        df = pd.read_excel(excel_file, skiprows=skip_rows)
        total_rows = len(df.index)

        # Iterate over each row in the DataFrame
        for index, row in df.iterrows():
            # Extract the second column
            query = row[1]
            for engine in engines:
                res = search_documents(
                    query, "", engine=engine, category_slug=category_slug
                )
                answer = res["result"]
                self.stdout.write(answer)

                # Add the result to a new column for this engine
                df.at[index, engine] = answer

            # Calculate and display the progress percentage
            progress = (index + 1) / total_rows * 100
            self.stdout.write("Progress: {:.2f}%".format(progress))
            # Write the DataFrame to a new Excel file
            df.to_excel("output.xlsx", index=False)

        # Write the DataFrame to a new Excel file
        df.to_excel("output.xlsx", index=False)
