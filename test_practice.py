import pandas as pd

customers = pd.DataFrame({
    "customer_id": [101, 102, 103, 104, 105, 106],
    "country": ["India", "Brazil", "India",
                "Canada", "Brazil", "India"]
})

campaigns = pd.DataFrame({
    "customer_id": [101, 102, 103, 105, 106],
    "converted": [1, 0, 1, 1, 0]
})

df = customers.merge(
    right=campaigns,
    how="left",
)

df = df.dropna(subset="converted")

result = (
    df.groupby("country")["converted"]
    .agg(
        total_campaign_records="count",
        successful_conversions="sum",
    )
    .reset_index()
)

print(result)