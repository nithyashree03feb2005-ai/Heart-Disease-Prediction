import sys
sys.path.append("src")

import streamlit as st
import numpy as np
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from ecg_features import get_ecg, extract_features
from db import init_db, insert_prediction, get_user_predictions, fetch_all_predictions, get_all_users_by_type
from auth import authenticate, register, validate_user_data
from report import generate_pdf

# Initialize database
init_db()

# Load models
try:
    model = pickle.load(open('models/model.pkl','rb'))
    scaler = pickle.load(open('models/scaler.pkl','rb'))
except:
    st.error("Model files not found. Please ensure model.pkl and scaler.pkl exist in the models folder.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="HeartCare Pro - Heart Disease Prediction System",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #e63946;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #457b9d;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .risk-low {
        color: #2a9d8f;
        font-weight: bold;
    }
    .risk-moderate {
        color: #e9c46a;
        font-weight: bold;
    }
    .risk-high {
        color: #e76f51;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'show_register' not in st.session_state:
    st.session_state.show_register = False

def logout():
    st.session_state.logged_in = False
    st.session_state.user_data = None
    st.session_state.page = 'login'
    st.session_state.show_register = False
    st.rerun()

def show_auth_page():
    """Display login and registration forms with improved UI"""
    
    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Header with logo/title
        st.markdown("""
            <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 15px; color: white; margin-bottom: 2rem;'>
                <h1 style='margin: 0; font-size: 2.5rem;'>❤️ HeartCare Pro</h1>
                <p style='margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem;'>Advanced Heart Disease Prediction System</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Tab-based navigation
        if not st.session_state.show_register:
            # LOGIN FORM
            st.markdown("<h2 style='color: #e63946; text-align: center;'>🔐 User Login</h2>", unsafe_allow_html=True)
            
            with st.form(key="login_form", clear_on_submit=False):
                login_username = st.text_input("Username", placeholder="Enter your username")
                login_password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    login_button = st.form_submit_button("Login", width='stretch')
                with col_btn2:
                    register_redirect = st.form_submit_button("Register →", width='stretch')
                
                if login_button:
                    if not login_username or not login_password:
                        st.error("❌ Please enter both username and password")
                    else:
                        user = authenticate(login_username, login_password)
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.user_data = {
                                'id': user[0],
                                'username': user[1],
                                'user_type': user[2],
                                'full_name': user[3],
                                'email': user[4]
                            }
                            st.success(f"✅ Welcome back, {user[3] or user[1]}!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                
                if register_redirect:
                    st.session_state.show_register = True
                    st.rerun()
        
        else:
            # REGISTRATION FORM
            st.markdown("<h2 style='color: #457b9d; text-align: center;'>📝 Create Account</h2>", unsafe_allow_html=True)
            
            with st.form(key="register_form", clear_on_submit=True):
                reg_username = st.text_input("Username *", placeholder="Choose a unique username")
                reg_password = st.text_input("Password *", type="password", placeholder="Minimum 4 characters")
                reg_user_type = st.selectbox("Register as:", ["Patient", "Doctor"])
                
                # Additional fields for doctors
                if reg_user_type == "Doctor":
                    reg_full_name = st.text_input("Full Name *", placeholder="Dr. John Smith")
                    reg_email = st.text_input("Email Address *", placeholder="doctor@hospital.com")
                    reg_phone = st.text_input("Phone Number *", placeholder="+1 (555) 123-4567")
                else:
                    reg_full_name = st.text_input("Full Name (Optional)", placeholder="Your name")
                    reg_email = st.text_input("Email Address (Optional)", placeholder="your@email.com")
                    reg_phone = st.text_input("Phone Number (Optional)", placeholder="+1 (555) 123-4567")
                
                col_reg1, col_reg2 = st.columns(2)
                with col_reg1:
                    register_button = st.form_submit_button("Create Account", width='stretch', type="primary")
                with col_reg2:
                    back_to_login = st.form_submit_button("← Back to Login", width='stretch')
                
                if register_button:
                    if not reg_username or not reg_password:
                        st.error("❌ Username and password are required")
                    elif len(reg_password) < 4:
                        st.error("❌ Password must be at least 4 characters long")
                    else:
                        success, message = register(
                            reg_username, 
                            reg_password, 
                            reg_user_type.lower(),
                            reg_full_name if reg_full_name else '',
                            reg_email if reg_email else '',
                            reg_phone if reg_phone else ''
                        )
                        
                        if success:
                            st.success(f"✅ {message}! Please login now.")
                            st.info("Redirecting to login page...")
                            st.session_state.show_register = False
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                
                if back_to_login:
                    st.session_state.show_register = False
                    st.rerun()
        
        # Footer
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center; color: #666; font-size: 0.9rem;'>
                <p>🔒 Secure & Confidential | For Medical Education Only</p>
                <p><i>This system should not replace professional medical advice</i></p>
            </div>
        """, unsafe_allow_html=True)

def get_risk_category(risk_score):
    """Categorize risk level"""
    if risk_score < 0.3:
        return "Low Risk", "🟢"
    elif risk_score < 0.6:
        return "Moderate Risk", "🟡"
    else:
        return "High Risk", "🔴"

def patient_dashboard():
    """Patient dashboard with prediction and history"""
    user = st.session_state.user_data
    
    # Welcome message - Fixed display with proper rendering
    full_name = user.get('full_name', '') or user.get('username', 'User')
    st.markdown(f"<h1 class='main-header'>❤️ HeartCare Pro</h1>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; margin-bottom: 2rem;'><h3 style='color: #457b9d;'>Welcome, {full_name}</h3></div>", unsafe_allow_html=True)
    
    # Navigation
    nav_options = ["Prediction", "My History", "Profile"]
    choice = st.sidebar.selectbox("Navigation", nav_options)
    
    if choice == "Prediction":
        st.markdown("<h2 class='sub-header'>🔍 Heart Disease Prediction</h2>", unsafe_allow_html=True)
        
        # Create two columns for better layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Medical Parameters")
            age = st.number_input("Age (years)", min_value=1, max_value=120, value=45)
            sex = st.selectbox("Sex", ["Male", "Female"])
            sex_val = 1 if sex == "Male" else 0
            
            cp = st.selectbox("Chest Pain Type", [
                "Typical Angina",
                "Atypical Angina",
                "Non-anginal Pain",
                "Asymptomatic"
            ])
            cp_val = ["Typical Angina", "Atypical Angina", "Non-anginal Pain", "Asymptomatic"].index(cp)
            
            trestbps = st.number_input("Resting Blood Pressure (mm Hg)", min_value=50, max_value=250, value=120)
            chol = st.number_input("Serum Cholesterol (mg/dl)", min_value=50, max_value=500, value=200)
            
            fbs = st.selectbox("Fasting Blood Sugar > 120 mg/dl", ["False", "True"])
            fbs_val = 1 if fbs == "True" else 0
            
            restecg = st.selectbox("Resting ECG Results", [
                "Normal",
                "ST-T Wave Abnormality",
                "Left Ventricular Hypertrophy"
            ])
            restecg_val = ["Normal", "ST-T Wave Abnormality", "Left Ventricular Hypertrophy"].index(restecg)
        
        with col2:
            st.subheader("Additional Parameters")
            thalach = st.number_input("Maximum Heart Rate Achieved", min_value=50, max_value=250, value=150)
            exang = st.selectbox("Exercise Induced Angina", ["No", "Yes"])
            exang_val = 0 if exang == "No" else 1
            
            oldpeak = st.number_input("ST Depression (Oldpeak)", min_value=0.0, max_value=10.0, value=1.0)
            slope = st.selectbox("Slope of Peak Exercise ST Segment", [
                "Upsloping",
                "Flat",
                "Downsloping"
            ])
            slope_val = ["Upsloping", "Flat", "Downsloping"].index(slope)
            
            ca = st.number_input("Number of Major Vessels Colored by Fluoroscopy", min_value=0, max_value=4, value=0)
            thal = st.selectbox("Thalassemia", [
                "Normal",
                "Fixed Defect",
                "Reversible Defect"
            ])
            thal_val = ["Normal", "Fixed Defect", "Reversible Defect"].index(thal)
        
        # Feature engineering
        chol_bp_ratio = chol / trestbps if trestbps != 0 else 0
        age_group = 0 if age < 40 else (1 if age < 60 else 2)
        
        # Prepare data for prediction (15 features matching the trained model)
        # Features: age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal + 2 engineered
        data_dict = {
            'age': [age], 'sex': [sex_val], 'cp': [cp_val], 'trestbps': [trestbps], 
            'chol': [chol], 'fbs': [fbs_val], 'restecg': [restecg_val], 'thalach': [thalach],
            'exang': [exang_val], 'oldpeak': [oldpeak], 'slope': [slope_val], 'ca': [ca], 
            'thal': [thal_val], 'chol_bp_ratio': [chol_bp_ratio], 'age_group': [age_group]
        }
        data_df = pd.DataFrame(data_dict)
        
        # Prediction button first
        if st.button("🎯 Predict Risk", width='stretch'):
            data_scaled = scaler.transform(data_df)
            prob = model.predict_proba(data_scaled)[0][1]
            
            # Display results
            st.markdown("---")
            st.markdown("<h2 style='text-align: center; color: #e63946;'>📈 Prediction Results</h2>", unsafe_allow_html=True)
            
            col_result1, col_result2, col_result3 = st.columns(3)
            
            risk_category, risk_icon = get_risk_category(prob)
            
            with col_result1:
                st.markdown(f"""
                    <div class='metric-card'>
                        <h3>Risk Score</h3>
                        <h1>{round(prob*100, 2)}%</h1>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_result2:
                st.markdown(f"""
                    <div style='background: white; padding: 1rem; border-radius: 10px; text-align: center; border: 2px solid {"#e76f51" if prob > 0.6 else "#2a9d8f"}'>
                        <h3>Category</h3>
                        <h2>{risk_icon} {risk_category}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_result3:
                st.markdown(f"""
                    <div style='background: white; padding: 1rem; border-radius: 10px; text-align: center;'>
                        <h3>Recommendation</h3>
                        <p>{'⚠️ Consult a doctor immediately' if prob > 0.6 else '✅ Maintain healthy lifestyle' if prob < 0.3 else '⚖️ Monitor regularly'}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Save prediction to database
            prediction_data = {
                'age': age, 'sex': sex_val, 'cp': cp_val, 'trestbps': trestbps,
                'chol': chol, 'fbs': fbs_val, 'restecg': restecg_val, 'thalach': thalach,
                'exang': exang_val, 'oldpeak': oldpeak, 'slope': slope_val,
                'ca': ca, 'thal': thal_val, 'chol_bp_ratio': chol_bp_ratio,
                'age_group': age_group, 'risk_score': prob
            }
            
            insert_prediction(user['id'], prediction_data)
            st.success("✅ Prediction saved to your medical history!")
            
            # Generate and offer PDF report
            try:
                # Get patient name from user data
                patient_name = user.get('full_name', '') or user.get('username', 'Patient')
                
                additional_info = {
                    'sex': sex_val,
                    'bp': trestbps,
                    'chol': chol,
                    'fbs': fbs_val,
                    'cp': cp,
                    'restecg': restecg,
                    'thalach': thalach  # Add heart rate for charts
                }
                pdf_file = generate_pdf(age, prob, patient_name, additional_info)
                
                with open(pdf_file, "rb") as pdf:
                    st.download_button(
                        label="📄 Download Medical Report (PDF)",
                        data=pdf.read(),
                        file_name=f"HeartCare_Report_{patient_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception as e:
                st.warning(f"Could not generate PDF: {str(e)}")
            
            # ECG Signal Analysis - AFTER prediction
            st.markdown("---")
            st.subheader("📊 ECG Signal Analysis")
            
            try:
                signal = get_ecg()
                feats = extract_features(signal)
                
                fig_ecg, ax_ecg = plt.subplots(figsize=(12, 4))
                ax_ecg.plot(signal, linewidth=0.8, color='#e63946')
                ax_ecg.set_title('Simulated ECG Waveform', fontsize=14, fontweight='bold')
                ax_ecg.set_xlabel('Time (ms)')
                ax_ecg.set_ylabel('Voltage (mV)')
                ax_ecg.grid(True, alpha=0.3, linestyle='--')
                ax_ecg.set_facecolor('#f8f9fa')
                fig_ecg.patch.set_facecolor('white')
                plt.tight_layout()
                st.pyplot(fig_ecg, width='stretch')
                plt.close(fig_ecg)
            except Exception as e:
                st.error(f"ECG visualization error: {str(e)}")
            
            # Add Risk Comparison Charts (Dynamic based on actual values)
            st.markdown("---")
            st.subheader("📊 Cardiovascular Risk Analysis")
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Risk Level Gauge Chart - Dynamic based on actual risk score
                fig_gauge, ax_gauge = plt.subplots(figsize=(5, 5))
                
                # Create gauge-like visualization showing risk position
                categories = ['Low Risk\n(0-30%)', 'Moderate Risk\n(30-60%)', 'High Risk\n(60%+)']
                colors_gauge = ['#2a9d8f', '#e9c46a', '#e76f51']
                
                # Create semi-circle gauge
                wedges, texts = ax_gauge.pie(
                    [0.3, 0.3, 0.4],
                    colors=colors_gauge,
                    startangle=90,
                    counterclock=False,
                    wedgeprops=dict(width=0.4)
                )
                
                # Add your risk indicator needle pointing to exact position
                risk_angle = 90 + (prob * 360)
                ax_gauge.plot([0.3 * np.cos(np.radians(risk_angle)), 
                              0.5 * np.cos(np.radians(risk_angle))], 
                             [0.3 * np.sin(np.radians(risk_angle)), 
                              0.5 * np.sin(np.radians(risk_angle))], 
                             'r-', linewidth=4, marker='o', markersize=12, zorder=10)
                
                ax_gauge.set_title(f'Your Risk Position\n{prob*100:.1f}%', 
                                 fontsize=12, fontweight='bold', pad=20, color='#1d3557')
                ax_gauge.axis('equal')
                plt.tight_layout()
                st.pyplot(fig_gauge, width='stretch')
                plt.close(fig_gauge)
            
            with col_chart2:
                # Risk Factor Contribution Chart - Based on ACTUAL clinical values
                fig_bar, ax_bar = plt.subplots(figsize=(5, 5))
                
                # Calculate relative contributions based on actual patient data
                # Higher values = higher contribution to risk
                age_factor = min(age / 100, 1.0) * 25
                bp_factor = min(max((trestbps - 90) / 100, 0), 1.0) * 20
                chol_factor = min(max((chol - 100) / 200, 0), 1.0) * 20
                fbs_factor = fbs_val * 15  # Binary: 0 or 15
                ecg_factor = (restecg_val / 2) * 20  # 0, 1, or 2 scaled
                hr_factor = min((thalach - 100) / 100, 1.0) * 15 if thalach > 100 else 5
                
                factors = ['Age', 'Blood Pressure', 'Cholesterol', 
                          'Blood Sugar', 'ECG Results', 'Heart Rate']
                raw_contributions = [age_factor, bp_factor, chol_factor, 
                                   fbs_factor, ecg_factor, hr_factor]
                
                # Normalize to sum to risk percentage
                total_contrib = sum(raw_contributions)
                if total_contrib > 0:
                    contributions = [(c / total_contrib) * prob * 100 for c in raw_contributions]
                else:
                    contributions = [prob * 100 / 6] * 6  # Equal distribution if no factors
                
                # Color bars based on contribution level
                bar_colors = []
                for contrib in contributions:
                    if contrib > 20:
                        bar_colors.append('#e76f51')  # Red - high contribution
                    elif contrib > 10:
                        bar_colors.append('#e9c46a')  # Yellow - moderate
                    else:
                        bar_colors.append('#2a9d8f')  # Green - low
                
                bars = ax_bar.barh(factors, contributions, color=bar_colors)
                ax_bar.set_xlabel('Contribution to Risk (%)', fontsize=9, fontweight='bold')
                ax_bar.set_title('Risk Factor Analysis (Based on Your Data)', 
                               fontsize=11, fontweight='bold', color='#1d3557')
                ax_bar.grid(axis='x', alpha=0.3, linestyle='--')
                max_contribution = max(contributions) if contributions else 20
                ax_bar.set_xlim([0, min(max(prob*100 + 10, max_contribution + 10), 100)])
                
                # Add value labels on bars
                for bar, val in zip(bars, contributions):
                    if val > 1:  # Only show if significant
                        ax_bar.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                                   f'{val:.1f}%', va='center', fontsize=8, fontweight='bold', color='#1d3557')
                
                plt.tight_layout()
                st.pyplot(fig_bar, width='stretch')
                plt.close(fig_bar)
            
            # Detailed analysis
            with st.expander("📋 Detailed Analysis Report"):
                st.write("**Your Input Parameters:**")
                
                # Create mapping for clean display values
                cp_display = {"Typical Angina": "Typical Angina", 
                             "Atypical Angina": "Atypical Angina", 
                             "Non-anginal Pain": "Non-anginal Pain", 
                             "Asymptomatic": "Asymptomatic"}
                
                restecg_display = {0: "Normal", 1: "ST-T Wave Abnormality", 2: "Left Ventricular Hypertrophy"}
                slope_display = {0: "Upsloping", 1: "Flat", 2: "Downsloping"}
                thal_display = {0: "Normal", 1: "Fixed Defect", 2: "Reversible Defect"}
                
                params_df = pd.DataFrame({
                    'Parameter': ['Age', 'Sex', 'Chest Pain Type', 'Blood Pressure', 'Cholesterol',
                                'Fasting Blood Sugar', 'ECG Results', 'Max Heart Rate', 'Exercise Angina', 
                                'ST Depression', 'ST Slope', 'Major Vessels', 'Thalassemia'],
                    'Value': [str(age), str(sex), str(cp), f"{trestbps} mm Hg", f"{chol} mg/dl",
                             "Yes" if fbs_val == 1 else "No", restecg_display[restecg_val], str(thalach),
                             "Yes" if exang_val == 1 else "No", str(oldpeak), slope_display[slope_val],
                             str(ca), thal_display[thal_val]]
                })
                st.dataframe(params_df, hide_index=True, width='stretch')
                
                st.write("**Risk Factors:**")
                if prob > 0.6:
                    st.warning("🔴 High Risk - Multiple factors may be contributing")
                elif prob > 0.3:
                    st.warning("🟡 Moderate Risk - Some factors need attention")
                else:
                    st.success("🟢 Low Risk - Good cardiovascular health indicators")
    
    elif choice == "My History":
        st.markdown("<h2 class='sub-header'>📋 My Medical History</h2>", unsafe_allow_html=True)
        
        predictions = get_user_predictions(user['id'])
        
        if predictions:
            # Display prediction history
            df_cols = ["Date", "Age", "BP", "Chol", "Risk Score", "Category"]
            history_data = []
            
            for pred in predictions:
                date = pred[15] if len(pred) > 15 else "N/A"
                risk_cat, _ = get_risk_category(pred[14])
                history_data.append([
                    date[:10] if isinstance(date, str) else date,
                    pred[2], pred[6], pred[5], f"{pred[14]*100:.2f}%", risk_cat
                ])
            
            history_df = pd.DataFrame(history_data, columns=df_cols)
            st.dataframe(history_df, width='stretch', hide_index=True)
            
            # Risk trend visualization
            if len(predictions) > 1:
                st.subheader("📈 Risk Trend Over Time")
                fig, ax = plt.subplots(figsize=(10, 5))
                dates = range(len(predictions))
                risks = [p[14]*100 for p in predictions[::-1]]  # Reverse for chronological order
                ax.plot(dates, risks, marker='o', linewidth=2, markersize=8, color='#e63946')
                ax.set_xlabel('Prediction Number')
                ax.set_ylabel('Risk Score (%)')
                ax.set_title('Your Heart Disease Risk Trend')
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
        else:
            st.info("📝 No predictions yet. Start by making your first prediction!")
    
    elif choice == "Profile":
        st.markdown("<h2 class='sub-header'>👤 My Profile</h2>", unsafe_allow_html=True)
        
        st.write(f"**Username:** {user['username']}")
        st.write(f"**Account Type:** Patient")
        if user['full_name']:
            st.write(f"**Full Name:** {user['full_name']}")
        if user['email']:
            st.write(f"**Email:** {user['email']}")
        
        st.write(f"**Member Since:** {datetime.now().strftime('%Y-%m-%d')}")

def doctor_dashboard():
    """Doctor dashboard with analytics and patient management"""
    user = st.session_state.user_data
    
    st.markdown(f"<h1 class='main-header'>👨‍⚕️ Doctor Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3>Dr. {user['full_name'] or user['username']}</h3>")
    
    # Navigation
    nav_options = ["Overview", "All Patients", "Analytics", "My Patients"]
    choice = st.sidebar.selectbox("Navigation", nav_options)
    
    if choice == "Overview":
        st.markdown("<h2 class='sub-header'>📊 Hospital Overview</h2>", unsafe_allow_html=True)
        
        # Get all predictions
        all_predictions = fetch_all_predictions()
        
        if all_predictions:
            # Key metrics
            total_patients = len(set([p[1] for p in all_predictions if p[1]]))
            avg_risk = np.mean([p[14] for p in all_predictions]) * 100
            high_risk_count = sum([1 for p in all_predictions if p[14] > 0.6])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Patients", total_patients)
            with col2:
                st.metric("Average Risk Score", f"{avg_risk:.2f}%")
            with col3:
                st.metric("High Risk Cases", high_risk_count)
            
            # Recent predictions table
            st.markdown("---")
            st.subheader("📋 Recent Predictions")
            
            recent_data = []
            for pred in all_predictions[:10]:  # Show last 10
                patient_name = pred[16] if len(pred) > 16 and pred[16] else pred[17]
                recent_data.append({
                    'Patient': patient_name or 'Anonymous',
                    'Age': pred[2],
                    'BP': pred[6],
                    'Cholesterol': pred[5],
                    'Risk': f"{pred[14]*100:.2f}%"
                })
            
            recent_df = pd.DataFrame(recent_data)
            st.dataframe(recent_df, width='stretch', hide_index=True)
        else:
            st.info("No patient data available yet")
    
    elif choice == "All Patients":
        st.markdown("<h2 class='sub-header'>🏥 All Patient Records</h2>", unsafe_allow_html=True)
        
        all_predictions = fetch_all_predictions()
        
        if all_predictions:
            # Create comprehensive dataframe
            patient_data = []
            for pred in all_predictions:
                patient_name = pred[16] if len(pred) > 16 and pred[16] else (pred[17] if len(pred) > 17 else 'Anonymous')
                risk_cat, _ = get_risk_category(pred[14])
                
                patient_data.append({
                    'Patient': patient_name,
                    'Age': pred[2],
                    'Sex': 'M' if pred[3] == 1 else 'F',
                    'BP': pred[6],
                    'Cholesterol': pred[5],
                    'Max HR': pred[8],
                    'Risk Score': f"{pred[14]*100:.2f}%",
                    'Category': risk_cat,
                    'Date': str(pred[15])[:10] if len(pred) > 15 and pred[15] else 'N/A'
                })
            
            df = pd.DataFrame(patient_data)
            st.dataframe(df, width='stretch', hide_index=True)
            
            # Filter options
            st.subheader("🔍 Filter Patients")
            col1, col2 = st.columns(2)
            with col1:
                min_age = st.slider("Min Age", 0, 100, 0)
            with col2:
                max_age = st.slider("Max Age", 0, 100, 100)
            
            filtered_df = df[(df['Age'] >= min_age) & (df['Age'] <= max_age)]
            st.write(f"Showing {len(filtered_df)} patients aged {min_age}-{max_age}")
            st.dataframe(filtered_df, width='stretch', hide_index=True)
    
    elif choice == "Analytics":
        st.markdown("<h2 class='sub-header'>📈 Advanced Analytics</h2>", unsafe_allow_html=True)
        
        all_predictions = fetch_all_predictions()
        
        if all_predictions:
            # Convert to dataframe for analysis
            df = pd.DataFrame(all_predictions, columns=[
                'id', 'user_id', 'age', 'sex', 'cp', 'trestbps', 'chol', 'restecg',
                'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'chol_bp_ratio',
                'age_group', 'risk_score', 'date', 'name', 'username'
            ])
            
            # Distribution of risk scores
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Risk Score Distribution")
                fig1, ax1 = plt.subplots(figsize=(8, 5))
                ax1.hist(df['risk_score']*100, bins=20, color='#e63946', alpha=0.7, edgecolor='black')
                ax1.set_xlabel('Risk Score (%)')
                ax1.set_ylabel('Number of Patients')
                ax1.set_title('Distribution of Heart Disease Risk')
                ax1.grid(True, alpha=0.3)
                st.pyplot(fig1)
            
            with col2:
                st.subheader("Risk by Age Group")
                fig2, ax2 = plt.subplots(figsize=(8, 5))
                age_groups = df.groupby('age_group')['risk_score'].mean() * 100
                bars = ax2.bar(['<40', '40-60', '>60'], age_groups.values, color=['#2a9d8f', '#e9c46a', '#e76f51'])
                ax2.set_xlabel('Age Group')
                ax2.set_ylabel('Average Risk Score (%)')
                ax2.set_title('Heart Disease Risk by Age Group')
                ax2.grid(True, alpha=0.3)
                st.pyplot(fig2)
            
            # Correlation analysis
            st.subheader("🔬 Correlation Analysis")
            corr_cols = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'risk_score']
            corr_df = df[corr_cols]
            corr_matrix = corr_df.corr()
            
            fig3, ax3 = plt.subplots(figsize=(10, 8))
            im = ax3.imshow(corr_matrix, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)
            plt.colorbar(im, ax=ax3)
            ax3.set_xticks(range(len(corr_cols)))
            ax3.set_yticks(range(len(corr_cols)))
            ax3.set_xticklabels(corr_cols, rotation=45)
            ax3.set_yticklabels(corr_cols)
            ax3.set_title('Feature Correlation with Risk Score')
            
            # Add correlation values
            for i in range(len(corr_cols)):
                for j in range(len(corr_cols)):
                    text = ax3.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}', ha="center", va="center", color="black")
            
            st.pyplot(fig3)
            
            # Risk factors analysis
            st.subheader("⚠️ Risk Factor Analysis")
            high_risk = df[df['risk_score'] > 0.6]
            low_risk = df[df['risk_score'] < 0.3]
            
            if len(high_risk) > 0 and len(low_risk) > 0:
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**High Risk Patients (>60%)**")
                    st.write(f"Count: {len(high_risk)}")
                    st.write(f"Avg Age: {high_risk['age'].mean():.1f}")
                    st.write(f"Avg Cholesterol: {high_risk['chol'].mean():.1f} mg/dl")
                    st.write(f"Avg BP: {high_risk['trestbps'].mean():.1f} mm Hg")
                with col2:
                    st.write("**Low Risk Patients (<30%)**")
                    st.write(f"Count: {len(low_risk)}")
                    st.write(f"Avg Age: {low_risk['age'].mean():.1f}")
                    st.write(f"Avg Cholesterol: {low_risk['chol'].mean():.1f} mg/dl")
                    st.write(f"Avg BP: {low_risk['trestbps'].mean():.1f} mm Hg")
    
    elif choice == "My Patients":
        st.markdown("<h2 class='sub-header'>👥 My Assigned Patients</h2>", unsafe_allow_html=True)
        
        # For now, show all patients (in a real system, this would be filtered by doctor assignment)
        all_patients = get_all_users_by_type('patient')
        
        if all_patients:
            patients_df = pd.DataFrame(all_patients, columns=['ID', 'Username', 'Name', 'Email', 'Joined'])
            st.dataframe(patients_df, width='stretch', hide_index=True)
        else:
            st.info("No patients assigned yet")

# Main application flow
if not st.session_state.logged_in:
    # Show login/registration page
    show_auth_page()
else:
    # Show appropriate dashboard based on user type
    if st.session_state.user_data['user_type'] == 'patient':
        patient_dashboard()
    else:
        doctor_dashboard()
    
    # Logout button in sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        logout()