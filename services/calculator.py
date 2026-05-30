# services/calculator.py
import streamlit as st

def smart_calculator():
    """App 5: Smart Calculator with expression evaluation and history."""
    st.markdown("<h2 style='text-align: center;'>🧮 Smart Calculator</h2>", unsafe_allow_html=True)
    st.markdown("Evaluate mathematical expressions (+, -, *, /, **, etc.)")
    
    expression = st.text_input("Enter expression:", placeholder="e.g., 2 + 3 * 4 / 2")
    
    if st.button("Calculate", type="primary", use_container_width=True):
        if expression:
            try:
                result = eval(expression, {"__builtins__": {}}, {})
                st.success(f"Result: **{result}**")
                if "calc_history" not in st.session_state:
                    st.session_state.calc_history = []
                st.session_state.calc_history.append((expression, result))
            except Exception as e:
                st.error(f"Invalid expression: {e}")
    
    if "calc_history" in st.session_state and st.session_state.calc_history:
        st.subheader("📜 History")
        for idx, (expr, res) in enumerate(reversed(st.session_state.calc_history[-5:])):
            st.text(f"{expr} = {res}")
        if st.button("Clear History"):
            st.session_state.calc_history = []
            st.rerun()
    else:
        st.info("No calculations yet. Enter an expression above.")
    
    if st.button("🏠 Back to Home", use_container_width=True):
        st.session_state["current_app"] = "home"
        st.rerun()