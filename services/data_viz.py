# services/data_viz.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def data_visualizer():
    """App 1: Data Visualizer - CSV/Excel upload and plotting."""
    st.markdown("<h2 style='text-align: center;'>📊 Data Visualizer</h2>", unsafe_allow_html=True)
    st.markdown("Upload a dataset and create beautiful plots.")
    
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Loaded {df.shape[0]} rows, {df.shape[1]} columns")
            st.dataframe(df.head(10), use_container_width=True)
            
            numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
            if len(numeric_cols) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    x_col = st.selectbox("X-axis", numeric_cols, key="x_col")
                with col2:
                    y_col = st.selectbox("Y-axis", numeric_cols, key="y_col")
                plot_type = st.radio("Plot type", ["Line Plot", "Bar Chart", "Scatter Plot"], horizontal=True)
                
                fig, ax = plt.subplots(figsize=(8, 4))
                if plot_type == "Line Plot":
                    ax.plot(df[x_col], df[y_col], marker='o', linestyle='-', color='#2a5298')
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
                    ax.set_title(f"{y_col} vs {x_col}")
                elif plot_type == "Bar Chart":
                    ax.bar(df[x_col], df[y_col], color='#3b82f6')
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
                    plt.xticks(rotation=45)
                else:
                    ax.scatter(df[x_col], df[y_col], alpha=0.6, color='#ef4444')
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
                st.pyplot(fig)
            else:
                st.warning("Need at least two numeric columns for plotting. Displaying basic stats.")
                st.dataframe(df.describe())
        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.info("👈 Please upload a CSV or Excel file to begin.")
    
    if st.button("🏠 Back to Home", use_container_width=True):
        st.session_state["current_app"] = "home"
        st.rerun()