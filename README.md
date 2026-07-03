# Ecommerce
Repository demo

## LookML Extends

This repository demonstrates how to use LookML **Extends** to modularize and reuse code for both Views and Explores.

### Step 1: View Extends (Implemented in `views/`)

We created a base view to share location dimensions across multiple views.

1.  **Created a base view `location`** in `views/location.view.lkml`.
    *   Defines common location-related dimensions: `city`, `state`, `zip`, `country`, `latitude`, and `longitude`.
    *   Uses `extension: required` to prevent direct use in Explores.
2.  **Extended `users` and `events` views** to inherit from `location`.
    *   Added `extends: [location]` to both views.
    *   Removed duplicate dimension definitions.

### Step 2: Explore Extends (Implemented in `models/training_ecommerce.model.lkml`)

We created a base Explore to share a core set of joins across multiple Explores.

1.  **Created a base Explore `base_events`**:
    *   Joins `events` with `event_session_facts` and `users`.
    *   Uses `extension: required` so it is not visible to users in the Explore menu.
2.  **Extended `events` Explore**:
    *   Uses `extends: [base_events]` to inherit the core joins.
    *   Adds a specific join to `event_session_funnel`.
3.  **Extended `conversions` Explore**:
    *   Uses `extends: [base_events]` to inherit the core joins.
    *   Adds a join to `order_items`.
    *   Demonstrates field exclusion by removing `order_items.total_revenue_from_completed_orders` from the Explore field list using `fields: [ALL_FIELDS*, -order_items.total_revenue_from_completed_orders]`.
