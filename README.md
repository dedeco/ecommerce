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

---

## Looker Integration & Embedding Tutorials

We are implementing a step-by-step guide for Looker API and Embedding.

### Step 1: Looker API (Pure SDK)
*   **Branch:** `embed-step01-api`
*   **Description:** Demonstrates how to authenticate with Looker API using the Python SDK and run queries programmatically.
*   **Key Files:**
    *   `looker_api_demo.py`: Python script to run a query.
    *   `looker.ini.example`: Template for API credentials.

#### How to run the API Demo:

1.  **Install the Looker SDK:**
    ```bash
    pip install looker-sdk
    ```
2.  **Configure Credentials:**
    Copy `looker.ini.example` to `looker.ini` and fill in your Looker Service Account API keys (generated via Looker Admin -> Users -> Service Accounts):
    ```bash
    cp looker.ini.example looker.ini
    ```
3.  **Run the script:**
    ```bash
    python3 looker_api_demo.py
    ```
