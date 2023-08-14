# Task 2

## Installation

Project is for now run locally without Docker. You must have Python 3.11 installed. It uses [Poetry](https://python-poetry.org/) for package management.

1. `curl -sSL https://install.python-poetry.org | python3`
2. `cd task_2`
3. `poetry install`

## Usage

Two scripts located in `car_scraper/cli` directory. You must be in `task_2` directory to run it using example commands.

### Check.py
Uses `GreatExpectations` to perform some data checks. Unfortunately I didn't manage to integrate motors check into Expecation report. The library is quite confusing, it needs more research.

You can also run motors check by file `car_scraper/cars_checker.py` which works well.

Run like this: `poetry run python -m car_scraper.cli.check <absolute_path_to_car_file>`

### Scrape.py
Downloads cars from SAuto. It saves data to local JSONL file. It's prepared to save data also to DB, but the code doesn't work. 

While downloading, it performs some basic checking of the input data - uses Pydantic model in `car_scraper/models.py`. Also `cars_provider.py` has `_validate_car_result` method. I noticed some cases when information about `gearbox_type` is missing - in that case the car is skipped. 

Run like this: 
```
poetry run python -m car_scraper.cli.scrape --manufacturer <manufacturer> --dir_path <absolute path to directory where file will be saved> --search_until <datetime how far in history to go>
```

Example: 
```
poetry run python -m car_scraper.cli.scrape --manufacturer skoda --dir_path ~/task_2/data --search_until 2023-08-13T11:19:16
```
