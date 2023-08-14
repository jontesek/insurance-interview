from abc import ABC, abstractmethod

import structlog

from .errors import SearchUntilDatetimeEnd
from .models import Car


class CarsSaver(ABC):
    @abstractmethod
    def save_cars(self, cars: list[Car]):
        pass

    @abstractmethod
    def on_end(self):
        pass


class FileSaver(CarsSaver):
    def __init__(
        self, logger: structlog.stdlib.BoundLogger, cars_file_path: str
    ) -> None:
        self.log = logger.bind(logger_name="file_saver")
        self._cars_file_path = cars_file_path

    def save_cars(self, cars: list[Car]) -> None:
        self.log.info(
            "save_cars.start", cars_file_path=self._cars_file_path, cars_count=len(cars)
        )
        with open(self._cars_file_path, "a+") as file_obj:
            for car in cars:
                file_obj.write(car.json(ensure_ascii=False) + "\n")
        self.log.info("save_cars.end")

    def on_end(self):
        pass


class DbSaver(CarsSaver):
    """Does not work - DB connection not implemented/tested"""

    INSERT_SQL = "INSERT INTO cars VALUES(%s)"

    def __init__(
        self, logger: structlog.stdlib.BoundLogger, db_connection_string: str
    ) -> None:
        self.log = logger.bind(logger_name="db_saver")
        self.db_connection = None  # psycopg2.connect(db_connection_string)

    def save_cars(self, cars: list[Car]) -> None:
        self.log.info("save_cars.start", db=True, cars_count=len(cars))
        # cursor = self.db_connection.cursor()
        # cur.executemany(self.INSERT_SQL, cars)
        # cursor.close()

    def on_end(self):
        print("ending")
        return
        # self.db_connection.commit()
        # self.db_connection.close()


if __name__ == "__main__":
    pass
