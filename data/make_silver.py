
import pathlib
import sys
import pandas as pd


def load_or_generate():
    repo = pathlib.Path(__file__).resolve().parent.parent
    while not (repo / "zoro").is_dir() and repo != repo.parent:
        repo = repo.parent

    sys.path.insert(0, str(repo))
    from zoro import data

    path = repo / "data" / "shipments.csv"
    if path.exists():
        raw = pd.read_csv(path, parse_dates=[
            "planned_departure", "planned_arrival", "actual_arrival"
        ])
        lanes = pd.read_csv(repo / "data" / "lanes.csv")
        carriers = pd.read_csv(repo / "data" / "carriers.csv")
    else:
        raw = data.shipments(100_000, seed=42)
        lanes = data.lanes(20, seed=11)
        carriers = data.carriers(20, seed=7)

    return raw, lanes, carriers, repo


def clean(df, lanes):
    before = len(df)
    weight_nans = int(df["weight_kg"].isna().sum())
    distance_nans = int(lanes["distance_km"].isna().sum())

    ships = df.drop_duplicates().copy()
    duplicates = before - len(ships)

    ships["weight_kg"] = ships["weight_kg"].fillna(
        ships.groupby("commodity")["weight_kg"].transform("median")
    )
    lanes = lanes.copy()
    lanes["distance_km"] = lanes["distance_km"].fillna(
        lanes["distance_km"].median()
    )

    bad_weights = int((ships["weight_kg"] <= 0).sum())
    ships = ships[ships["weight_kg"] > 0].reset_index(drop=True)

    bad_transit = int(
        (ships["planned_arrival"] <= ships["planned_departure"]).sum()
    )
    ships = ships[
        ships["planned_arrival"] > ships["planned_departure"]
    ].reset_index(drop=True)

    mask = (
        (ships["status"] == "In Transit")
        & ships["actual_arrival"].notna()
    )
    status_fixed = int(mask.sum())
    ships.loc[mask, "status"] = "Delivered"

    metrics = {
        "input_rows": before,
        "duplicates_removed": duplicates,
        "weight_nans_imputed": weight_nans,
        "distance_nans_imputed": distance_nans,
        "bad_weights_dropped": bad_weights,
        "bad_transit_dropped": bad_transit,
        "status_mismatches_fixed": status_fixed,
    }
    return ships, lanes, metrics


def validate(df, lanes, carriers):
    checks = [
        df.duplicated().sum() == 0,
        df["weight_kg"].isna().sum() == 0,
        (df["weight_kg"] > 0).all(),
        df["delay_hours"].isna().sum() == 0,
        df["is_on_time"].isna().sum() == 0,
        (df["value_usd"] >= 0).all(),
        df["carrier_id"].isin(carriers["carrier_id"]).all(),
        df["lane_id"].isin(lanes["lane_id"]).all(),
        set(df["is_on_time"].unique()) <= {True, False},
        df["delay_hours"].between(-48, 240).all(),
        (df["planned_arrival"] > df["planned_departure"]).all(),
        lanes["distance_km"].isna().sum() == 0,
    ]

    for i, passed in enumerate(checks, 1):
        print(f"{'PASS' if passed else 'FAIL'} Check {i}")

    count = sum(checks)
    print(f"CHECKS_PASSED: {count} of {len(checks)}")
    return all(checks)


def main():
    raw, lanes, carriers, repo = load_or_generate()
    ships, lanes, metrics = clean(raw, lanes)

    if not validate(ships, lanes, carriers):
        raise SystemExit("Validation failed; outputs not saved.")

    out = repo / "data" / "silver_pipeline"
    out.mkdir(parents=True, exist_ok=True)

    ships.to_csv(out / "shipments_silver.csv", index=False)
    lanes.to_csv(out / "lanes_silver.csv", index=False)
    carriers.to_csv(out / "carriers_silver.csv", index=False)

    report = [
        "# Silver Pipeline - Cleaning Report",
        "",
        f"- Input rows: {metrics['input_rows']:,}",
        f"- Duplicates removed: {metrics['duplicates_removed']:,}",
        f"- Weight NaNs imputed: {metrics['weight_nans_imputed']:,}",
        f"- Distance NaNs imputed: {metrics['distance_nans_imputed']:,}",
        f"- Non-positive weights dropped: {metrics['bad_weights_dropped']:,}",
        f"- Bad transit rows dropped: {metrics['bad_transit_dropped']:,}",
        f"- Status mismatches fixed: {metrics['status_mismatches_fixed']:,}",
        f"- Output rows: {len(ships):,}",
        "",
        "## Validation",
        "",
        "- Checks passed: 12 of 12",
    ]
    (out / "validation-report.md").write_text(
        "\n".join(report) + "\n", encoding="utf-8"
    )

    print("SILVER_ROW_COUNT:", len(ships))


if __name__ == "__main__":
    main()