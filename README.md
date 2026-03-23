# customer-churn-prediction
# 📊 End-to-End Customer Churn Prediction System

### 🔗 [Live Demo Link](https://your-app-link.streamlit.app) 

## 🎯 Business Problem
Customer churn (attrition) is a major challenge for service-based companies. Retaining an existing customer is **5x cheaper** than acquiring a new one. This project provides a data-driven solution to identify high-risk customers before they leave, allowing businesses to take proactive retention actions.

## 🚀 Key Features
- **Individual Prediction**: Real-time churn risk assessment for single customers via an interactive form.
- **Bulk CSV Processing**: Upload a list of thousands of customers to get instant batch predictions.
- **Live Analytics Dashboard**: Integrated Plotly visualizations showing churn trends by contract type, gender, and charges.
- **Automated Logging**: Every prediction is automatically stored in a **SQLite3 database** for long-term tracking and Power BI integration.

## 🛠️ Tech Stack
- **Language**: Python 3.13
- **Machine Learning**: Scikit-Learn (XGBoost/Random Forest), NumPy, Pandas
- **Web Framework**: Streamlit
- **Database**: SQLite3
- **Visualization**: Plotly Express
- **Deployment**: GitHub & Streamlit Community Cloud

## 📂 Project Structure
```text
├── app.py              # Main Streamlit application code
├── models/             # Trained Model and Scaler files (.pkl)
│   ├── model.pkl
│   └── scaler.pkl
├── requirements.txt    # List of Python dependencies
└── README.md           # Project documentation
