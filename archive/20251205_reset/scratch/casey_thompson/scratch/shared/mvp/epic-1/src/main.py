import pandas as pd

def run():
    # minimal CSV ingestion placeholder
    df = pd.DataFrame({'id':[1,2,3], 'value':[10,20,30]})
    print(df.head())

if __name__ == '__main__':
    run()
