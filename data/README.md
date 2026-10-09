# Generated data

Generated using `zoro.data` for Week 1 of the Zorost AI Engineering Lab.

## Configuration

- Seed: `42`
- Requested shipments: `100,000`

## Dataset Files

| File | Rows |
|---|---:|
| `carriers.csv` | 20 |
| `lanes.csv` | 20 |
| `shipments.csv` | 100,200 |
| `support_tickets.csv` | 2,000 |

The generator adds duplicate shipment rows, so the actual shipment count is higher than requested.

## Schema

Column names for each CSV:

- **carriers:** `carrier_id`, `carrier_name`, `region`, `on_time_rate`, `base_rate_usd_per_km_ton`, `fleet_size`
- **lanes:** `lane_id`, `origin`, `destination`, `distance_km`, `avg_transit_days`, `toll_km`, `port_region`
- **shipments:** `shipment_id`, `carrier_id`, `lane_id`, `commodity`, `weight_kg`, `value_usd`, `planned_departure`, `planned_arrival`, `actual_arrival`, `delay_hours`, `is_on_time`, `status`, `weather_severity`
- **support_tickets:** `ticket_id`, `shipment_id`, `customer_id`, `category`, `priority`, `created_at`, `text`

## Data Quality Issues

Verified in the Week 1 notebook:

- Duplicate shipment rows: 200
- Missing shipment weights: 301
- Missing lane distances: 1

These issues will be explored in Week 2.

## Note on the Data Dictionary

The dataset includes `support_tickets.csv`, but its column definitions are not included in the original Week 1 `data-dictionary.md`. The original notebook and dictionary have been left unchanged.

See [`data-dictionary.md`](data-dictionary.md) for the available field definitions.