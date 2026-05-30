# services/converter.py
import streamlit as st

CONVERSION_TYPES = {
    "📏 Length": {
        "units": ["mm", "cm", "m", "km", "in", "ft", "yd", "mi"],
        "to_base": {"mm": 0.001, "cm": 0.01, "m": 1, "km": 1000,
                     "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.344},
    },
    "⚖️ Weight": {
        "units": ["mg", "g", "kg", "t", "oz", "lb"],
        "to_base": {"mg": 0.000001, "g": 0.001, "kg": 1, "t": 1000,
                     "oz": 0.0283495, "lb": 0.453592},
    },
    "🌡️ Temperature": {
        "units": ["°C", "°F", "K"],
        "to_base": None,
    },
    "🧪 Volume": {
        "units": ["mL", "L", "gal (US)", "qt (US)", "cup", "fl oz"],
        "to_base": {"mL": 0.001, "L": 1, "gal (US)": 3.78541,
                     "qt (US)": 0.946353, "cup": 0.236588, "fl oz": 0.0295735},
    },
    "⚡ Speed": {
        "units": ["m/s", "km/h", "mph", "knot", "ft/s"],
        "to_base": {"m/s": 1, "km/h": 0.277778, "mph": 0.44704,
                     "knot": 0.514444, "ft/s": 0.3048},
    },
    "💾 Data": {
        "units": ["B", "KB", "MB", "GB", "TB"],
        "to_base": {"B": 1, "KB": 1024, "MB": 1048576,
                     "GB": 1073741824, "TB": 1099511627776},
    },
}


def convert_value(value, from_unit, to_unit, category):
    if category == "🌡️ Temperature":
        return _convert_temperature(value, from_unit, to_unit)
    data = CONVERSION_TYPES[category]
    base_val = value * data["to_base"][from_unit]
    return base_val / data["to_base"][to_unit]


def _convert_temperature(value, from_unit, to_unit):
    # To °C first
    if from_unit == "°C":
        celsius = value
    elif from_unit == "°F":
        celsius = (value - 32) * 5 / 9
    else:
        celsius = value - 273.15
    # From °C to target
    if to_unit == "°C":
        return celsius
    elif to_unit == "°F":
        return celsius * 9 / 5 + 32
    else:
        return celsius + 273.15


def converter():
    """Unit Converter — convert between 50+ units across 6 categories."""
    st.markdown("<h2 style='text-align: center;'>📐 Unit Converter</h2>", unsafe_allow_html=True)
    st.markdown("Convert between length, weight, temperature, volume, speed & data units.")

    category = st.selectbox("Category", list(CONVERSION_TYPES.keys()))

    units = CONVERSION_TYPES[category]["units"]

    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        from_unit = st.selectbox("From", units, key="from_unit")
        value = st.number_input("Value", value=1.0, step=0.1, format="%g")
    with col2:
        st.markdown("<div style='text-align:center;padding-top:2.5rem;font-size:2rem;'>⇄</div>", unsafe_allow_html=True)
    with col3:
        to_unit = st.selectbox("To", [u for u in units if u != from_unit] + [from_unit],
                               index=0 if len(units) > 1 else 0, key="to_unit")

    result = convert_value(value, from_unit, to_unit, category)

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        padding: 1.5rem;
        border-radius: 1rem;
        text-align: center;
        margin: 1rem 0;
        color: white;
    ">
        <span style="font-size:1.8rem;font-weight:700;">{value} {from_unit}</span>
        <span style="font-size:1.5rem;margin:0 1rem;">=</span>
        <span style="font-size:2.2rem;font-weight:700;">{result:,.4g}</span>
        <span style="font-size:1.8rem;font-weight:700;"> {to_unit}</span>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Tip: You can change the value above and see results update instantly.")

    if st.button("🏠 Back to Home", use_container_width=True):
        st.session_state["current_app"] = "home"
        st.rerun()
