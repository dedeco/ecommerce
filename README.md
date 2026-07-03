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

---

## Looker Integration & Embedding Tutorials - Step 2

This branch demonstrates **Secure SSO Embedding**.

### Key Files:
*   [sso_server.py](sso_server.py): Python script that generates the signed SSO URL and runs a local web server to display the embedded dashboard in an iframe.
*   [embed_config.json.example](embed_config.json.example): Template for configuration.

### How to run the SSO Embed Demo:

1.  **Configure Credentials:**
    Copy `embed_config.json.example` to `embed_config.json`:
    ```bash
    cp embed_config.json.example embed_config.json
    ```
2.  **Edit Configuration:**
    Edit `embed_config.json` and fill in:
    *   `looker_url`: Your Looker instance URL (e.g., `https://your-company.looker.com`).
    *   `embed_secret`: The Embed Secret from Looker Admin -> Platform -> Embed.
    *   `dashboard_id`: The ID of the dashboard (`training_ecommerce::business_pulse`).
3.  **Run the Server:**
    ```bash
    python3 sso_server.py
    ```
4.  **View the Embed:**
    Open your browser and navigate to `http://localhost:8080`.
