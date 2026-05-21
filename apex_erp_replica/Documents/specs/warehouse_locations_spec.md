# Page Specification: Warehouse Locations

## 1. Overview
The Warehouse Locations page displays all warehouse locations and their bin/zone structures. It allows users to view stock by location and manage warehouse configurations.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Search Input** | `q` (query string) | `GET /api/v1/warehouses?q={query}` | `GET` |
| **Warehouses Table** | `warehouses[]` | `GET /api/v1/warehouses` | `GET` |
| **Add Warehouse Button** | N/A | Opens modal/form | N/A |
| **View Zones Action** | `warehouse_id` | `GET /api/v1/warehouses/{id}/zones` | `GET` |
| **Edit Action** | `warehouse_id` | Opens edit modal | N/A |

## 3. Data Structure (API Contracts)

### A. Warehouses List (`GET /api/v1/warehouses`)
**Response:**
```json
{
  "warehouses": [
    {
      "warehouse_id": "WH-001",
      "name": "Main Warehouse",
      "address": "123 Industrial Blvd, Suite 100",
      "city": "New York",
      "country": "USA",
      "total_zones": 5,
      "total_bins": 120,
      "stock_value": 850000.00,
      "utilization": 78,
      "status": "Active"
    },
    {
      "warehouse_id": "WH-002",
      "name": "Warehouse B",
      "address": "456 Commerce Dr",
      "city": "Los Angeles",
      "country": "USA",
      "total_zones": 3,
      "total_bins": 80,
      "stock_value": 320000.00,
      "utilization": 45,
      "status": "Active"
    },
    {
      "warehouse_id": "WH-003",
      "name": "Warehouse C",
      "address": "789 Storage Lane",
      "city": "Chicago",
      "country": "USA",
      "total_zones": 2,
      "total_bins": 40,
      "stock_value": 85000.00,
      "utilization": 92,
      "status": "Active"
    }
  ]
}
```

### B. Warehouse Zones (`GET /api/v1/warehouses/{id}/zones`)
```json
{
  "warehouse_id": "WH-001",
  "zones": [
    { "zone_id": "Z-A", "name": "Zone A - Electronics", "bins": 30, "utilization": 85 },
    { "zone_id": "Z-B", "name": "Zone B - Office Supplies", "bins": 25, "utilization": 60 },
    { "zone_id": "Z-C", "name": "Zone C - Furniture", "bins": 20, "utilization": 90 }
  ]
}
```

### C. Add/Update Warehouse (`POST /api/v1/warehouses` or `PATCH /api/v1/warehouses/{id}`)
**Request:**
```json
{
  "name": "New Warehouse",
  "address": "100 New Street",
  "city": "Miami",
  "country": "USA",
  "status": "Active"
}
```

## 4. Logical Actions
- **Search**: Filters warehouses by name or location.
- **Utilization Bar**: Visual progress bar showing capacity usage.
  - Green: < 70%
  - Yellow: 70-85%
  - Red: > 85%
- **View Zones**: Expands row or navigates to zone detail view.
- **Add Warehouse**: Opens modal form to create new warehouse.
- **Edit**: Opens modal form to modify warehouse details.

## 5. Integration Notes
- Linked from Inventory Dashboard sidebar as "Warehouse Locations".
- Uses card/table components from `main.css`.
