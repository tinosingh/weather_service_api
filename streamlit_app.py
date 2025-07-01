"""
Simple Streamlit GUI for the Weather Service.

This provides a minimal interface for managing weather data
fetching parameters.
"""
import streamlit as st
import uuid
from datetime import datetime, timedelta


# Set page config
st.set_page_config(
    page_title="Weather Data Fetcher",
    page_icon="⛅",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS for better styling
st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .success-msg {
        color: #0f9d58;
        padding: 1em;
        background-color: #e8f5e9;
        border-radius: 0.5em;
        margin: 1em 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def main():
    """Main Streamlit application."""
    st.title("⛅ Weather Data Fetcher")

    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")

        # Location selection (simplified to just Kaisaniemi for now)
        st.subheader("Location")
        location = {
            "id": str(uuid.uuid4()),
            "name": "Kaisaniemi, Helsinki",
            "lat": 60.1699,
            "lon": 24.9384
        }
        st.write(f"**Selected:** {location['name']}")

        # Time range selection
        st.subheader("Time Range")
        date_col1, date_col2 = st.columns(2)
        with date_col1:
            start_date = st.date_input(
                "Start date",
                value=datetime.now() - timedelta(days=7),
                max_value=datetime.now(),
                help="Start date for data fetching"
            )
        with date_col2:
            end_date = st.date_input(
                "End date",
                value=datetime.now(),
                min_value=start_date,
                max_value=datetime.now(),
                help="End date for data fetching"
            )

        # Time resolution
        st.subheader("Time Resolution")
        resolution = st.selectbox(
            "Select time resolution",
            ["1 hour", "3 hours", "6 hours", "12 hours", "1 day"],
            index=2,
            help="Time interval between data points"
        )

        # Weather parameters
        st.subheader("Weather Parameters")
        col1, col2 = st.columns(2)
        with col1:
            temperature = st.checkbox("Temperature", True)
            humidity = st.checkbox("Humidity", True)
            pressure = st.checkbox("Pressure", False)
        with col2:
            wind_speed = st.checkbox("Wind Speed", True)
            wind_direction = st.checkbox("Wind Direction", False)
            precipitation = st.checkbox("Precipitation", True)

    # Main content area
    st.header("Fetch Weather Data")

    # Show selected parameters
    with st.expander("Selected Parameters", expanded=True):
        st.write(
            f"**Location:** {location['name']} "
            f"({location['lat']}, {location['lon']})"
        )
        st.write(f"**Time Range:** {start_date} to {end_date}")
        st.write(f"**Time Resolution:** {resolution}")

        selected_params = [
            param for param, selected in [
                ("Temperature", temperature),
                ("Humidity", humidity),
                ("Pressure", pressure),
                ("Wind Speed", wind_speed),
                ("Wind Direction", wind_direction),
                ("Precipitation", precipitation)
            ] if selected
        ]
        st.write(
            "**Selected Parameters:** " +
            ", ".join(selected_params) or "None"
        )

    # Fetch data button
    fetch_col1, fetch_col2 = st.columns([1, 3])
    with fetch_col1:
        if st.button("🔄 Fetch Weather Data", type="primary"):
            # In a real app, this would call the API
            st.session_state.last_fetch = {
                "location": location,
                "start_date": start_date,
                "end_date": end_date,
                "resolution": resolution,
                "parameters": selected_params,
                "timestamp": datetime.now()
            }

    # Show success message if data was fetched
    if "last_fetch" in st.session_state:
        last_fetch = st.session_state.last_fetch
        time_since = (datetime.now() - last_fetch["timestamp"]).total_seconds()

        if time_since < 5:  # Only show for 5 seconds
            st.markdown(
                f"""
                <div class="success-msg">
                    ✅ Successfully fetched weather data for
                    {last_fetch['location']['name']} from
                    {last_fetch['start_date']} to {last_fetch['end_date']}
                </div>
                """,
                unsafe_allow_html=True
            )

    # Placeholder for data visualization
    st.subheader("Weather Data")
    st.info(
        "🔍 Select parameters and click 'Fetch Weather Data' "
        "to load visualization"
    )

    # Example visualization (in a real app, this would show actual data)
    if "last_fetch" in st.session_state and temperature:
        import pandas as pd
        import numpy as np

        # Generate sample data
        dates = pd.date_range(
            start=start_date,
            end=end_date + timedelta(days=1),
            freq=resolution.split()[0].upper() + "H"
        )

        # Create sample temperature data
        base_temp = 15.0
        temps = base_temp + 10 * np.sin(np.linspace(0, 10, len(dates)))

        # Create a simple line chart
        chart_data = pd.DataFrame({
            "Date": dates,
            "Temperature (°C)": temps,
        })

        st.line_chart(chart_data.set_index("Date"))

    # Add some info about the app
    st.sidebar.markdown("---")
    st.sidebar.info(
        "ℹ️ This is a minimal interface for the Weather Data Fetcher. "
        "Select your parameters and click 'Fetch Weather Data' to retrieve "
        "weather information."
    )


if __name__ == "__main__":
    main()
