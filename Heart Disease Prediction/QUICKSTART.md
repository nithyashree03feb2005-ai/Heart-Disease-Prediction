# 🚀 Quick Start Guide - HeartCare Pro

## First Time Setup

### 1. Start the Application
```powershell
cd "D:\Heart Disease Prediction"
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

### 2. Access the App
Open your browser to: **http://localhost:8502**

---

## 📝 Creating Your First Account

### As a Patient:
1. On the login page, click the **"Register"** tab on the right
2. Fill in:
   - Username (choose any unique name)
   - Password (minimum 4 characters)
   - Select "Patient" as user type
3. Click **"Register"**
4. You'll be redirected to login - use your credentials to login

### As a Doctor:
1. On the login page, click the **"Register"** tab
2. Fill in:
   - Username
   - Password (minimum 4 characters)
   - Select "Doctor" as user type
   - Full Name (required)
   - Email (required)
   - Phone Number (required)
3. Click **"Register"**
4. Login with your credentials

---

## 🩺 Patient Features - How to Use

### Making Your First Prediction:

1. **Login** with your patient account
2. Navigate to **"Prediction"** from the sidebar
3. Fill in your medical information:
   - Basic info: Age, Sex
   - Chest Pain Type (select from dropdown)
   - Blood Pressure & Cholesterol levels
   - ECG Results
   - Additional cardiac parameters
4. View your **ECG Signal** visualization
5. Click **"🎯 Predict Risk"**
6. Review your results:
   - **Risk Score** (percentage)
   - **Risk Category** (Low/Moderate/High)
   - **Recommendations**

### Viewing Your History:

1. Click **"My History"** in the sidebar
2. See all your past predictions in a table
3. View the **Risk Trend Chart** showing changes over time

### Understanding Your Risk:

- **🟢 Low Risk (0-30%)**: Healthy cardiovascular indicators
- **🟡 Moderate Risk (30-60%)**: Some factors need attention
- **🔴 High Risk (60%+)**: Consult a healthcare provider

---

## 👨‍⚕️ Doctor Features - How to Use

### Accessing the Dashboard:

1. **Login** with your doctor account
2. You'll see the **Doctor Dashboard** automatically

### Overview Tab:
- **Total Patients**: Number of unique patients
- **Average Risk Score**: Across all predictions
- **High Risk Cases**: Count of high-risk predictions
- **Recent Predictions**: Last 10 patient records

### All Patients Tab:
- Complete list of all patient predictions
- Filter by age range using sliders
- Export data for analysis

### Analytics Tab:
Advanced visualizations including:
- **Risk Distribution**: Histogram showing risk score spread
- **Age Group Analysis**: Risk comparison across age groups
- **Correlation Heatmap**: Relationships between risk factors
- **Risk Factor Analysis**: Statistical comparisons

---

## 💡 Tips for Best Results

### For Accurate Predictions:
1. Enter accurate, recent medical measurements
2. Use consistent units (mm Hg for BP, mg/dl for cholesterol)
3. If unsure about any parameter, consult your doctor
4. Save predictions to track changes over time

### For Doctors:
1. Use filters to focus on specific patient groups
2. Check correlation analysis to understand key risk factors
3. Compare high-risk vs low-risk patient characteristics
4. Export data for research purposes

---

## 🔐 Security Best Practices

- Choose a strong, unique password
- Don't share your login credentials
- Logout when finished (use the Logout button in sidebar)
- Keep your personal information updated

---

## 📊 Understanding the Medical Parameters

### Essential Parameters:
- **Chest Pain Type**: 
  - 0: Typical Angina
  - 1: Atypical Angina
  - 2: Non-anginal Pain
  - 3: Asymptomatic

- **Resting ECG**:
  - 0: Normal
  - 1: ST-T Wave Abnormality
  - 2: Left Ventricular Hypertrophy

- **ST Slope**:
  - 0: Upsloping
  - 1: Flat
  - 2: Downsloping

- **Thalassemia**:
  - 0: Normal
  - 1: Fixed Defect
  - 2: Reversible Defect

---

## ❓ Troubleshooting

### Can't Login?
- Verify username and password are correct
- Check for extra spaces
- Ensure Caps Lock is off
- Try registering again if you forgot credentials

### Model Files Not Found?
- Make sure you're running from the correct directory
- Verify that `models/model.pkl` and `models/scaler.pkl` exist

### Database Errors?
- The database is created automatically on first run
- Located at `database/patients.db`
- Don't manually edit the database file

---

## 📞 Need Help?

- Check the main README.md for detailed documentation
- Review the in-app help sections
- Contact your system administrator for technical support

---

**Remember**: This tool is for educational purposes and should not replace professional medical advice!
