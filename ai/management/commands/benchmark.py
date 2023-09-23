from django.core.management.base import BaseCommand
import pandas as pd
from ai.services.search_service import search_documents


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
            "--skip",
            type=int,
            default=0,
            help="Number of rows to skip from the start of the Excel file",
        )

    def handle(self, *args, **options):
        category_slug = options["category_slug"]
        excel_file = options["excel_file"]
        engines = options["engines"]
        skip_rows = options["skip"]

        self.stdout.write(f"Category ID: {category_slug}")
        self.stdout.write(f"Excel file: {excel_file}")
        self.stdout.write(f"Engines: {', '.join(engines)}")
        self.stdout.write(f"Skip: {skip_rows}")

        data_frame = pd.read_excel(excel_file, skiprows=skip_rows)
        total_rows = len(data_frame.index)

        # Iterate over each row in the DataFrame
        for index, row in data_frame.iterrows():
            # Extract the second column
            query = row[1]
            for engine in engines:
                res = search_documents(
                    query, engine=engine, category_slug=category_slug
                )
                answer = res["result"]
                self.stdout.write(answer)

                # Add the result to a new column for this engine
                data_frame.at[index, engine] = answer

            # Calculate and display the progress percentage
            progress = (index + 1) / total_rows * 100
            self.stdout.write(f"Progress: {progress:.2f}%")
            # Write the DataFrame to a new Excel file
            data_frame.to_excel("output.xlsx", index=False)

        # Write the DataFrame to a new Excel file
        data_frame.to_excel("output.xlsx", index=False)