# Looker Integration & Embedding Approaches Guide

This document outlines the architecture, configuration requirements, and testing procedures for the four progressive Looker integration and embedding approaches implemented across the branches of this repository.

---

## Comparative Overview of Approaches

| Step / Approach | Git Branch | Primary Script | Purpose & Capabilities | Required Credentials |
| :--- | :--- | :--- | :--- | :--- |
| **1. Looker API (Pure SDK)** | `embed-step01-api` | [looker_api_demo.py](file:///usr/local/google/home/andresousa/projects/ecommerce/embed_demo/looker_api_demo.py) | Programmatic query execution via Looker Python SDK without UI embedding. | [looker.ini](file:///usr/local/google/home/andresousa/projects/ecommerce/embed_demo/looker.ini) (API 3 Client ID & Secret) |
| **2. Secure SSO Embedding** | `embed-step02-sso` | `sso_server.py` | Securely embedding LookML dashboards in web iframes using backend-signed SSO URLs (no Looker user login required). | [embed_config.json](file:///usr/local/google/home/andresousa/projects/ecommerce/embed_demo/embed_config.json) (Looker URL, Embed Secret, Dashboard ID) |
| **3. Looker Embed SDK** | `embed-step03-embed-sdk` | `sso_server.py` | Interactive dashboard embedding with bi-directional JavaScript communication (custom UI buttons driving dashboard filters). | [embed_config.json](file:///usr/local/google/home/andresousa/projects/ecommerce/embed_demo/embed_config.json) (Looker URL, Embed Secret, Dashboard ID) |
| **4. Rich Data Application** | `embed-step04-rich-app` | `sso_server.py` | Full portal combining API SDK (to dynamically fetch filter options like Brands from Looker) with Embed SDK (to filter dashboard). | Both [looker.ini](file:///usr/local/google/home/andresousa/projects/ecommerce/embed_demo/looker.ini) and [embed_config.json](file:///usr/local/google/home/andresousa/projects/ecommerce/embed_demo/embed_config.json) |

---

## Prerequisites & Credentials Setup

Before testing the approaches, two configuration files must be populated with valid credentials from your Looker instance (`https://9ced7b3e-c0b9-44fe-b0da-e73fdf7cbc1c.looker.app`):

### 1. Service Account API Credentials ([looker.ini](file:///usr/local/google/home/andresousa/projects/ecommerce/embed_demo/looker.ini))
Required for **Step 1** and **Step 4**.
1. Navigate to Looker **Admin** $\rightarrow$ **Users** $\rightarrow$ **Service Accounts** and create a dedicated Service Account for your integration.
2. Click **API Keys** under that Service Account and generate a new key pair (**Client ID** and **Client Secret**).
3. Update [looker.ini](file:///usr/local/google/home/andresousa/projects/ecommerce/embed_demo/looker.ini):
```ini
[Looker]
base_url=https://9ced7b3e-c0b9-44fe-b0da-e73fdf7cbc1c.looker.app
client_id=<YOUR_API_CLIENT_ID>
client_secret=<YOUR_API_CLIENT_SECRET>
verify_ssl=true
```

### 2. Embed Secret ([embed_config.json](file:///usr/local/google/home/andresousa/projects/ecommerce/embed_demo/embed_config.json))
Required for **Step 2**, **Step 3**, and **Step 4**.
1. Navigate to Looker Admin $\rightarrow$ Platform $\rightarrow$ **Embed** and retrieve or reset the **Embed Secret**.
2. Update [embed_config.json](file:///usr/local/google/home/andresousa/projects/ecommerce/embed_demo/embed_config.json):
```json
{
  "looker_url": "https://9ced7b3e-c0b9-44fe-b0da-e73fdf7cbc1c.looker.app",
  "embed_secret": "<YOUR_EMBED_SECRET>",
  "dashboard_id": "training_ecommerce::business_pulse"
}
```

---

## Step-by-Step Testing Procedures

### Step 1: Looker API (Pure SDK)
* **Current Branch:** `embed-step01-api`
* **Test Command:**
  ```bash
  cd embed_demo
  python3 looker_api_demo.py
  ```
* **Expected Behavior:** Verifies authentication via `sdk.me()`, executes an inline query on the `order_items` Explore, and outputs the top 12 months of revenue in JSON format.

### Step 2: Secure SSO Embedding
* **Switch Branch:**
  ```bash
  git checkout embed-step02-sso
  ```
* **Test Command:**
  ```bash
  cd embed_demo
  python3 sso_server.py
  ```
* **Expected Behavior:** Starts a local HTTP server at `http://localhost:8080`. Opening this URL in a browser renders the `business_pulse` LookML dashboard inside an iframe authenticated via a backend-generated HMAC-SHA1 signed URL.

### Step 3: Looker Embed SDK (Interactive Dashboard)
* **Switch Branch:**
  ```bash
  git checkout embed-step03-embed-sdk
  ```
* **Test Command:**
  ```bash
  cd embed_demo
  python3 sso_server.py
  ```
* **Expected Behavior:** Starts a local server at `http://localhost:8080`. The rendered page includes custom HTML filter buttons ("Filter: California", "Filter: New York"). Clicking these buttons sends JavaScript events via `@looker/embed-sdk` to update dashboard filters and re-run queries without reloading the iframe.

### Step 4: Rich Application (Advanced Integration)
* **Switch Branch:**
  ```bash
  git checkout embed-step04-rich-app
  ```
* **Test Command:**
  ```bash
  cd embed_demo
  python3 sso_server.py
  ```
* **Expected Behavior:** Starts a full data application portal at `http://localhost:8080`. On load, the frontend queries the local `/api/brands` endpoint, which uses the Looker Python SDK to dynamically fetch distinct brand names from Looker. Selecting a brand from the populated dropdown uses the Embed SDK to filter the embedded dashboard in real time.
