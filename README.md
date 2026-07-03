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

### 7. Rich Application (Advanced Integration)
*   **Branch:** `embed-step04-rich-app`
*   **Description:** Implements a full data application portal. It uses Looker API (Python SDK) to dynamically fetch filter options (Brands) from the database and uses the Embed SDK to apply the user's selection to the embedded `business_pulse` dashboard.

---

## Looker Integration & Embedding Tutorials - Step 4

This branch demonstrates a **Rich Application** combining both the **Looker API** and the **Embed SDK**.

### Key Files:
*   [sso_server.py](sso_server.py): Updated Python script. It now uses the `looker-sdk` to query Looker's API and acts as a local API gateway, serving the frontend, fetching brands from Looker, and generating signed SSO URLs.
*   [embed_config.json.example](embed_config.json.example): Template for embed configuration.
*   [looker.ini.example](looker.ini.example): Template for Looker API credentials.

### How to run the Rich Application Demo:

1.  **Install Looker Python SDK:**
    ```bash
    pip install looker-sdk
    ```
2.  **Configure API Credentials:**
    Copy `looker.ini.example` to `looker.ini` and fill in your Looker API credentials:
    ```bash
    cp looker.ini.example looker.ini
    ```
3.  **Configure Embed Credentials:**
    Copy `embed_config.json.example` to `embed_config.json` and fill in your Embed secret and dashboard details:
    ```bash
    cp embed_config.json.example embed_config.json
    ```
4.  **Run the Server:**
    ```bash
    python3 sso_server.py
    ```
5.  **Test the Portal:**
    *   Open your browser and navigate to `http://localhost:8080`.
    *   On load, the app will call the local backend endpoint `/api/brands`. The backend will query Looker API for distinct brands in the `order_items` explore and return them.
    *   A **custom HTML dropdown** will populate with these brands dynamically.
    *   Selecting a brand from the dropdown will send a message via the Embed SDK to filter the embedded `business_pulse` dashboard by that brand and refresh it.
