
from src.ingestion import ingest_data
from src.validation import validate_all
from src.referential_validation import validate_referential_integrity
from src.transformation import transform_data
from src.mysql_loading import (
    load_mysql_data,
    show_mysql_table_counts
)


def test_mysql_loading():

    print("\nSTEP 1: INGESTING CSV DATA")
    source_data = ingest_data()

    print("\nSTEP 2: VALIDATING DATA")
    valid_data = validate_all(source_data)

    print("\nSTEP 3: CHECKING REFERENTIAL INTEGRITY")
    referential_data = validate_referential_integrity(valid_data)

    print("\nSTEP 4: TRANSFORMING DATA")
    transformed_data = transform_data(referential_data)

    print("\nTRANSFORMED RECORD COUNTS")

    for table_name, dataframe in transformed_data.items():
        print(f"{table_name}: {len(dataframe)}")

    print("\nSTEP 5: LOADING DATA INTO MYSQL")

    load_mysql_data(transformed_data)

    print("\nSTEP 6: VERIFYING MYSQL TABLE COUNTS")

    show_mysql_table_counts()

    print("\nMYSQL LOADING TEST COMPLETED")


if __name__ == "__main__":
    test_mysql_loading()
