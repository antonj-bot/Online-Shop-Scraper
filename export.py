def export_to_excel(records, site, keyword):
    if not records:
        logger.warning("No records to export")
        return

    df = pd.DataFrame(records)

    # Sort safely (only if columns exist)
    sort_cols = []
    ascending = []

    if "reviews" in df.columns:
        sort_cols.append("reviews")
        ascending.append(False)

    if "price" in df.columns:
        sort_cols.append("price")
        ascending.append(True)

    if sort_cols:
        df = df.sort_values(by=sort_cols, ascending=ascending)

    filename = f"{site.lower()}_scrape_{keyword}.xlsx"

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Results")

        worksheet = writer.sheets["Results"]
        worksheet.auto_filter.ref = (
            f"A1:{chr(64 + len(df.columns))}{len(df) + 1}"
        )

        # Auto-adjust column widths
        for col in worksheet.columns:
            max_length = 0
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            worksheet.column_dimensions[col[0].column_letter].width = min(
                max_length + 2, 50
            )

    logger.info(f"Exported {len(records)} items to {filename}")
    print(f"✓ Saved to {filename}")