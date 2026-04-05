# 🧪 Demo Test Accounts & Scenarios

## Quick Test Credentials

### Patient Accounts (Create via Registration)

**Test Patient 1:**
- Username: `patient1`
- Password: `test1234`
- Type: Patient

**Test Patient 2:**
- Username: `john_doe`
- Password: `demo5678`
- Type: Patient

### Doctor Accounts (Create via Registration)

**Test Doctor 1:**
- Username: `dr_smith`
- Password: `doctor123`
- Full Name: Dr. John Smith
- Email: dr.smith@hospital.com
- Phone: 555-0123

**Test Doctor 2:**
- Username: `dr_jones`
- Password: `cardio456`
- Full Name: Dr. Sarah Jones
- Email: dr.jones@cardiocenter.com
- Phone: 555-0456

---

## 🎯 Sample Prediction Scenarios

### Scenario 1: Low Risk Patient
**Patient Profile:**
- Age: 35
- Sex: Male (1)
- Chest Pain Type: Typical Angina (0)
- Blood Pressure: 120 mm Hg
- Cholesterol: 180 mg/dl
- Resting ECG: Normal (0)
- Max Heart Rate: 180
- Exercise Angina: No (0)
- ST Depression: 0.5
- Slope: Upsloping (0)
- Major Vessels: 0
- Thalassemia: Normal (0)

**Expected Result:** Low Risk (<30%)

---

### Scenario 2: Moderate Risk Patient
**Patient Profile:**
- Age: 55
- Sex: Male (1)
- Chest Pain Type: Atypical Angina (1)
- Blood Pressure: 140 mm Hg
- Cholesterol: 240 mg/dl
- Resting ECG: ST-T Abnormality (1)
- Max Heart Rate: 150
- Exercise Angina: No (0)
- ST Depression: 1.5
- Slope: Flat (1)
- Major Vessels: 1
- Thalassemia: Fixed Defect (1)

**Expected Result:** Moderate Risk (30-60%)

---

### Scenario 3: High Risk Patient
**Patient Profile:**
- Age: 65
- Sex: Male (1)
- Chest Pain Type: Non-anginal Pain (2)
- Blood Pressure: 160 mm Hg
- Cholesterol: 280 mg/dl
- Resting ECG: LV Hypertrophy (2)
- Max Heart Rate: 130
- Exercise Angina: Yes (1)
- ST Depression: 2.5
- Slope: Downsloping (2)
- Major Vessels: 2
- Thalassemia: Reversible Defect (2)

**Expected Result:** High Risk (>60%)

---

## 📋 Testing Checklist

### Registration Flow
- [ ] Register as Patient (simple form)
- [ ] Register as Doctor (extended form)
- [ ] Try duplicate username (should fail)
- [ ] Try short password (should fail)
- [ ] Verify error messages appear

### Login Flow
- [ ] Login with valid credentials
- [ ] Login with invalid credentials (should fail)
- [ ] Verify welcome message shows user name
- [ ] Check session persists across pages

### Patient Features
- [ ] Fill out prediction form completely
- [ ] View ECG visualization
- [ ] Submit prediction
- [ ] Verify risk score displays (0-100%)
- [ ] Check risk category appears (Low/Moderate/High)
- [ ] See color-coded results
- [ ] Read personalized recommendations
- [ ] Navigate to "My History"
- [ ] Verify prediction saved to history
- [ ] Make second prediction
- [ ] Check trend chart appears with multiple entries
- [ ] View Profile page
- [ ] Logout successfully

### Doctor Features
- [ ] Access Overview dashboard
- [ ] View key metrics (Total Patients, Avg Risk, High Risk Count)
- [ ] Check Recent Predictions table
- [ ] Navigate to "All Patients" tab
- [ ] Verify comprehensive patient list displays
- [ ] Use age filter sliders
- [ ] Confirm filtering works correctly
- [ ] Go to "Analytics" tab
- [ ] View Risk Distribution histogram
- [ ] Check Age Group Analysis bar chart
- [ ] Examine Correlation Heatmap
- [ ] Review Risk Factor Analysis statistics
- [ ] Visit "My Patients" tab
- [ ] Logout successfully

### PDF Report
- [ ] Complete a prediction
- [ ] Verify report generation message
- [ ] Download PDF report
- [ ] Open and review report contents:
  - Patient information section
  - Risk assessment with color coding
  - Medical recommendations
  - Health tips list
  - Disclaimer section
  - Professional formatting

### Database Verification
- [ ] Check database file created at `database/patients.db`
- [ ] Verify users table has registered accounts
- [ ] Confirm predictions table stores all parameters
- [ ] Check timestamps recorded correctly

### UI/UX Testing
- [ ] Verify responsive design on different screen sizes
- [ ] Test navigation sidebar functionality
- [ ] Check color scheme consistency
- [ ] Verify emoji indicators display
- [ ] Test collapsible sections (expand/collapse)
- [ ] Confirm charts render without errors
- [ ] Check tables are readable and formatted
- [ ] Verify buttons are clearly labeled

### Edge Cases
- [ ] Try entering extreme values (age > 120, BP > 250)
- [ ] Enter zero values where allowed
- [ ] Leave required fields empty
- [ ] Test with minimum valid inputs
- [ ] Verify graceful error handling

---

## 🎨 Visual Elements to Verify

### Color Coding
- 🟢 **Green** (#2a9d8f): Low risk, positive indicators
- 🟡 **Yellow** (#e9c46a): Moderate risk, caution
- 🔴 **Red** (#e76f51): High risk, urgent attention
- 🔵 **Blue** (#457b9d): Secondary branding, headers

### Icons & Emojis
- ❤️ Heart disease/health
- 🔐 Login/security
- 📝 Registration
- 👤 Patient profile
- 👨‍⚕️ Doctor
- 📊 Analytics/charts
- 🎯 Prediction button
- 📈 Results display
- ✅ Success indicators
- ⚠️ Warnings
- 🟢🟡🔴 Risk levels

---

## 📊 Expected Analytics Outputs

### For Doctor Dashboard (with sample data)

**With 10+ predictions:**
- Total Patients: Count of unique user IDs
- Average Risk Score: Mean of all risk scores × 100
- High Risk Cases: Count where risk > 60%

**Charts should show:**
1. **Risk Distribution**: Bell curve or skewed based on data
2. **Age Groups**: Typically shows increasing risk with age
3. **Correlations**: 
   - Positive: Age ↔ Risk, Oldpeak ↔ Risk
   - Negative: Thalach ↔ Risk
4. **Risk Factors**: High-risk group should show worse averages

---

## 🔒 Security Testing

### Authentication
- [ ] Passwords stored in database (plain text in demo, would be hashed in production)
- [ ] SQL injection prevention (try entering `' OR '1'='1`)
- [ ] Session management works (can't access dashboard without login)
- [ ] Logout clears session completely

### Input Validation
- [ ] Numeric fields accept only numbers
- [ ] Dropdown menus prevent invalid selections
- [ ] Required fields enforced
- [ ] Reasonable value ranges suggested

---

## 💾 Data Persistence Testing

1. **Create Account** → Logout → Login again → Account still exists ✓
2. **Make Prediction** → Logout → Login → Check History → Prediction saved ✓
3. **Register Patient** → Login as Doctor → View All Patients → New patient appears ✓
4. **Close Browser** → Reopen → Still logged in (session persistence) ✓
5. **Clear Cache/Cookies** → Must login again ✓

---

## 🌐 Browser Compatibility

Test in multiple browsers if possible:
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if available)

Verify:
- Charts render correctly
- Layout is consistent
- Interactive elements work
- Downloads function properly

---

## 📱 Responsive Design Testing

### Desktop (1920x1080)
- Multi-column layouts display properly
- Sidebar navigation visible
- All charts full size
- Tables show all columns

### Laptop (1366x768)
- Layout adjusts appropriately
- Content remains readable
- Navigation accessible

### Tablet (768x1024)
- Columns stack vertically
- Touch-friendly buttons
- Simplified navigation

---

## ⚠️ Known Limitations (Demo Version)

1. **Password Security**: Stored as plain text (production would hash)
2. **Email Verification**: Not implemented for doctor registration
3. **File Upload**: No photo uploads for profiles
4. **Real-time Updates**: Requires manual refresh
5. **Doctor-Patient Assignment**: Infrastructure exists but UI not fully implemented
6. **Appointment Scheduling**: Not included in current version
7. **Multi-language**: English only currently

---

## 🎯 Success Criteria

Your system is working correctly if:

✅ Users can register and login
✅ Patients can make predictions and see results
✅ Predictions are saved to history
✅ Doctors can view comprehensive analytics
✅ All charts and visualizations render
✅ PDF reports generate with professional formatting
✅ Navigation is intuitive and smooth
✅ Data persists across sessions
✅ Risk categorization is accurate (color-coded)
✅ Filtering and search functions work
✅ Logout clears session properly

---

## 🚀 Quick Demo Flow (5-Minute Walkthrough)

1. **Start App**: `streamlit run app.py`
2. **Register Patient**: Create account (30 seconds)
3. **Login**: Use credentials (10 seconds)
4. **Make Prediction**: Fill form and submit (2 minutes)
5. **View Results**: See risk score and category (30 seconds)
6. **Check History**: View saved prediction (20 seconds)
7. **Logout**: Click logout button (10 seconds)
8. **Register Doctor**: Create doctor account (1 minute)
9. **Login as Doctor**: Access dashboard (10 seconds)
10. **View Analytics**: Explore all tabs (2 minutes)
11. **Review Complete!** ✓

**Total Time**: ~8-10 minutes for full feature demo

---

## 📞 Support Information

If you encounter issues during testing:

1. **Check Console**: Look for Python errors in terminal
2. **Verify Dependencies**: Ensure all packages installed
3. **Database Issues**: Delete `patients.db` and restart
4. **Model Files**: Confirm `model.pkl` and `scaler.pkl` exist
5. **Port Conflicts**: Change port if 8502/8503 in use

---

**Happy Testing!** 🎉

For detailed documentation, see README.md and QUICKSTART.md
