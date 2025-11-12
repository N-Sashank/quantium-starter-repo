# data_processing.py
import pandas as pd
from pathlib import Path

# Path to the data folder
DATA_DIR = Path("data")

# Read and combine all CSVs in the folder
files = list(DATA_DIR.glob("*.csv"))
df_list = [pd.read_csv(f) for f in files]
df = pd.concat(df_list, ignore_index=True)

# --- 1. Keep only Pink Morsels ---
df = df[df["product"] == "pink morsel"]

# --- 2. Create Sales column (price × quantity) ---
df["Sales"] = df["price"] * df["quantity"]

# --- 3. Keep only Sales, Date, Region ---
output_df = df[["Sales", "date", "region"]].copy()
output_df.rename(columns={"date": "Date", "region": "Region"}, inplace=True)

# --- 4. Sort by Date (optional, for readability) ---
output_df.sort_values(by="Date", inplace=True)

# --- 5. Save processed data ---
OUTPUT_PATH = DATA_DIR / "processed_sales_data.csv"
output_df.to_csv(OUTPUT_PATH, index=False)

print(f"✅ Data processed successfully! Saved to: {OUTPUT_PATH}")
print(output_df.head())
