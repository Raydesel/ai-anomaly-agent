import json
import streamlit as st
from pipeline import fetch_recent_logs, analyze_anomalies

st.set_page_config(page_title="Daily Server Log Scan", page_icon="📊")

st.title("Daily Server Log Scan")
st.write("Use the button below to fetch today\'s server logs and analyze them for severe anomalies using Claude AI.")

if st.button("Run Daily Scan"):
    with st.spinner("Fetching recent logs..."):
        logs_json = fetch_recent_logs()

    try:
        logs_data = json.loads(logs_json)
    except json.JSONDecodeError:
        st.error("Failed to parse server log data from Supabase.")
    else:
        if isinstance(logs_data, dict) and logs_data.get("error"):
            st.error(f"Failed to fetch logs: {logs_data['error']}")
        elif isinstance(logs_data, dict) and logs_data.get("message") == "No logs found in the server_logs table":
            st.info("No logs found in the server_logs table.")
        else:
            with st.spinner("Analyzing anomalies with Claude AI..."):
                report = analyze_anomalies(logs_json)

            st.markdown("### Claude Anomaly Report")
            st.markdown(report)
