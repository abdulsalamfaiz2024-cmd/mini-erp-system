# Sales Module: Implementation Roadmap

## 1. Overview
This folder contains the page-by-page implementation plans for the Sales module. Every plan here is derived from the technical specifications in `/Documents/specs/`.

---

## 2. Page Plans
| Page Name | Plan Document | Status |
| :--- | :--- | :--- |
| **New Sales Order Form** | [new_sales_order_plan.md](new_sales_order_plan.md) | Ready |
| **Sales Order Details** | [sales_order_details_plan.md](sales_order_details_plan.md) | Ready |
| **Invoice Details** | (Pending) | TBD |
| **New Invoice Form** | (Pending) | TBD |

---

## 3. Shared Sales Logic
These plans share the `controllers/sales_controller.py` and `models/sales.py` logic. Any modification to one must be checked for side-effects on others.
