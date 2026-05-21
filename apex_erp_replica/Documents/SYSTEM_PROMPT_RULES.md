
This document serves as the master instruction set for building and documenting new pages within the Apex ERP system. Follow these rules strictly to ensure architectural consistency.

---

## 🏗️ 1. Project Directory Structure
All work MUST follow this folder hierarchy:
- `/Pages/`: Functional HTML components for each specific view.
- `/Documents/specs/`: Markdown technical specifications (API Contracts).
- `/assets/`:
    - `/css/main.css`: Global design tokens and shared UI styles.
    - `/js/`: Client-side logic and API bridges.
- `/Backend/`: Python logic (models, controllers, api).

---

## 🎨 2. UI Development Rules
When presented with a UI image:
1. **Analyze Design**: Identify the core layout (Grid, Flexbox), color palette (HSL/Hex), and typography.
2. **Implementation**: 
    - Use **Vanilla HTML5** and **CSS3**.
    - Maintain the "Premium" aesthetic: smooth transitions, consistent padding (usually 20px-40px), and rounded corners (8px-12px).
    - **Place files in `/Pages/[page_name].html`**.
3. **Connectivity**: Add the appropriate navigation link to the Sidebar in `index.html`.

---


---

## 🔗 3. Integration Protocol
After creating a page:
1. **Update `index.html`**: Ensure the sidebar menu points to the new file in `/Pages/`.
2. **CSS Sync**: If new components are created, add their styles to `assets/css/main.css` to maintain brand consistency.
3. **Route Logic**: If a routing script exists in `assets/js/router.js`, register the new view there.

---

## 📄 4. Document Creation Rules
Every new page MUST have a matching technical specification in `/Documents/specs/[page_name]_spec.md`. The document must contain:

### A. UI-to-API Mapping Table
A clear table showing:
| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |

### B. API Data Contract
Provide exact JSON examples for both Request and Response. This ensures the backend developer knows exactly what keys to use (e.g., `invoice_id`, `grand_total`).

### C. Logic & Actions
Define what happens when buttons are clicked (e.g., "Navigates to /Pages/invoice_details.html" or "Triggers POST to /api/orders").

Every thing you did most be documented in the document becouse any other model can read it to build the backend or edite the page IU.
---

## 🛠️ 5. Programmer Handoff
The documentation must be complete enough that a Backend Programmer can build the entire API without looking at the HTML code. If a key is missing in the Document, the job is considered incomplete.
