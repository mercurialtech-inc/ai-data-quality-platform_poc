from kpi_catalog import get_kpi_metadata

def build_recommendation_context(kpi_id: str, business_context: str | None = None) -> dict:
    
    kpi_meta, all_column_meta, kpi_column_meta = get_kpi_metadata(kpi_id)
    
    return {
    "kpi": kpi_meta,
    "columns": all_column_meta,
    "business_context": business_context
    }

if __name__ == "__main__":
    context = build_recommendation_context(
        "KPI_REVENUE_001",
        "Refund amounts may be negative."
    )

    print(context)