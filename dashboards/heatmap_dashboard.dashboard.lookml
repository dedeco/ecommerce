- dashboard: heatmap_dashboard
  title: Heatmap Dashboard
  layout: grid
  elements:
  - name: Order Status Heatmap
    title: Order Status Heatmap
    model: training_ecommerce
    explore: order_items
    type: looker_heatmap
    fields: [order_items.created_date, order_items.status, order_items.order_item_count]
    pivots: [order_items.status]
    sorts: [order_items.created_date desc]
    limit: 500
    column_limit: 50
    total: false
    row_total: false
    listen: {}
    note_state: collapsed
    note_display: hover
    note_text: A heatmap of order statuses over time.
    x_axis_gridlines: false
    y_axis_gridlines: true
    show_view_names: false
    show_y_axis_labels: true
    show_y_axis_ticks: true
    y_axis_tick_density: default
    y_axis_tick_density_custom: 5
    show_x_axis_label: true
    show_x_axis_ticks: true
    x_axis_scale: auto
    y_axis_scale: auto
    y_axis_reversed: false
    show_null_points: true
    interpolation: linear
    color_application:
      collection_id: 181b0404-5347-43ab-8246-133d1055b2f1
      palette_id: 2f5b3631-5730-42e9-938a-b461b077334c
    series_colors: {}
    show_legend: true
    legend_position: center
    show_value_labels: false
    label_density: 25
    label_type: lab
    font_size: 12
    series_types: {}
    ordering: none
    show_null_labels: false
    show_totals_labels: false
    show_silhouette: false
    totals_color: "#808080"
    trellis: ''
    stacking: ''
    limit_displayed_rows: false
    hide_totals: false
    hide_row_totals: false
    y_axes: []
    x_axis_label: Date
    x_axis_zoom: true
    y_axis_zoom: true
    hidden_fields: []
    defaults_version: 1
    series_labels: {}
    show_row_numbers: true
    transpose: false
    truncate_text: true
    size_to_fit: true
    show_sql_query_menu_options: false
    show_drill_overlay: true
    show_datatable: true
    show_comparison: true
    comparison_type: value
    comparison_reverse_colors: false
    show_comparison_label: true
    enable_conditional_formatting: false
    conditional_formatting_include_totals: false
    conditional_formatting_include_nulls: false
