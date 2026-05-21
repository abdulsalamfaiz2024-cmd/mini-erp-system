# Phase 3 Plan: Front-end Integration & Connectivity

## 1. Objective
Enable the HTML pages to communicate with the Backend API and display dynamic data.

---

## 2. Implementation Sub-Phases

### Phase 3.1: The API Bridge
- **Standard**: Create `assets/js/api_bridge.js`.
- **Logic**: Centralized class or set of functions using `fetch()` and `async/await`.
- **Security**: Automatically attaches the "Authorization: Bearer <TOKEN>" header to every call.

### Phase 3.2: Page-Specific Scripts
- **Standard**: Create JS files mirroring the HTML (e.g., `assets/js/sales_orders.js`).
- **Interaction**:
    - `onLoad`: Call `getOrders()`.
    - `onSubmit`: Gather form fields into JSON and call `submitOrder()`.

### Phase 3.3: Global State & Routing
- Handle login redirects (If No Token -> Redirect to index.html).
- Populate navigation "Active" states dynamically if needed.

---

## 3. Success Metrics
- A user can log in.
- A user can create a Sales Order and see it appear in the "Orders List".
- Every value in the UI matches the value in the Database.
