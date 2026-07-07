# Ecommerce LookML Project

This repository contains a LookML model for e-commerce analysis.

## Project Structure & Features

We have implemented several LookML features, which are documented and code-commented in their respective branches:

### 1. Year-over-Year (YOY) Metrics
*   **Branch:** `feature/yoy-metrics`
*   **Description:** Implements native Period-over-Period (PoP) YOY metrics for the `order_items` Explore.
*   **Key Files:**
    *   `views/order_items_extended.view.lkml` (extends `order_items` to add YOY measures)
    *   `models/training_ecommerce.model.lkml` (configured to use the extended view)

### 2. LookML Extends - Step 1: View Extends
*   **Branch:** `step01`
*   **Description:** Demonstrates how to reuse common location dimensions (city, state, etc.) by creating a base `location` view and extending `users` and `events` views with it.

### 3. LookML Extends - Step 2: Explore Extends
*   **Branch:** `step02`
*   **Description:** Demonstrates how to reuse a core set of joins by creating a base `base_events` Explore and extending it to create `events` and `conversions` Explores. Also demonstrates field exclusion in extended Explores.

### 4. Looker API (Pure SDK)
*   **Branch:** `embed-step01-api`
*   **Description:** Demonstrates how to authenticate with Looker API using the Python SDK and run queries programmatically.

### 5. Secure SSO Embedding (Dashboard)
*   **Branch:** `embed-step02-sso`
*   **Description:** Demonstrates how to securely embed the `business_pulse` LookML dashboard using signed SSO URLs and a local Python server.

### 6. Looker Embed SDK (Interactive Dashboard)
*   **Branch:** `embed-step03-embed-sdk`
*   **Description:** Demonstrates how to use Looker's Embed SDK to establish bi-directional communication, listen to events, and send actions (like filtering) to the embedded dashboard.

---

## Looker Integration & Embedding Tutorials - Step 3

This branch demonstrates the **Looker Embed SDK** for interactive embedding.

### Key Files:
*   [sso_server.py](sso_server.py): Updated Python script. It now generates the signed SSO URL (including `embed_domain`) and serves an HTML page integrated with the Looker Embed SDK.
*   [embed_config.json.example](embed_config.json.example): Template for configuration.

### How to run the Embed SDK Demo:

1.  **Configure Credentials:**
    Copy `embed_config.json.example` to `embed_config.json`:
    ```bash
    cp embed_demo/embed_config.json.example embed_demo/embed_config.json
    ```
2.  **Edit Configuration:**
    Edit `embed_config.json` and fill in:
    *   `looker_url`: Your Looker instance URL (e.g., `https://your-company.looker.com`).
    *   `embed_secret`: The Embed Secret from Looker Admin -> Platform -> Embed.
    *   `dashboard_id`: The ID of the dashboard (`training_ecommerce::business_pulse`).
3.  **Run the Server:**
    ```bash
    cd embed_demo
    python3 sso_server.py
    ```
4.  **View the Interactive Embed:**
    *   Open your browser and navigate to `http://localhost:8080`.
    *   You will see **custom buttons** at the top of the page ("Filter: California", "Filter: New York").
    *   Clicking these buttons will send a message via the Embed SDK to the Looker iframe, updating the `State` filter and running the dashboard automatically.
    *   Open the browser's developer console (F12) to see logs of Looker events being captured by the host page.
