
from src.ingestion import ingest_data
from src.validation import validate_all


print("STARTING DATA INGESTION")

data = ingest_data()

print("\nSTARTING DATA VALIDATION")

valid_data = validate_all(data)

print("\nFINAL VALIDATION SUMMARY")

for name, df in valid_data.items():
    print(f"{name}: {len(df)} valid records")

print("\nINGESTION AND VALIDATION COMPLETED!")
