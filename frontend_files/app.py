import streamlit as st
import requests
import pandas as pd
import io

st.set_page_config(
    page_title="SuperKart Sales Forecasting Dashboard",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 SuperKart Sales Forecasting")
st.markdown("Welcome to the SuperKart Sales Forecasting dashboard. This UI communicates with our containerized Flask backend to run production predictions on our Tuned Champion Random Forest model.")

# Sidebar Navigation
option = st.sidebar.selectbox("Choose Prediction Mode:", ["Single Item Online Forecast", "Batch File Upload"])

# We assume our containers share a Docker network, meaning the frontend can reference the backend service name directly
BACKEND_URL = "http://backend:7860"

if option == "Single Item Online Forecast":
    st.header("📈 Single Item Sales Estimator")
    st.write("Adjust the product and store attributes below to retrieve a real-time sales forecast.")

    col1, col2 = st.columns(2)

    with col1:
        product_weight = st.slider("Product Weight (kg)", min_value=4.0, max_value=25.0, value=12.5, step=0.1)
        product_allocated_area = st.slider("Product Allocated Display Area Ratio", min_value=0.001, max_value=0.3, value=0.05, step=0.001)
        product_mrp = st.number_input("Product Maximum Retail Price ($)", min_value=10.0, max_value=300.0, value=147.0, step=1.0)
        product_sugar = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        product_category = st.selectbox("Product Category Type", ["Perishables", "Non Perishables"])

    with col2:
        store_age = st.number_input("Store Age (Years)", min_value=1, max_value=50, value=15, step=1)
        store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
        store_city = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
        store_type = st.selectbox("Store Type", ["Departmental Store", "Food Mart", "Supermarket Type1", "Supermarket Type2"])
        product_id_char = st.selectbox("Product Identifier (Group Char)", ["FD", "DR", "NC"])

    if st.button("Predict Forecasted Sales"):
        # Construct payload
        payload = {
            "Product_Weight": float(product_weight),
            "Product_Sugar_Content": product_sugar,
            "Product_Allocated_Area": float(product_allocated_area),
            "Product_MRP": float(product_mrp),
            "Store_Size": store_size,
            "Store_Location_City_Type": store_city,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": int(store_age),
            "Product_Type_Category": product_category
        }

        try:
            with st.spinner("Communicating with prediction engine..."):
                response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload)

            if response.status_code == 200:
                prediction_value = response.json()["prediction"]
                st.success(f"💰 Estimated Product Store Sales Total: **${prediction_value:,.2f}**")
            else:
                st.error(f"Error from API: {response.text}")
        except Exception as e:
            st.error(f"Could not reach prediction API backend. Details: {e}")

elif option == "Batch File Upload":
    st.header("📁 Bulk Batch Forecasts")
    st.write("Upload a structured `.csv` file to predict total sales over multiple stores and product items simultaneously.")

    uploaded_file = st.file_uploader("Choose a CSV file:", type=["csv"])

    if uploaded_file is not None:
        # Show preview
        df_preview = pd.read_csv(uploaded_file)
        st.write("### Uploaded Data Preview")
        st.dataframe(df_preview.head(5))

        # Prepare buffer for API dispatch
        uploaded_file.seek(0)
        files_payload = {"file": (uploaded_file.name, uploaded_file.read(), "text/csv")}

        if st.button("Run Batch Predictions"):
            try:
                with st.spinner("Generating batch forecasts..."):
                    response = requests.post(f"{BACKEND_URL}/v1/predictbatch", files=files_payload)

                if response.status_code == 200:
                    results = response.json()

                    # Map predictions back to preview dataframe
                    pred_list = [results[str(i)] for i in range(len(df_preview))]
                    df_preview["Predicted_Store_Sales_Total"] = pred_list

                    st.success("🎉 Forecasts completed successfully!")
                    st.dataframe(df_preview)
                else:
                    st.error(f"Error generating batch forecast: {response.text}")
            except Exception as e:
                st.error(f"Could not reach forecast engine. Details: {e}")
