
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google.genai.errors import APIError

from classifier import classify_ticket, validate_ticket

load_dotenv()

st.set_page_config(
    page_title="AI Support Ticket Classifier",
    page_icon="🎫",
    layout="centered",
)

HISTORY_FILE = Path("tickets.csv")

st.title("🎫 AI Support Ticket Classifier")
st.write(
    "Analyse customer support messages, identify priority, "
    "and draft a suggested response."
)

st.info(
    "Use fictional or anonymised customer messages. "
    "AI classifications can be incorrect, so review results "
    "before taking action."
)

if not os.getenv("GEMINI_API_KEY"):
    st.warning(
        "API key not found. Add GEMINI_API_KEY to your .env file "
        "and restart the app."
)

with st.form("ticket_form"):
    ticket = st.text_area(
        "Customer support message",
        placeholder=(
            "Example: I was charged twice for my subscription..."
        ),
        height=180,
        max_chars=5000,
    )

    submitted = st.form_submit_button(
        "Analyse ticket",
        type="primary",
        use_container_width=True,
    )

if submitted:
    try:
        ticket = validate_ticket(ticket)

        with st.spinner("Analysing ticket..."):
            result = classify_ticket(ticket)

        st.session_state["latest_ticket"] = ticket
        st.session_state["latest_result"] = result.model_dump()

        st.success("Ticket analysis complete.")

        st.subheader("Classification")

        col1, col2, col3 = st.columns(3)

        col1.metric("Category", result.category)
        col2.metric("Priority", result.priority)
        col3.metric("Sentiment", result.sentiment)

        st.subheader("Summary")
        st.write(result.summary)

        st.subheader("Suggested response")
        st.write(result.suggested_reply)

        st.caption(
            "This response is a draft. A human should review it "
            "before sending it to a customer."
        )

        # Save the completed analysis to CSV.
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ticket": ticket,
            "category": result.category,
            "priority": result.priority,
            "sentiment": result.sentiment,
            "summary": result.summary,
            "suggested_reply": result.suggested_reply,
        }

        new_record = pd.DataFrame([record])

        if HISTORY_FILE.exists():
            old_records = pd.read_csv(HISTORY_FILE)
            history = pd.concat(
                [old_records, new_record],
                ignore_index=True,
            )
        else:
            history = new_record

        history.to_csv(HISTORY_FILE, index=False)
        st.toast("Analysis saved to local ticket history.")

    except ValueError as error:
        st.error(str(error))

    except APIError as error:
        if getattr(error, "code", None) == 503:
            st.warning(
                "Gemini is temporarily busy. "
                "Please wait a minute and try again."
            )
        else:

            st.error(f"Gemini API error: {error}")
        # Log technical details to the local terminal, not the UI.

    except RuntimeError as error:
        st.error(str(error))

    except Exception as error:
        st.error(
            "An unexpected error occurred. Check the terminal "
            "for technical details."
        )
        print(f"Unexpected error: {error}")


st.divider()
st.subheader("Ticket history")

if HISTORY_FILE.exists():
    try:
        history = pd.read_csv(HISTORY_FILE)

        st.write(f"Saved analyses: {len(history)}")
        st.dataframe(
            history[
                [
                    "timestamp",
                    "category",
                    "priority",
                    "sentiment",
                    "summary",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        csv_data = history.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download ticket history (CSV)",
            data=csv_data,
            file_name="ticket_history.csv",
            mime="text/csv",
        )

    except (OSError, ValueError, pd.errors.ParserError):
        st.warning("Could not read the saved ticket history.")
else:
    st.write("No tickets have been analysed yet.")
