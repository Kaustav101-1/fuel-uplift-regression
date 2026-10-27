# -*- coding: utf-8 -*-
"""
Generate SYNTHETIC sample data so the model can be run without real records.

All numbers are invented. The pattern is deliberately simple: each aircraft type has a
typical uplift, some routes need more fuel, and when fuel is cheaper at the departure
station than at the destination, more fuel is uplifted ("tankering").

Run:
    python make_sample_data.py
Creates data/training.xlsx, data/validation.xlsx and data/test.xlsx (70/15/15 split).
"""

from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
N_FLIGHTS = 1200

AIRCRAFT = {           # code: (typical uplift in litres, turboprop?)
    "320": (6500, "No"),
    "321": (8000, "No"),
    "738": (6800, "No"),
    "AT7": (1800, "Yes"),
    "DH8": (2200, "Yes"),
}
DESTINATIONS = {       # destination: extra litres for a longer sector
    "DEL": 1500, "BOM": 1800, "CCU": 300, "GAU": 0, "BLR": 2500, "HYD": 2000,
}
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def make_flights(n):
    aircraft = RNG.choice(list(AIRCRAFT), n)
    dest = RNG.choice(list(DESTINATIONS), n)
    day = RNG.choice(WEEKDAYS, n)
    from_price = RNG.normal(92000, 4000, n).round()
    to_price = RNG.normal(90000, 5000, n).round()

    base = np.array([AIRCRAFT[a][0] for a in aircraft])
    sector = np.array([DESTINATIONS[d] for d in dest])
    turboprop = np.array([AIRCRAFT[a][1] for a in aircraft])
    sector = np.where(turboprop == "Yes", sector * 0.25, sector)

    # Tankering: each Rs 1,000/KL cheaper at departure -> ~120 extra litres (jets only)
    tanker = np.where(turboprop == "No", (to_price - from_price) / 1000 * 120, 0)
    weekend = np.isin(day, ["Friday", "Sunday"]) * 300   # busier, heavier flights

    uplift = base + sector + tanker + weekend + RNG.normal(0, 600, n)
    uplift = np.clip(uplift, 300, None).round()

    return pd.DataFrame({
        "Day of Week": day,
        "Aircraft": aircraft,
        "Turboprop": turboprop,
        "To IATA": dest,
        "From Landed Price (Rs/KL)": from_price,
        "To Landed Price (Rs/KL)": to_price,
        "Qty Uplifted (L)": uplift,
    })


def main():
    out = Path(__file__).resolve().parent / "data"
    out.mkdir(exist_ok=True)
    df = make_flights(N_FLIGHTS).sample(frac=1, random_state=42).reset_index(drop=True)
    n_train, n_val = int(0.70 * len(df)), int(0.15 * len(df))
    parts = {
        "training": df.iloc[:n_train],
        "validation": df.iloc[n_train:n_train + n_val],
        "test": df.iloc[n_train + n_val:],
    }
    for name, part in parts.items():
        part.to_excel(out / f"{name}.xlsx", index=False)
        print(f"{name}.xlsx: {len(part)} synthetic flights")


if __name__ == "__main__":
    main()
