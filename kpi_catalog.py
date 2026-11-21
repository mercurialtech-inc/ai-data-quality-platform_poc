
# kpi_catalog.py

# Synthetic KPI definitions
kpi_metadata = {
    "KPI_REVENUE_001": {
        "name": "Transaction Revenue",
        "definition": "Sum of transaction amounts for completed transactions",
        "formula": "SUM(amount)",
        "source_table": "revenue.transactions",
        "source_column": "amount",
        "source_grain": "One row per transaction",
        "kpi_grain": "One row per business location per day"
    }
}


# Synthetic table and column metadata
table_metadata = {
    "revenue.transactions": {
        "transaction_id": {
            "data_type": "string",
            "nullable": "no"
        },
        "location_id": {
            "data_type": "string",
            "nullable": "no"
        },
        "transaction_date": {
            "data_type": "date",
            "nullable": "no"
        },
        "amount": {
            "data_type": "float",
            "nullable": "no"
        },
        "transaction_status": {
            "data_type": "string",
            "nullable": "no"
        }
    }
}


def get_kpi_metadata(kpi_id: str) -> tuple[dict, dict, dict]:
    """
    Retrieve KPI metadata, source-table column metadata,
    and the primary KPI measure-column metadata.

    Raises:
        KeyError: If the KPI, source table, or measure column
                  is missing from the synthetic catalog.
    """

    kpi_meta = kpi_metadata[kpi_id]

    source_table = kpi_meta["source_table"]
    source_column = kpi_meta["source_column"]

    all_column_meta = table_metadata[source_table]
    kpi_column_meta = all_column_meta[source_column]

    return kpi_meta, all_column_meta, kpi_column_meta


if __name__ == "__main__":

    # Successful lookup
    try:
        kpi_meta, all_column_meta, kpi_column_meta = (
            get_kpi_metadata("KPI_REVENUE_001")
        )

        print("KPI metadata:", kpi_meta)
        print("All column metadata:", all_column_meta)
        print("KPI column metadata:", kpi_column_meta)

    except KeyError as e:
        print(f"Metadata lookup failed: {e}")

    # Negative test: unknown KPI
    try:
        get_kpi_metadata("KPI_UNKNOWN")

    except KeyError as e:
        print(f"Expected lookup failure: {e}")
