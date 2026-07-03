# Ecommerce
Repository demo

## LookML Extends - Step 1: View Extends

This branch demonstrates how to use LookML **View Extends** to modularize and reuse code.

### Implementation Details:

1.  **Created a base view `location`** in `views/location.view.lkml`.
    *   This view contains common location-related dimensions: `city`, `state`, `zip`, `country`, `latitude`, and `longitude`.
    *   It uses `extension: required` to prevent it from being used directly in Explores.
2.  **Extended `users` and `events` views** to inherit from `location`.
    *   Added `include: location.view` and `extends: [location]` to both views.
    *   Removed the duplicate dimension definitions from `views/users.view.lkml` and `views/events.view.lkml`.

This ensures that any updates to the location dimensions only need to be made in one place (`views/location.view.lkml`).
