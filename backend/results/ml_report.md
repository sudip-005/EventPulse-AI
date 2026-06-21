# EventPulse AI - Machine Learning Model Results

Generated at: 2026-06-21 16:56:31

## 1. Event Duration Regressor (XGBRegressor)
Predicts the expected resolution time of the incident in minutes.

- **Mean Absolute Error (MAE)**: 71.83 minutes (CV: 65.38 +/- 4.81)
- **Root Mean Squared Error (RMSE)**: 113.71 minutes
- **Mean Absolute Percentage Error (MAPE)**: 124.10%
- **R^2 Score**: 0.6919

### Duration Feature Importances
| Feature | Importance |
| :--- | :--- |
| `event_type_encoded` | 0.3928 |
| `average_resolution_time` | 0.3316 |
| `is_raining` | 0.0662 |
| `precipitation` | 0.0505 |
| `is_rush_hour` | 0.0164 |
| `longitude` | 0.0140 |
| `hour` | 0.0121 |
| `latitude` | 0.0119 |
| `corridor_encoded` | 0.0117 |
| `priority_encoded` | 0.0117 |
| `estimated_attendance` | 0.0103 |
| `zone_incident_density` | 0.0091 |
| `geohash` | 0.0091 |
| `month` | 0.0085 |
| `is_weekend` | 0.0083 |
| `day_of_week` | 0.0082 |
| `zone_encoded` | 0.0081 |
| `junction_incident_density` | 0.0076 |
| `junction_encoded` | 0.0064 |
| `requires_road_closure` | 0.0055 |
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
| `zone_incident_density` | 0.0000 |
| `junction_incident_density` | 0.0000 |

