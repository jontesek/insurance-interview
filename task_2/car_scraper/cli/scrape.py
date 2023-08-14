# You can use this script to save cars.
import argparse
import datetime
import os

from ..models import DATE_FORMAT, DATETIME_FORMAT
from ..service import Service

DEFAULT_SEARCH_HOURS = 24


def setup_service() -> Service:
    is_debug = bool(os.environ.get("DEBUG", 1))
    service = Service(is_debug=is_debug)
    return service


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dir_path",
        help="Save data to file in this directory (use absolute path)",
        type=str,
    )
    parser.add_argument("--file_name", help="Optional file name", type=str)
    parser.add_argument("--db_conn", help="Save data to this database", type=str)
    parser.add_argument(
        "--manufacturer", help="Car manufacturer which to save the data for.", type=str
    )
    parser.add_argument(
        "--search_until",
        help="Date or datetime for the earliest car advert to save.",
        type=str,
    )

    args = parser.parse_args()

    # Check arguments
    if not args.manufacturer:
        exit("You must provide manufacturer.")

    if not args.dir_path and not args.db_conn:
        exit("You must provider either dir_path or db_connn.")

    if args.dir_path and not os.path.exists(args.dir_path):
        exit("dir_path does not exist")

    if search_until := args.search_until:
        try:
            search_until = datetime.datetime.strptime(search_until, DATETIME_FORMAT)
        except ValueError:
            try:
                search_until = datetime.datetime.strptime(search_until, DATE_FORMAT)
            except ValueError:
                exit("search_until must be in format %Y-%m-%d or %Y-%m-%dT%H:%M:%S")
    else:
        search_until = datetime.datetime.now() - datetime.timedelta(
            hours=DEFAULT_SEARCH_HOURS
        )
        print(
            f"You didn't provide default search_until settings, using default: {str(search_until)}"
        )

    # Run scraper
    service = setup_service()
    if args.dir_path:
        service.save_cars_to_file(
            args.manufacturer, search_until, args.dir_path, args.file_name
        )
    if args.db_conn:
        service.save_cars_to_db(args.manufacturer, search_until, args.db_conn)


if __name__ == "__main__":
    main()
