# Plan 3.1: The Intermediary API Bridge (Exhaustive Detail)

## 1. Scope & Objective
This document defines the "Translator" layer between your premium HTML pages and the Python Backend. It ensures that frontend developers never have to worry about headers, tokens, or raw fetch syntax.

---

## 2. Technical Standard
- **File Location**: `assets/js/api_bridge.js`
- **Pattern**: Singleton Class or Module Pattern.
- **Protocol**: HTTPS / Fetch API (Async/Await).

---

## 3. Core Class Logic (`ApexAPI`)
The bridge will expose a simple method for every module defined in Phase 2.

```javascript
class ApexAPI {
    constructor() {
        this.baseURL = window.location.origin + "/api/v1";
        this.token = localStorage.getItem("apex_token");
    }

    async request(endpoint, options = {}) {
        const headers = {
            "Content-Type": "application/json",
            ...options.headers
        };
        if (this.token) headers["Authorization"] = `Bearer ${this.token}`;

        const response = await fetch(`${this.baseURL}${endpoint}`, { ...options, headers });
        if (response.status === 401) window.location.href = "/index.html"; // Auto-logout
        return response.json();
    }
}
```

---

## 4. Module-Specific Methods
The bridge will have dedicated sections for:
- **Auth**: `login(user, pass)`, `logout()`.
- **Sales**: `submitOrder(data)`, `getOrder(id)`.
- **Inventory**: `updateStock(sku, adjustment)`.
- **Finance**: `getLedger(params)`.

---

## 5. Security & Error Handling
- **Token Management**: If the API returns a 401 (Expired Token), the bridge must clear `localStorage` and redirect to the login screen immediately to prevent data leaks.
- **Global Loader**: The bridge will communicate with a `global_loader_id` in the UI to show a "Processing..." spinner during every fetch call.

---

## 6. Verification Steps
1. [ ] **Connectivity Test**: Ping `/api/v1/health` via the bridge and verify success.
2. [ ] **Token Persistence**: verify that refreshing the page does not lose the Auth token from the request headers.
3. [ ] **Error Toast Test**: verify that a 500 error from the backend triggers a user-friendly error message in the UI instead of a console crash.
