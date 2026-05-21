# Page Specification: Journal Entries

## 1. Overview
The Journal Entries page lists all double-entry accounting transactions. Users can view, create, and audit entries to ensure the books remain balanced.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Total Debits (MTD)** | `total_debits` | `GET /api/v1/finance/ledger/journals/summary` | `GET` |
| **Total Credits (MTD)** | `total_credits` | `GET /api/v1/finance/ledger/journals/summary` | `GET` |
| **Unposted Entries Count** | `unposted_count` | `GET /api/v1/finance/ledger/journals/summary` | `GET` |
| **Search Journals** | `q` | `GET /api/v1/finance/ledger/journals?q={query}` | `GET` |
| **Month/Year Filter** | `month`, `year` | `GET /api/v1/finance/ledger/journals` | `GET` |
| **Journal Table** | `journals[]` | `GET /api/v1/finance/ledger/journals` | `GET` |
| **New Entry Button** | N/A | Navigation link | N/A |
| **Status Badge** | `status` | `GET /api/v1/finance/ledger/journals` | `GET` |

## 3. Data Structure (API Contracts)

### A. Journals List (`GET /api/v1/finance/ledger/journals`)
**Response:**
```json
{
  "journals": [
    {
      "date": "2023-10-24",
      "ref_id": "JE-10045",
      "description": "Office Supplies Purchase",
      "lines": [
        { "account": "6020 - Supplies", "debit": 450.00, "credit": 0.00 },
        { "account": "1010 - Cash", "debit": 0.00, "credit": 450.00 }
      ],
      "status": "Posted",
      "total_debit": 450.00,
      "total_credit": 450.00
    },
    {
      "date": "2023-10-23",
      "ref_id": "JE-10046",
      "description": "Monthly Rent Adjustment",
      "lines": [
        { "account": "6300 - Rent Exp", "debit": 2500.00, "credit": 0.00 },
        { "account": "2100 - Acc. Pay.", "debit": 0.00, "credit": 2500.00 }
      ],
      "status": "Draft",
      "total_debit": 2500.00,
      "total_credit": 2500.00
    }
  ],
  "pagination": { "current": 1, "total": 248 }
}
```

### B. Post Journal (`POST /api/v1/finance/ledger/journals/{id}/post`)
**Response:**
```json
{
  "success": true,
  "message": "Journal Entry JE-10046 posted successfully"
}
```

## 4. Logical Actions
- **New Entry**: Navigates to a form (conceptualized as `new_journal_form.html`) to add a double-entry transaction.
- **Filter**: Users can filter by period or use specific keywords (Reference ID, Description).
- **Audit**: Clicking "Posted" badge shows the posting log (who, when).
- **Edit Draft**: Draft entries can be modified before final posting.

## 5. Integration Notes
- Critical for double-entry bookkeeping validation.
- Debits must always equal Credits. The UI highlights unbalanced entries with an "Unbalanced" warning badge.
- Tied closely to the General Ledger.
