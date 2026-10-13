# AI Customer Support Ticket Classifier

A Python web application that uses Google's Gemini API to analyse customer support tickets and generate structured insights.

## Features
- Classifies tickets by category and priority
- Analyses customer sentiment
- Generates concise ticket summaries
- Suggests professional customer support replies
- Stores and displays previous analyses using CSV history

## Technologies
- Python
- Streamlit
- Google Gemini API
- Pydantic
- Pandas
- CSV

## Setup

1. Clone this repository.
2. Create and activate a virtual environment.
3. Install dependencies with:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example` and add your Gemini API key.
5. Start the application with:

   streamlit run app.py

## Notes
A Gemini API key is required. API availability and free-tier usage limits may vary. Use fictional or anonymised customer messages when testing.

AI-generated classifications and suggested replies should be reviewed by a human before use.
