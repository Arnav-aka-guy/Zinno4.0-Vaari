"""Prompt and schema definition for HostedVisionReader (Step 03).

NOTE ON CONFIDENCE: The confidence values returned by the vision model are the model's
own self-reported estimates and are NOT statistically calibrated probabilities.
"""

PROMPT_VERSION = "v1"

REGISTER_EXTRACTION_PROMPT = """You are reading a photograph of a handwritten crop-residue machinery booking register from a Custom Hiring Centre in Punjab (Gurmukhi Punjabi and English mixed).
All entries on this page are synthetic test entries.

Extract the rows into ONLY valid JSON matching this exact structure (no markdown fences, no prose):
{
  "rows": [
    {
      "row": 1,
      "fields": {
        "phone": "string or null",
        "name": "string or null",
        "village": "string or null",
        "acres": 4.5,
        "service_type": "super_seeder | happy_seeder | baler | mulcher | raw string",
        "harvest_date": "YYYY-MM-DD or DD/MM or null",
        "note": "string or null"
      },
      "confidence": {
        "phone": 0.95,
        "name": 0.60,
        "village": 0.90,
        "acres": 0.85,
        "service_type": 0.92,
        "harvest_date": 0.80
      }
    }
  ]
}

Strict rules:
1. Copy only what is written on the page.
2. Do not guess missing values — use null whenever a cell is blank.
3. Do not invent rows, and ignore crossed-out rows or header rows.
4. Give low confidence (below 0.6) to any cell that is smudged, overwritten, or unclear.
   Note: confidence is your own uncalibrated estimate from 0.0 to 1.0.
"""

RETRY_JSON_MESSAGE = (
    "Return ONLY valid JSON matching the required schema with top-level key 'rows'. "
    "Do not include markdown formatting or any explanation."
)
