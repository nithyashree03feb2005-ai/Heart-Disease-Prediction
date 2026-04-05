from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import matplotlib.pyplot as plt
import io

def generate_risk_gauge_chart(risk_percentage):
    """Generate risk gauge chart as image"""
    fig, ax = plt.subplots(figsize=(4, 4), dpi=150)
    
    # Create donut chart
    categories = ['Low\n(0-30%)', 'Moderate\n(30-60%)', 'High\n(60%+)']
    colors_gauge = ['#2a9d8f', '#e9c46a', '#e76f51']
    
    wedges, texts = ax.pie(
        [0.3, 0.3, 0.4],
        colors=colors_gauge,
        startangle=90,
        counterclock=False,
        wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
    )
    
    # Add needle
    import numpy as np
    risk_angle = 90 + (risk_percentage / 100 * 360)
    ax.plot([0.3 * np.cos(np.radians(risk_angle)), 
            0.55 * np.cos(np.radians(risk_angle))], 
           [0.3 * np.sin(np.radians(risk_angle)), 
            0.55 * np.sin(np.radians(risk_angle))], 
           'r-', linewidth=5, marker='o', markersize=15, zorder=10)
    
    ax.set_title(f'Risk Position: {risk_percentage:.1f}%', 
                fontsize=11, fontweight='bold', pad=15, color='#1d3557')
    ax.axis('equal')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_risk_factor_chart(age, bp, chol, fbs, ecg, hr, risk_percentage):
    """Generate risk factor analysis bar chart"""
    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    
    # Calculate contributions
    age_factor = min(age / 100, 1.0) * 25
    bp_factor = min(max((bp - 90) / 100, 0), 1.0) * 20
    chol_factor = min(max((chol - 100) / 200, 0), 1.0) * 20
    fbs_factor = fbs * 15
    ecg_factor = (ecg / 2) * 20
    hr_factor = min((hr - 100) / 100, 1.0) * 15 if hr > 100 else 5
    
    factors = ['Age', 'BP', 'Cholesterol', 'Blood Sugar', 'ECG', 'Heart Rate']
    raw_contributions = [age_factor, bp_factor, chol_factor, fbs_factor, ecg_factor, hr_factor]
    
    total = sum(raw_contributions)
    if total > 0:
        contributions = [(c / total) * risk_percentage for c in raw_contributions]
    else:
        contributions = [risk_percentage / 6] * 6
    
    # Color bars
    bar_colors = []
    for contrib in contributions:
        if contrib > 20:
            bar_colors.append('#e76f51')
        elif contrib > 10:
            bar_colors.append('#e9c46a')
        else:
            bar_colors.append('#2a9d8f')
    
    bars = ax.barh(factors, contributions, color=bar_colors, edgecolor='white', linewidth=1.5)
    ax.set_xlabel('Contribution (%)', fontsize=9, fontweight='bold', color='#1d3557')
    ax.set_title('Risk Factor Analysis', fontsize=11, fontweight='bold', color='#1d3557', pad=10)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    # Add value labels
    for bar, val in zip(bars, contributions):
        if val > 1:
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                   f'{val:.1f}%', va='center', fontsize=8, fontweight='bold', color='#1d3557')
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_pdf(age, risk, patient_name='Patient', additional_data=None):
    """Generate a comprehensive medical report with charts and ECG"""
    doc = SimpleDocTemplate("heart_disease_report.pdf", 
                           rightMargin=0.5*inch, 
                           leftMargin=0.5*inch,
                           topMargin=0.5*inch, 
                           bottomMargin=0.5*inch,
                           pagesize=letter)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=colors.HexColor('#e63946'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#457b9d'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1d3557'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        spaceAfter=6
    )
    
    content = []
    
    # Title Header
    content.append(Paragraph("❤️ HeartCare Pro", title_style))
    content.append(Paragraph("Advanced Heart Disease Prediction System", subtitle_style))
    
    # Patient Information Section
    content.append(Paragraph("Patient Information", heading_style))
    
    patient_info = [
        ['Report Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
        ['Patient Name:', patient_name],
        ['Age:', str(age)],
    ]
    
    if additional_data:
        if 'sex' in additional_data:
            sex_display = "Male" if additional_data['sex'] == 1 else "Female"
            patient_info.append(['Sex:', sex_display])
        if 'bp' in additional_data:
            patient_info.append(['Blood Pressure:', f"{additional_data['bp']} mm Hg"])
        if 'chol' in additional_data:
            patient_info.append(['Cholesterol:', f"{additional_data['chol']} mg/dL"])
        if 'fbs' in additional_data:
            fbs_display = "Yes" if additional_data['fbs'] == 1 else "No"
            patient_info.append(['Fasting Blood Sugar > 120 mg/dL:', fbs_display])
        if 'cp' in additional_data:
            patient_info.append(['Chest Pain Type:', additional_data['cp']])
        if 'restecg' in additional_data:
            patient_info.append(['Resting ECG:', additional_data['restecg']])
    
    patient_table = Table(patient_info, colWidths=[2.2*inch, 3.3*inch])
    patient_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a8dadc')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1faee')),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    content.append(patient_table)
    content.append(Spacer(1, 20))
    
    # Risk Assessment Section with Color Coding
    content.append(Paragraph("Risk Assessment", heading_style))
    
    risk_percentage = round(risk * 100, 2)
    
    if risk < 0.3:
        risk_category = "Low Risk"
        risk_color = colors.HexColor('#2a9d8f')
        recommendation = """Your heart disease risk is <b>low</b>. Continue maintaining a healthy lifestyle with regular exercise, 
        balanced diet rich in fruits and vegetables, adequate sleep (7-8 hours), and routine health check-ups. 
        Avoid smoking and limit alcohol consumption."""
    elif risk < 0.6:
        risk_category = "Moderate Risk"
        risk_color = colors.HexColor('#e9c46a')
        recommendation = """You have <b>moderate risk</b> factors. Consider consulting with a healthcare provider about lifestyle 
        modifications including regular cardiovascular exercise, weight management, stress reduction techniques, 
        and monitoring your blood pressure and cholesterol levels."""
    else:
        risk_category = "High Risk"
        risk_color = colors.HexColor('#e76f51')
        recommendation = """Your risk score indicates <b>elevated risk</b>. We <b>strongly recommend</b> consulting with a cardiologist 
        for comprehensive evaluation including ECG, stress test, and personalized treatment plan. 
        Early intervention can significantly improve outcomes."""
    
    risk_data = [
        ['Heart Disease Risk Score', f"{risk_percentage}%"],
        ['Risk Category', f"🔴 {risk_category}" if risk > 0.6 else f"🟡 {risk_category}" if risk > 0.3 else f"🟢 {risk_category}"],
    ]
    
    risk_table = Table(risk_data, colWidths=[3*inch, 2.5*inch])
    risk_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (-1, -1), risk_color),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 2, colors.white),
        ('BOX', (0, 0), (-1, -1), 3, colors.black),
    ]))
    content.append(risk_table)
    content.append(Spacer(1, 20))
    
    # Generate and add ECG Signal Chart
    content.append(Paragraph("Simulated ECG Signal", heading_style))
    
    try:
        from ecg_features import get_ecg
        signal = get_ecg()
        
        fig, ax = plt.subplots(figsize=(8, 3), dpi=100)
        ax.plot(signal, linewidth=1.2, color='#e63946')
        ax.set_title('ECG Waveform', fontsize=12, fontweight='bold', color='#1d3557')
        ax.set_xlabel('Time (ms)', fontsize=9, color='#457b9d')
        ax.set_ylabel('Voltage (mV)', fontsize=9, color='#457b9d')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_facecolor('#f8f9fa')
        fig.patch.set_facecolor('white')
        plt.tight_layout()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        
        # Add image to PDF
        temp_img_path = "temp_ecg.png"
        with open(temp_img_path, 'wb') as f:
            f.write(buf.getvalue())
        
        content.append(Image(temp_img_path, width=6.5*inch, height=2.5*inch))
        content.append(Spacer(1, 15))
        plt.close(fig)
    except Exception as e:
        content.append(Paragraph(f"<i>ECG visualization unavailable: {str(e)}</i>", normal_style))
        content.append(Spacer(1, 15))
    
    # Add Risk Visualization Charts
    content.append(Paragraph("Risk Visualization", heading_style))
    content.append(Spacer(1, 10))
    
    try:
        # Generate Risk Gauge Chart
        gauge_buf = generate_risk_gauge_chart(risk_percentage)
        temp_gauge_path = "temp_gauge.png"
        with open(temp_gauge_path, 'wb') as f:
            f.write(gauge_buf.getvalue())
        
        # Generate Risk Factor Chart (if data available)
        if additional_data:
            bp_val = additional_data.get('bp', 120)
            chol_val = additional_data.get('chol', 200)
            fbs_val = additional_data.get('fbs', 0)
            ecg_val_map = {'Normal': 0, 'ST-T Wave Abnormality': 1, 'Left Ventricular Hypertrophy': 2}
            ecg_val = ecg_val_map.get(additional_data.get('restecg', 'Normal'), 0)
            hr_val = additional_data.get('thalach', 150)  # Use actual heart rate
            
            factor_buf = generate_risk_factor_chart(age, bp_val, chol_val, fbs_val, ecg_val, hr_val, risk_percentage)
            temp_factor_path = "temp_factor.png"
            with open(temp_factor_path, 'wb') as f:
                f.write(factor_buf.getvalue())
            
            # Add both charts side by side using a table
            chart_table = Table([
                [Image(temp_gauge_path, width=2.8*inch, height=2.8*inch),
                 Image(temp_factor_path, width=3.5*inch, height=2.8*inch)]
            ], colWidths=[2.8*inch, 3.5*inch])
            chart_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            content.append(chart_table)
        else:
            # Just add gauge chart centered
            content.append(Image(temp_gauge_path, width=4*inch, height=4*inch))
        
        content.append(Spacer(1, 20))
    except Exception as e:
        content.append(Paragraph(f"<i>Chart generation error: {str(e)}</i>", normal_style))
        content.append(Spacer(1, 15))
    
    # Medical Recommendations
    content.append(Paragraph("Medical Recommendations", heading_style))
    rec_paragraph = Paragraph(f"<b>{recommendation}</b>", normal_style)
    content.append(rec_paragraph)
    content.append(Spacer(1, 15))
    
    # Cardiovascular Health Tips with Icons
    content.append(Paragraph("Cardiovascular Health Tips", heading_style))
    
    tips_data = [
        ["🥗", "Nutrition", "Maintain a balanced diet rich in fruits, vegetables, whole grains, and lean proteins. Limit saturated fats, trans fats, and sodium intake."],
        ["🏃", "Exercise", "Engage in at least 150 minutes of moderate aerobic activity or 75 minutes of vigorous activity per week, plus muscle-strengthening exercises."],
        ["⚖️", "Weight Management", "Maintain a healthy weight (BMI 18.5-24.9). Even modest weight loss (5-10%) can significantly reduce cardiovascular risk."],
        ["😴", "Sleep", "Get 7-8 hours of quality sleep nightly. Poor sleep is linked to increased risk of heart disease, obesity, and diabetes."],
        ["🚭", "Avoid Smoking", "Quit smoking and avoid secondhand smoke. Smoking cessation rapidly reduces cardiovascular risk."],
        ["🍷", "Limit Alcohol", "If you drink, do so in moderation (up to 1 drink/day for women, 2 for men). Excessive alcohol raises blood pressure."],
        ["🧘", "Stress Management", "Practice stress-reduction techniques like meditation, deep breathing, yoga, or mindfulness. Chronic stress affects heart health."],
        ["🩺", "Regular Monitoring", "Schedule regular check-ups to monitor blood pressure, cholesterol, blood sugar, and other cardiovascular risk factors."]
    ]
    
    for icon, title, description in tips_data:
        tip_title = Paragraph(f"<b>{icon} {title}</b>", normal_style)
        tip_desc = Paragraph(description, normal_style)
        content.append(tip_title)
        content.append(tip_desc)
        content.append(Spacer(1, 4))
    
    content.append(Spacer(1, 20))
    
    # Risk Factor Education
    content.append(Paragraph("Understanding Your Risk Factors", heading_style))
    
    risk_factors = """
    <b>Key Cardiovascular Risk Factors:</b><br/>
    • <b>Age:</b> Risk increases with age, especially after 45 for men and 55 for women<br/>
    • <b>Family History:</b> Genetics play a role in heart disease susceptibility<br/>
    • <b>Blood Pressure:</b> Hypertension (≥140/90 mmHg) strains the heart and damages arteries<br/>
    • <b>Cholesterol:</b> High LDL ("bad") cholesterol and low HDL ("good") cholesterol increase risk<br/>
    • <b>Diabetes:</b> Fasting blood sugar >120 mg/dL indicates diabetes, a major risk factor<br/>
    • <b>Obesity:</b> Excess weight, especially around the waist, increases cardiac workload<br/>
    • <b>Physical Inactivity:</b> Sedentary lifestyle contributes to multiple risk factors<br/>
    • <b>Smoking:</b> Damages blood vessels, reduces oxygen, and increases clotting risk
    """
    
    content.append(Paragraph(risk_factors, normal_style))
    content.append(Spacer(1, 20))
    
    # Disclaimer Section
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        italic=True,
        alignment=TA_CENTER
    )
    
    content.append(Spacer(1, 30))
    content.append(Paragraph("<b>IMPORTANT DISCLAIMER</b>", 
                ParagraphStyle('DiscTitle', parent=disclaimer_style, fontName='Helvetica-Bold', fontSize=9)))
    
    disclaimer_text = """
    This report is generated by an AI-based prediction system (HeartCare Pro) for educational and informational purposes only. 
    It should <b>NOT</b> replace professional medical advice, diagnosis, or treatment. The information provided is not intended to 
    diagnose, treat, cure, or prevent any disease or medical condition. Always seek the advice of your physician or other 
    qualified health provider with any questions you may have regarding a medical condition. Never disregard professional 
    medical advice or delay in seeking it because of something you have read in this report. If you think you may have a 
    medical emergency, call your doctor or emergency services immediately.
    """
    
    content.append(Paragraph(disclaimer_text, disclaimer_style))
    content.append(Spacer(1, 20))
    
    # Footer
    footer_text = f"""
    <b>HeartCare Pro - Advanced Heart Disease Prediction System</b><br/>
    Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | Patient: {patient_name}<br/>
    <i>For Medical Education Only - Not a Replacement for Professional Healthcare</i>
    """
    
    content.append(Paragraph(footer_text, disclaimer_style))
    
    # Build PDF
    doc.build(content)
    return "heart_disease_report.pdf"