# Setting Up the Live Demo Plot Polygon at the Venue

During the live on-stage demo, the Driver phone captures real GPS coordinates inside the presentation hall. To ensure the live position check (`check_position`) evaluates against a real polygon boundary around the hall, follow these steps before going on stage:

## Step-by-Step Procedure

1. **Draw the Polygon at the Venue:**
   - Open [https://geojson.io](https://geojson.io) in your browser.
   - Zoom in to the exact building or hall where the demo is taking place.
   - Use the polygon tool to draw a rectangle around the hall (roughly 2 to 4 acres).
   - In the feature's `properties` object on the right panel, add:
     ```json
     "request_id": 1
     ```
2. **Save the GeoJSON File:**
   - Save the resulting `FeatureCollection` as `examples/demo_plot.geojson`.
3. **Attach the Polygon to the Demo Request:**
   - After running `python tasks.py reset`, run:
     ```bash
     python scripts/load_plots.py examples/demo_plot.geojson
     ```
   - This attaches the polygon geometry, geodesic acreage, and centroid to Request #1's plot (`location_source = "polygon"`).

## What to Say on Stage

As specified in `docs/BUILD_PLAN.md` Section 6, state plainly to the judges before anyone asks:
- *"The demo plot polygon was drawn around this hall so our phone's live GPS fix is checked against a real polygon boundary on stage."*
- *"Because our live job finishes in under a minute on stage, the `too_fast` check will fire — that is the anomaly check working as designed, and it never blocks or penalises the farmer."*
