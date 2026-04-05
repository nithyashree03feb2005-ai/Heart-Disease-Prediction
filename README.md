❤️ HeartCare Pro - Advanced Heart Disease Prediction System
A professional, user-friendly web application for predicting heart disease risk using machine learning and ECG analysis. Built with Streamlit for an intuitive interface and advanced analytics capabilities.

🌟 Key Features
For Patients 👤
Secure Registration & Login: Create personal accounts with profile management
Heart Disease Prediction: Advanced ML-based risk assessment with 13 clinical parameters
ECG Signal Analysis: Real-time ECG waveform generation and feature extraction
Risk Categorization:
🟢 Low Risk (<30%)
🟡 Moderate Risk (30-60%)
🔴 High Risk (>60%)
Medical History Tracking: View all past predictions with trend analysis
Comprehensive Medical Reports: Download detailed PDF reports with:
Patient information
Risk assessment with color-coded categories
Personalized recommendations
Cardiovascular health tips
Medical disclaimer
For Doctors 👨‍⚕️
Professional Dashboard: Comprehensive overview of patient data
Patient Management: View and manage all patient records
Advanced Analytics:
Risk score distribution histograms
Age group risk analysis
Correlation heatmaps for risk factors
Statistical comparisons between high/low risk groups
Filtering & Search: Filter patients by age, risk level, and other parameters
Data Export: Access complete patient prediction history
🎨 Unique Features
Modern, Professional UI

Clean, responsive design with custom CSS styling
Intuitive navigation and user flow
Color-coded risk indicators
Interactive visualizations
Dual User System

Separate interfaces for patients and doctors
Role-based access control
Secure authentication system
Advanced Visualizations

ECG signal waveforms
Risk trend charts over time
Distribution histograms
Correlation analysis heatmaps
Age group comparisons
Comprehensive Reporting

Professional PDF reports with medical formatting
Personalized health recommendations
Detailed parameter analysis
Preventive care guidelines
Historical Tracking

Complete prediction history for each patient
Risk progression visualization
Timestamp tracking
🚀 Getting Started
Prerequisites
Python 3.8 or higher
Virtual environment (recommended)
Installation
Clone or download the project

cd "D:\Heart Disease Prediction"
Activate virtual environment

.\.venv\Scripts\Activate.ps1
Install dependencies

pip install -r requirements.txt
Run the application

streamlit run app.py
Access the application

Open your browser and navigate to: http://localhost:8502
📋 Usage Guide
For Patients
Register a New Account

Click on "Register" tab
Select "Patient" as user type
Enter username and password (min 4 characters)
Complete registration
Login

Enter your username and password
Click "Login"
Make a Prediction

Navigate to "Prediction" section
Enter your medical parameters:
Age, Sex, Chest Pain Type
Blood Pressure, Cholesterol
ECG Results, Maximum Heart Rate
Exercise Angina, ST Depression
Slope, Major Vessels, Thalassemia
Review the simulated ECG signal
Click "Predict Risk"
View your results with risk category and recommendations
View History

Navigate to "My History"
See all your past predictions
View risk trend charts
Download Report

After prediction, receive personalized medical report
Includes risk factors, recommendations, and health tips
For Doctors
Register as Doctor

Select "Doctor" as user type
Provide full name, email, and phone number
Complete registration
Access Dashboard

Overview: See key metrics and recent predictions
All Patients: Browse complete patient database with filtering
Analytics: Advanced statistical analysis and visualizations
My Patients: View assigned patients (feature ready for expansion)
Analyze Data

Risk score distributions
Age-based risk stratification
Correlation analysis between risk factors
Compare high-risk vs low-risk patient characteristics
🗄️ Database Schema
The application uses SQLite with the following tables:

Users Table
User ID (Primary Key)
Username (Unique)
Password
User Type (Patient/Doctor)
Full Name, Email, Phone
Created At
Predictions Table
Prediction ID (Primary Key)
User ID (Foreign Key)
All medical parameters (13 features)
Risk Score
Prediction Date
Doctor-Patients Table
Assignment ID (Primary Key)
Doctor ID (Foreign Key)
Patient ID (Foreign Key)
Assignment Date
Notes
🧪 Technical Details
Machine Learning Model
Algorithm: Random Forest Classifier
Features: 18 input features (13 clinical + 5 engineered)
Output: Probability score (0-1) for heart disease risk
Preprocessing: StandardScaler for feature normalization
Feature Engineering
Cholesterol-to-Blood Pressure Ratio
Age Group Categorization
ECG Signal Features (4 extracted features)
Security
Password-protected authentication
Session-based login management
Input validation for registration
SQL injection prevention through parameterized queries
📊 Clinical Parameters
The prediction model uses the following clinically validated parameters:

Age - Patient's age in years
Sex - Male (1) or Female (0)
Chest Pain Type - 4 categories (0-3)
Resting Blood Pressure - mm Hg
Serum Cholesterol - mg/dl
Resting ECG - 3 categories (0-2)
Maximum Heart Rate - Achieved during exercise
Exercise Induced Angina - Yes (1) or No (0)
ST Depression - Oldpeak value
ST Slope - 3 categories (0-2)
Major Vessels - Number colored by fluoroscopy (0-4)
Thalassemia - 3 categories (0-2)
⚠️ Disclaimer
This application is for educational and research purposes only. It should NOT replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers for medical concerns.

🛠️ Technology Stack
Frontend: Streamlit
Backend: Python
Database: SQLite
Machine Learning: Scikit-learn (Random Forest)
Data Visualization: Matplotlib, Pandas
Report Generation: ReportLab
Signal Processing: NumPy
📁 Project Structure
Heart Disease Prediction/
├── app.py                  # Main Streamlit application
├── src/
│   ├── auth.py            # Authentication logic
│   ├── db.py              # Database operations
│   ├── ecg_features.py    # ECG signal generation & features
│   ├── train.py           # Model training script
│   └── report.py          # PDF report generation
├── models/
│   ├── model.pkl          # Trained Random Forest model
│   └── scaler.pkl         # Feature scaler
├── database/
│   └── patients.db        # SQLite database
├── Dataset/
│   └── heart_disease_data.csv  # Training dataset
└── requirements.txt       # Python dependencies
🔮 Future Enhancements
 Email notifications for high-risk predictions
 Doctor-patient assignment system
 Appointment scheduling
 Integration with electronic health records (EHR)
 Multi-language support
 Mobile application
 Telemedicine integration
 Advanced risk factor analysis with deep learning
 Genetic risk factors integration
 Lifestyle recommendation engine
👥 Support
For questions or issues, please refer to the in-application help section or contact the development team.

Developed with ❤️ for advancing cardiovascular health awareness

Last Updated: April 2026
