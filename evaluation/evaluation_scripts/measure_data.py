import pandas as pd
import polars as pl
import os

DATA_PATH = 'evaluation/evaluation_results/adult/groupby.csv'

# Global Fallbacks
df_pandas = pd.read_csv(DATA_PATH) if os.path.exists(DATA_PATH) else pd.DataFrame()
df_polars = pl.read_csv(DATA_PATH) if os.path.exists(DATA_PATH) else pl.DataFrame()

def pandas_groupby(df=None): return df_pandas.groupby('education').mean(numeric_only=True)
def polars_groupby(df=None): return df_polars.group_by('education').mean() # Rust backend (RQ4)
def pandas_dropna(df=None): return df_pandas.dropna()
def polars_dropna(df=None): return df_polars.drop_nulls()