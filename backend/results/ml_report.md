# EventPulse AI - Machine Learning Model Results

Generated at: 2026-06-21 01:32:34

## 1. Event Duration Regressor (XGBRegressor)
Predicts the expected resolution time of the incident in minutes.

- **Mean Absolute Error (MAE)**: 71.55 minutes (CV: 64.84 +/- 4.99)
- **Root Mean Squared Error (RMSE)**: 114.01 minutes
- **Mean Absolute Percentage Error (MAPE)**: 123.86%
- **R^2 Score**: 0.6903

### Duration Feature Importances
| Feature | Importance |
| :--- | :--- |
| `event_type_encoded` | 0.4101 |
| `average_resolution_time` | 0.3415 |
| `precipitation` | 0.0616 |
| `is_raining` | 0.0450 |
| `is_rush_hour` | 0.0165 |
| `longitude` | 0.0140 |
| `priority_encoded` | 0.0138 |
| `corridor_encoded` | 0.0131 |
| `hour` | 0.0120 |
| `latitude` | 0.0118 |
| `estimated_attendance` | 0.0101 |
| `zone_encoded` | 0.0091 |
| `geohash` | 0.0089 |
| `day_of_week` | 0.0088 |
| `month` | 0.0073 |
| `junction_encoded` | 0.0057 |
| `requires_road_closure` | 0.0056 |
| `is_weekend` | 0.0051 |
| `temperature` | 0.0000 |
| `historical_event_frequency` | 0.0000 |

## 2. Congestion Impact Level Classifier (XGBClassifier)
Predicts the categorical severity rating (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).

- **Overall Accuracy**: 94.00% (CV: 95.95% +/- 1.11%)
- **Weighted Precision**: 0.9404
- **Weighted Recall**: 0.9400
- **Weighted F1 Score**: 0.9401

### Impact Feature Importances
| Feature | Importance |
| :--- | :--- |
| `priority_encoded` | 0.4873 |
| `corridor_encoded` | 0.1217 |
| `average_resolution_time` | 0.1133 |
| `requires_road_closure` | 0.0818 |
| `estimated_attendance` | 0.0401 |
| `event_type_encoded` | 0.0371 |
| `longitude` | 0.0273 |
| `zone_encoded` | 0.0240 |
| `hour` | 0.0113 |
| `day_of_week` | 0.0103 |
| `junction_encoded` | 0.0100 |
| `latitude` | 0.0089 |
| `month` | 0.0086 |
| `geohash` | 0.0073 |
| `is_rush_hour` | 0.0063 |
| `precipitation` | 0.0046 |
| `is_weekend` | 0.0000 |
| `temperature` | 0.0000 |
| `is_raining` | 0.0000 |
| `historical_event_frequency` | 0.0000 |

