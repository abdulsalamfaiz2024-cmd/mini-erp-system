# Plan 2.3: Purchasing, Inventory & Returns (Exhaustive Detail)

## 1. Scope & Objective
This document outlines the logic for restocking the warehouse (Purchasing), managing physical movements (Inventory), and handling reversals (Returns).

---

## 2. Implementation Specifications

### 2.1. Purchasing Lifecycle (`pur_orders`)
- **Source**: `new_purchase_order_form_spec.md`, `purchase_order_list_spec.md`
- **Linkage**: On "Goods Receipt" (Confirming delivery), the system MUST increment `inv_products.stock_qty`.
- **Status Checks**: `Draft` -> `Sent` -> `Partial Receipt` -> `Fulfilled`.

### 2.2. Returns & Reversals (`ret_requests`)
- **Source**: `new_return_request_spec.md`, `return_details_spec.md`
- **Logic**:
    1. Verify `original_invoice_id` exists.
    2. Define `return_type`: `Refund`, `Replacement`, or `Store Credit`.
    3. Update `ret_items` table with "Inspection Notes" (e.g., Damaged vs Ready for Resale).

---

## 3. Inventory Control Logic (`controllers/inventory_manager.py`)
This module is the only one authorized to modify `stock_qty`.

| Action | Logic |
| :--- | :--- |
| **Sales Commitment** | Decrease `available_qty` but maintain `physical_qty`. |
| **Goods Receipt** | Increase `physical_qty` and `available_qty`. |
| **Stock Adjustment** | Manual override for shrinkage or damages (Requires ADMIN role). |

---

## 4. Key Functions & Locations
| Function Name | Location | Description |
| :--- | :--- | :--- |
| `receive_goods` | `controllers/inventory_controller.py` | Triggers on delivery confirmation. |
| `submit_return` | `controllers/returns_controller.py` | Validates against historical invoices. |
| `update_warehouse_loc`| `controllers/inventory_manager.py` | Tracks physical placement of items. |

---

## 5. Verification Steps
1. [ ] **Stock Reconciliation**: Verify that receiving 10 items in a PO accurately reflects in the Product List.
2. [ ] **Return Validity**: Attempt to return more items than were originally invoiced; verify rejection.
3. [ ] **Supplier History**: Verify that a supplier's detail view accurately shows all historical POs.
