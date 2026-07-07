import sys
import os
import looker_sdk
from looker_sdk import models40 as models


def main():
    # Check if looker.ini exists
    if not os.path.exists("looker.ini"):
        print("Error: looker.ini file not found.")
        print(
            "Please copy looker.ini.example to looker.ini and fill in your "
            "Looker"
            "API credentials.")
        sys.exit(1)

    print("Initializing Looker SDK...")
    # Initialize the SDK. By default, it looks for looker.ini in the current
    # directory.
    sdk = looker_sdk.init40()

    try:
        # 1. Verify authentication by getting current user info
        print("\nChecking authentication...")
        me = sdk.me()
        print(
            f"Successfully authenticated as: {me.first_name} {me.last_name} (ID: {me.id})")

        # 2. Run an inline query on the order_items explore
        print("\nRunning query on 'order_items' explore (Revenue by Month)...")

        # Define the query structure We fetch the created month and total
        # revenue, limiting to last 12 months
        query = models.WriteQuery(
            model="training_ecommerce",
            view="order_items",
            fields=["order_items.created_month", "order_items.total_revenue"],
            limit="12",
            sorts=["order_items.created_month desc"]
        )

        # Run the query. We request JSON output.
        result = sdk.run_inline_query(
            result_format="json",
            body=query
        )

        print("\nQuery Results:")
        print(result)

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print(
            "Please check your looker.ini configuration and ensure your "
            "Looker instance is accessible and the model/explore exists.")


if __name__ == "__main__":
    main()
