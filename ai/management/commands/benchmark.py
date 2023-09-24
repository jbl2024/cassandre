# pylint: disable=broad-except
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from django.core.management.base import BaseCommand

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
        parser.add_argument(
            "--max-tasks",
            type=int,
            default=10,
            help="Maximum number of parallel tasks",
        )

    def handle_row(self, index, row, engines, category_slug):
        """
        Handles a single row from the Excel file.

        Args:
            index (int): The index of the row in the Excel file.
            row (pd.Series): The row data from the Excel file.
            engines (list): The list of engines to be used.
            category_slug (str): The slug of the category.

        Returns:
            tuple: The index of the row and the results from the search.
        """
        results = {}
        query = row[1]
        for engine in engines:
            try:
                res = search_documents(
                    query, engine=engine, category_slug=category_slug
                )
                answer = res["result"]
                results[engine] = answer
            except Exception as err:
                # Handle specific exceptions as needed or just log the error
                self.stdout.write(
                    f"Error processing index {index} with engine {engine}: {err}"
                )
                results[engine] = "Error"
        return index, results

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

        with ThreadPoolExecutor(max_workers=options["max_tasks"]) as executor:
            futures = [
                executor.submit(self.handle_row, index, row, engines, category_slug)
                for index, row in data_frame.iterrows()
            ]

            for future in futures:
                try:
                    index, results = future.result()
                    for engine, answer in results.items():
                        data_frame.at[index, engine] = answer

                    # Calculate and display the progress percentage
                    progress = (index + 1) / total_rows * 100
                    self.stdout.write(f"Progress: {progress:.2f}% ({index + 1}/{total_rows})")
                except Exception as err:
                    # Save partial results to avoid losing data
                    data_frame.to_excel("output_partial.xlsx", index=False)
                    self.stdout.write(
                        f"Error processing index {index}. Saved partial results to "
                        f"'output_partial.xlsx'. Error: {err}"
                    )

        # Write the DataFrame to a new Excel file once after all tasks have completed
        data_frame.to_excel("output.xlsx", index=False)
