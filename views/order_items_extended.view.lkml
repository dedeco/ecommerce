include: "/views/order_items.view"

view: order_items_extended {
  extends: [order_items]

  # --- Revenue YOY ---

  measure: total_revenue_last_year {
    type: period_over_period
    description: "Total revenue from the previous year"
    based_on: total_revenue
    based_on_time: created_year
    period: year
    kind: previous
    value_format_name: usd
  }

  measure: total_revenue_yoy_difference {
    type: period_over_period
    description: "Difference in total revenue compared to the previous year"
    based_on: total_revenue
    based_on_time: created_year
    period: year
    kind: difference
    value_format_name: usd
  }

  measure: total_revenue_yoy_relative_change {
    type: period_over_period
    description: "Relative change in total revenue compared to the previous year"
    based_on: total_revenue
    based_on_time: created_year
    period: year
    kind: relative_change
    value_format_name: percent_2
  }

  # --- Order Count YOY ---

  measure: order_count_last_year {
    type: period_over_period
    description: "Order count from the previous year"
    based_on: order_count
    based_on_time: created_year
    period: year
    kind: previous
  }

  measure: order_count_yoy_difference {
    type: period_over_period
    description: "Difference in order count compared to the previous year"
    based_on: order_count
    based_on_time: created_year
    period: year
    kind: difference
  }

  measure: order_count_yoy_relative_change {
    type: period_over_period
    description: "Relative change in order count compared to the previous year"
    based_on: order_count
    based_on_time: created_year
    period: year
    kind: relative_change
    value_format_name: percent_2
  }
}
