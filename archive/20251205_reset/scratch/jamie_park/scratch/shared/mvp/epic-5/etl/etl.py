# Minimal ETL skeleton for Epic-5

def run_etl(input_path: str, output_path: str):
    # TODO: implement ETL logic
    print(f"Running Epic-5 ETL from {input_path} to {output_path}")

if __name__ == '__main__':
    run_etl('data/input.csv', 'data/output.parquet')
