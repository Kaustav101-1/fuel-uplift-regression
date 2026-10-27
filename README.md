# Predicting Aviation Fuel Uplift with Linear Regression

How much fuel will a flight take on at a station? This project predicts the **fuel uplift per flight (litres)** from the day of the week, aircraft type, destination and the **landed price of jet fuel** at the departure and destination airports.

Price matters because airlines often **tanker** fuel: when fuel is cheaper at the departure station than at the destination, they uplift extra to avoid buying expensive fuel later. A supplier that can forecast uplift can plan stock, staffing and bowser allocation, and anticipate demand shifts when prices change.

## Approach

| Step | What | Why |
|---|---|---|
| Inputs | Day of week, aircraft, turboprop (Yes/No), destination, departure and destination landed price (Rs/KL) | The operational and commercial drivers of uplift |
| Cleaning | Standardises text (e.g. `320.0` → `320`), checks weekday and Yes/No values, treats invalid prices as missing | Excel exports are messy; bad inputs fail loudly instead of silently |
| Encoding | One-hot encoding for categories; median imputation + scaling for prices | Turns mixed data into numbers a regression can use |
| Model | Linear regression inside a scikit-learn `Pipeline` | Simple, fast and **explainable**: each coefficient is "litres per unit change" |
| Validation | Separate training / validation / test files; test used only with `--evaluate-test` | Prevents tuning on the test set, so the final score is honest |
| Benchmark | Compared against always predicting the training average | Shows how much the model actually adds |

All preprocessing is fitted on the training data only and saved together with the model, so new flights are processed exactly the same way.

## Example run (synthetic data)

The real flight data is not included. `make_sample_data.py` generates **synthetic** flights with a similar structure:

```
Validation performance          Test performance
MAE:  664.9 L                   MAE:  635.6 L
RMSE: 825.2 L                   RMSE: 814.4 L
R²:   0.930                     R²:   0.930
Benchmark MAE: 2,887.9 L        Benchmark MAE: 2,812.4 L
```

On this sample, the model's average error is about **4.5x smaller** than the naive benchmark. These figures describe the synthetic data only.

## How to run

```bash
pip install -r requirements.txt
python make_sample_data.py              # creates data/training.xlsx, validation.xlsx, test.xlsx
python fuel_uplift_linear.py            # train + validate
python fuel_uplift_linear.py --evaluate-test   # final test, once the model is settled
```

Outputs (in `outputs/`): per-flight predictions with errors, `evaluation_metrics.csv`, and the saved model (`linear_fuel_uplift_model.joblib`).

To use your own data, place three Excel files in `data/` with these columns (others are ignored):
`Day of Week`, `Aircraft`, `Turboprop`, `To IATA`, `From Landed Price (Rs/KL)`, `To Landed Price (Rs/KL)`, `Qty Uplifted (L)`.

## Limitations and next steps

- A linear model assumes each factor adds a fixed amount. Real tankering behaviour depends on aircraft *and* price gap together. Interaction terms or tree-based models (random forest, gradient boosting) could capture that.
- Destinations or aircraft not seen in training are flagged, and treated the same as the baseline category.
- Useful next features: sector distance, payload or load factor, and the departure–destination price *difference* as an explicit input.

## Tech

Python · pandas · scikit-learn · joblib
