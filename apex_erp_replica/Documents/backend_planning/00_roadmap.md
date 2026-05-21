# Apex ERP Backend: Master Roadmap

## 1. Project Project Status
- **Phase 0: Frontend Design**: 90% Complete (Static HTML & Unified Sidebar).
- **Phase 1: Foundation & Security**: **Current Focus**
- **Phase 2: Core ERP Modules**: Not Started
- **Phase 3: Integration & Global Logic**: Not Started

---

## 2. Planning Structure (`/Documents/backend_planning/`)
This folder contains the blueprints for every stage of the backend development. Every single page (30 total) is now planned individually for maximum precision.
1. `00_roadmap.md`: You are here. The master index of the project.
2. `phase_1_foundation/_index.md`: Master index for Infrastructure, Security, and Core DB Logic.
3. `phase_2_modules/`: (Directory) Contains 1 roadmap per functional page:
    - `01_sales/_index.md` (Orders, Invoices)
    - `02_finance/_index.md` (Ledger, Expenses)
    - `03_inventory/_index.md` (Stock, Warehouse)
    - `04_purchasing/_index.md` (PO, Suppliers)
    - `05_returns/_index.md` (Logistics, Credit)
    - `06_common/_index.md` (Customers, Dashboard)
4. `phase_3_integration/_index.md`: Master index for Frontend-to-Backend data binding.

---

## 3. Execution Logging (`/Documents/backend_execution_logs/`)
For every step completed, a document will be created here describing:
- What was done.
- Which files were modified/created.
- Function definitions and Key mappings.
- Linkages between Frontend and Backend.

---

## 4. Current Stage: Phase 1 (Foundation)
**Objective**: Build the "Brain and Shell" of the application.
- **Target Files**: `Backend/main.py`, `Backend/core/db.py`, `Backend/api/auth.py`.
- **Status**: Planning.

---

## 5. Master Page Index
*Reference for all functional documents as of Jan 01, 2026.*
- Dashboard
- Sales Order Details / New Sales Order
- Invoice Details / New Invoice
- Returns (Dashboard, List, Details, Request, Inspection, Credit)
- Purchasing (Dashboard, List, Details, New PO, Suppliers, Supplier Details)
- Inventory (Dashboard, List, Details, Adjustment, Goods Receipt, Warehouse)
- Finance (Dashboard, Expenses, New Expense, Reports, Ledger, Journals)
- Customers
