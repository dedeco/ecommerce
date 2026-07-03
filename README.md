# Ecommerce
Repository demo

## LookML Model

This repository contains a LookML model for e-commerce analysis.

### Period-over-Period (PoP) YOY Metrics

We have implemented Year-over-Year (YOY) metrics for the `order_items` explore using Looker's native `period_over_period` type measures.

To keep the codebase modular, these metrics are defined in an extended view file:
*   [views/order_items_extended.view.lkml](views/order_items_extended.view.lkml) (extends `order_items`)

#### Available YOY Measures:

*   **Revenue YOY:**
    *   `total_revenue_last_year`: Total revenue from the same period in the previous year.
    *   `total_revenue_yoy_difference`: Absolute difference in revenue compared to the previous year.
    *   `total_revenue_yoy_relative_change`: Percentage change in revenue compared to the previous year.
*   **Order Count YOY:**
    *   `order_count_last_year`: Order count from the same period in the previous year.
    *   `order_count_yoy_difference`: Absolute difference in order count compared to the previous year.
    *   `order_count_yoy_relative_change`: Percentage change in order count compared to the previous year.

All these metrics are based on the `created` dimension group (`created_year` timeframe) and automatically adapt to the timeframe grain selected in the Explore query.
