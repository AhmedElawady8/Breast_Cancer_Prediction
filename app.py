import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import warnings
import os
import hashlib
import time
from datetime import datetime
import io
import base64
from PIL import Image
import json
warnings.filterwarnings('ignore')

# إعداد الصفحة
st.set_page_config(
    page_title="نظام الذكاء الاصطناعي للكشف عن سرطان الثدي",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تنسيق CSS احترافي
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap');
    
    * {
        font-family: 'Tajawal', sans-serif;
    }
    
    .main-title {
        text-align: center;
        color: #2c3e50;
        font-size: 2.8rem;
        margin-bottom: 1rem;
        font-weight: 700;
        padding: 10px;
        background: linear-gradient(90deg, #3498db, #2c3e50);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .section-title {
        color: #3498db;
        font-size: 1.8rem;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 3px solid #3498db;
        padding-bottom: 0.5rem;
    }
    
    .card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    .medical-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 5px solid #3498db;
        padding: 20px;
        margin: 10px 0;
        border-radius: 10px;
    }
    
    .risk-high {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(255, 65, 108, 0.3);
    }
    
    .risk-low {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(86, 171, 47, 0.3);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
        color: white;
        border: none;
        padding: 15px 40px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 1.2rem;
        width: 100%;
        margin: 20px 0;
    }
    
    .login-container {
        background: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        max-width: 500px;
        margin: 50px auto;
    }
    
    .doctor-badge {
        background: linear-gradient(135deg, #3498db, #2c3e50);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
    }
    
    .patient-record {
        background: white;
        border-left: 4px solid #3498db;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #ff9800 0%, #ff5722 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
    
    .success-box {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class AuthenticationSystem:
    def __init__(self):
        # كلمات مرور مشفرة (في بيئة حقيقية، يتم تخزينها في قاعدة بيانات)
        self.users = {
            'dr.ahmed': self._hash_password('password123'),
            'dr.amira': self._hash_password('medical456'),
            'admin': self._hash_password('admin@2024')
        }
        self.user_roles = {
            'dr.ahmed': 'doctor',
            'dr.amira': 'doctor',
            'admin': 'admin'
        }
    
    def _hash_password(self, password):
        """تشفير كلمة المرور باستخدام SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username, password):
        """تسجيل دخول المستخدم"""
        username_lower = username.lower()
        if username_lower in self.users and self.users[username_lower] == self._hash_password(password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username_lower
            st.session_state['role'] = self.user_roles.get(username_lower, 'doctor')
            return True
        return False
    
    def logout(self):
        """تسجيل خروج المستخدم"""
        for key in ['logged_in', 'username', 'role']:
            if key in st.session_state:
                del st.session_state[key]
    
    def add_user(self, username, password, role='doctor'):
        """إضافة مستخدم جديد (للمشرف فقط)"""
        username_lower = username.lower()
        if username_lower not in self.users:
            self.users[username_lower] = self._hash_password(password)
            self.user_roles[username_lower] = role
            return True
        return False

class DataManager:
    def __init__(self):
        self.predictions_file = 'patient_records.csv'
        self._initialize_files()
    
    def _initialize_files(self):
        """تهيئة ملفات البيانات إذا لم تكن موجودة"""
        if not os.path.exists(self.predictions_file):
            # إنشاء ملف CSV مع الأعمدة الأساسية
            columns = [
                'patient_id', 'patient_name', 'age', 'gender', 
                'doctor', 'timestamp', 'prediction', 
                'probability_0', 'probability_1', 'notes'
            ]
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.predictions_file, index=False, encoding='utf-8-sig')
    
    def save_prediction(self, patient_info, input_values, prediction, probability, feature_names):
        """حفظ نتيجة التشخيص في قاعدة البيانات"""
        try:
            # تحميل البيانات الحالية
            if os.path.exists(self.predictions_file):
                df = pd.read_csv(self.predictions_file, encoding='utf-8-sig')
            else:
                df = pd.DataFrame()
            
            # إنشاء سجل جديد
            new_record = {
                'patient_id': f"PAT{len(df)+1:04d}",
                'patient_name': patient_info.get('name', 'غير معروف'),
                'age': patient_info.get('age', ''),
                'gender': patient_info.get('gender', ''),
                'doctor': st.session_state.get('username', 'غير معروف'),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'prediction': 'خبيث' if prediction == 1 else 'حميد',
                'probability_0': round(probability[0] * 100, 2) if probability is not None else 0,
                'probability_1': round(probability[1] * 100, 2) if probability is not None else 0,
                'notes': patient_info.get('notes', '')
            }
            
            # إضافة قياسات المريض
            for i, feature_name in enumerate(feature_names):
                if i < len(input_values):
                    new_record[feature_name] = round(float(input_values[i]), 6)
                else:
                    new_record[feature_name] = 0.0
            
            # إضافة السجل الجديد
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
            
            # حفظ الملف بالترتيب الصحيح للأعمدة
            df.to_csv(self.predictions_file, index=False, encoding='utf-8-sig')
            
            return new_record['patient_id']
            
        except Exception as e:
            st.error(f"❌ خطأ في حفظ بيانات المريض: {str(e)}")
            return None
    
    def get_patient_history(self, doctor=None):
        """استرجاع سجل المرضى"""
        try:
            if os.path.exists(self.predictions_file):
                df = pd.read_csv(self.predictions_file, encoding='utf-8-sig')
                if doctor:
                    df = df[df['doctor'] == doctor]
                return df
            else:
                return pd.DataFrame()
        except Exception as e:
            st.error(f"❌ خطأ في قراءة السجلات: {str(e)}")
            return pd.DataFrame()
    
    def get_statistics(self):
        """الحصول على إحصائيات عامة"""
        df = self.get_patient_history()
        if len(df) == 0:
            return {
                'total_patients': 0,
                'malignant_cases': 0,
                'benign_cases': 0,
                'today_cases': 0
            }
        
        total = len(df)
        malignant = len(df[df['prediction'] == 'خبيث'])
        benign = len(df[df['prediction'] == 'حميد'])
        
        # حساب الحالات اليومية
        today_date = datetime.now().strftime("%Y-%m-%d")
        today_cases = 0
        if 'timestamp' in df.columns:
            for timestamp in df['timestamp']:
                if isinstance(timestamp, str) and today_date in timestamp:
                    today_cases += 1
        
        return {
            'total_patients': total,
            'malignant_cases': malignant,
            'benign_cases': benign,
            'today_cases': today_cases
        }

class BreastCancerPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.features = None
        self.data_manager = DataManager()
        self.model_loaded = False
        
    def load_model(self, model_path='logistic_model.pkl', scaler_path='scaler.pkl', features_path='feature_names.json'):
        """تحميل النموذج والـ Scaler وأسماء الميزات"""
        try:
            # تحميل أسماء الميزات أولاً
            if os.path.exists(features_path):
                with open(features_path, 'r', encoding='utf-8') as f:
                    self.features = json.load(f)
            else:
                st.error(f"❌ ملف أسماء الميزات غير موجود: {features_path}")
                return False
            
            # تحميل النموذج
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
            else:
                st.error(f"❌ ملف النموذج غير موجود: {model_path}")
                return False
            
            # تحميل Scaler
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
            else:
                st.error(f"❌ ملف الـ Scaler غير موجود: {scaler_path}")
                return False
            
            self.model_loaded = True
            st.success(f"✅ تم تحميل النموذج بنجاح ({len(self.features)} ميزة)")
            return True
            
        except Exception as e:
            st.error(f"❌ خطأ في تحميل النموذج: {str(e)}")
            return False
    
    def predict(self, input_data):
        """تنفيذ التنبؤ"""
        if self.model is None or self.scaler is None:
            st.error("❌ النموذج أو الـ Scaler غير محمل")
            return None, None
    
        try:
            # التحقق من عدد الميزات
            if len(input_data) != len(self.features):
                st.error(f"❌ عدد القيم المدخلة ({len(input_data)}) لا يتطابق مع عدد الميزات المطلوبة ({len(self.features)})")
                return None, None
         
            # تحويل البيانات إلى DataFrame
            df_input = pd.DataFrame([input_data], columns=self.features)
            
            # تطبيق الـ scaler
            input_scaled = self.scaler.transform(df_input)
            
            # التنبؤ
            prediction = self.model.predict(input_scaled)[0]
            probability = self.model.predict_proba(input_scaled)[0]

            return prediction, probability
        
        except ValueError as e:
            st.error(f"❌ خطأ في معالجة البيانات: {str(e)}")
            return None, None
        except Exception as e:
            st.error(f"❌ خطأ غير متوقع في التنبؤ: {str(e)}")
            return None, None

def create_breast_anatomy_chart():
    """إنشاء مخطط تشريح الثدي"""
    fig = go.Figure()
    
    # رسم شكل الثدي
    fig.add_shape(type="circle", x0=0.2, y0=0.2, x1=0.8, y1=0.8,
                  line=dict(color="#3498db", width=3))
    
    tumor_types = {
        "ورم حميد": {"color": "#2ecc71", "x": 0.4, "y": 0.6},
        "ورم خبيث": {"color": "#e74c3c", "x": 0.6, "y": 0.4}
    }
    
    for tumor_name, tumor_info in tumor_types.items():
        fig.add_trace(go.Scatter(
            x=[tumor_info["x"]],
            y=[tumor_info["y"]],
            mode="markers+text",
            name=tumor_name,
            marker=dict(size=25, color=tumor_info["color"]),
            text=[f"● {tumor_name}"],
            textposition="top center"
        ))
    
    fig.update_layout(
        plot_bgcolor="rgba(240, 248, 255, 0.8)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        showlegend=True,
        height=400,
        margin=dict(l=0, r=0, t=50, b=0),
        title="مخطط تشريح الثدي"
    )
    
    return fig

def show_login_page(auth_system):
    """عرض صفحة تسجيل الدخول"""
    st.markdown('<h1 class="main-title">🩺 نظام الذكاء الاصطناعي للكشف عن سرطان الثدي</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align: center; color: #2c3e50;">🔐 تسجيل دخول الطبيب</h2>', unsafe_allow_html=True)
        
        username = st.text_input("👤 اسم المستخدم", placeholder="أدخل اسم المستخدم")
        password = st.text_input("🔒 كلمة المرور", type="password", placeholder="أدخل كلمة المرور")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("دخول النظام", use_container_width=True, type="primary"):
                if username and password:
                    if auth_system.login(username, password):
                        st.success("✅ تم تسجيل الدخول بنجاح!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
                else:
                    st.warning("⚠️ يرجى إدخال اسم المستخدم وكلمة المرور")
        
        with col_btn2:
            if st.button("عرض معلومات النظام", use_container_width=True):
                st.info("""
                **معلومات النظام:**
                - النظام مخصص لأخصائيي الأشعة والأورام
                - الدخول مقصور على الأطباء المسجلين
                - البيانات محفوظة بسرية تامة
                """)
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #7f8c8d;'>
        <strong>بيانات الدخول التجريبية:</strong><br>
        👤 dr.ahmed / 🔒 password123<br>
        👤 dr.amira / 🔒 medical456<br>
        👤 admin / 🔒 admin@2024
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_doctor_dashboard(auth_system, predictor):
    """عرض لوحة تحكم الطبيب"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        username = st.session_state.get("username", "")
        display_name = username.split(".")[-1].title() if "." in username else username.title()
        st.markdown(f'<h2 style="margin: 0;">👨‍⚕️ مرحباً د. {display_name}</h2>', unsafe_allow_html=True)
    
    with col2:
        role = st.session_state.get("role", "طبيب")
        st.markdown(f'<div class="doctor-badge">{role}</div>', unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            auth_system.logout()
            st.rerun()
    
    st.markdown("---")
    
    # قائمة التنقل الجانبية
    menu_options = [
        "🏠 الصفحة الرئيسية",
        "👨‍⚕️ تشخيص مريض جديد", 
        "📋 سجل المرضى",
        "📊 التحاليل الإحصائية",
        "⚙️ إدارة النظام",
        "ℹ️ معلومات طبية"
    ]
    
    if st.session_state.get("role") == "admin":
        menu_options.append("👥 إدارة المستخدمين")
    
    page = st.sidebar.radio("القائمة الرئيسية", menu_options, index=0)
    
    # تحميل النموذج إذا لم يكن محملاً
    if not predictor.model_loaded:
        if not predictor.load_model():
            st.warning("⚠️ يرجى تحميل النموذج أولاً من صفحة 'إدارة النظام'")
    
    if page == "🏠 الصفحة الرئيسية":
        show_homepage(predictor)
    elif page == "👨‍⚕️ تشخيص مريض جديد":
        show_prediction_page(predictor)
    elif page == "📋 سجل المرضى":
        show_patient_records(predictor)
    elif page == "📊 التحاليل الإحصائية":
        show_statistics(predictor)
    elif page == "⚙️ إدارة النظام":
        show_system_management(predictor, auth_system)
    elif page == "ℹ️ معلومات طبية":
        show_medical_info()
    elif page == "👥 إدارة المستخدمين" and st.session_state.get("role") == "admin":
        show_user_management(auth_system)

def show_homepage(predictor):
    """عرض الصفحة الرئيسية"""
    st.markdown('<h1 class="main-title">🏥 لوحة التحكم الطبية</h1>', unsafe_allow_html=True)
    
    # الحصول على الإحصائيات
    stats = predictor.data_manager.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='stats-card'>
            <h4>👨‍⚕️ فريق العمل</h4>
            <div style='font-size: 2.5rem; font-weight: bold;'>3</div>
            <p>أعضاء مسجلين</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stats-card'>
            <h4>📋 النشاط اليومي</h4>
            <div style='font-size: 2.5rem; font-weight: bold;'>{stats['today_cases']}</div>
            <p>تشخيص جديد</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stats-card'>
            <h4>⚠️ الحالات الخبيثة</h4>
            <div style='font-size: 2.5rem; font-weight: bold;'>{stats['malignant_cases']}</div>
            <p>إجمالي الخبيث</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='stats-card'>
            <h4>📊 إجمالي الحالات</h4>
            <div style='font-size: 2.5rem; font-weight: bold;'>{stats['total_patients']}</div>
            <p>مريض مسجل</p>
        </div>
        """, unsafe_allow_html=True)
    
    # حالة النظام
    if predictor.model_loaded:
        st.markdown('<div class="success-box">✅ النظام جاهز للعمل</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="warning-box">⚠️ يرجى تحميل النموذج من صفحة إدارة النظام</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">📊 نظرة عامة</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = create_breast_anatomy_chart()
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if stats['total_patients'] > 0:
            labels = ['حميد', 'خبيث']
            values = [stats['benign_cases'], stats['malignant_cases']]
            colors = ['#2ecc71', '#e74c3c']
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker_colors=colors,
                textinfo='label+percent'
            )])
            fig.update_layout(title="توزيع التشخيصات", height=400)
        else:
            fig = go.Figure(data=[go.Pie(
                labels=['حميد', 'خبيث'],
                values=[50, 50],
                hole=0.4,
                marker_colors=['#2ecc71', '#e74c3c']
            )])
            fig.update_layout(title="توزيع التشخيصات", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # ملاحظات ونصائح
    st.markdown('<div class="section-title">💡 نصائح واستفسارات</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='medical-card'>
            <h4>📋 قبل التشخيص:</h4>
            <ul>
            <li>✓ تأكد من دقة القياسات المدخلة</li>
            <li>✓ راجع تاريخ المريض الطبي</li>
            <li>✓ قارن مع الفحوصات السابقة</li>
            <li>✓ استشر زملاءك في الحالات الصعبة</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='medical-card'>
            <h4>🔍 بعد التشخيص:</h4>
            <ul>
            <li>✓ احفظ نتائج التشخيص</li>
            <li>✓ أضف ملاحظات مفصلة</li>
            <li>✓ خطط للمتابعة الدورية</li>
            <li>✓ شارك النتائج مع المريض</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def show_prediction_page(predictor):
    """عرض صفحة التشخيص"""
    st.markdown('<h1 class="main-title">👨‍⚕️ تشخيص مريض جديد</h1>', unsafe_allow_html=True)
    
    if not predictor.model_loaded:
        st.error("❌ النموذج الطبي غير جاهز!")
        st.info("انتقل إلى صفحة 'إدارة النظام' لتحميل النموذج")
        return
    
    st.markdown("""
    <div class='medical-card'>
    <strong>ملاحظة:</strong> أدخل القياسات بدقة من تقرير الأشعة أو الفحص الطبي.
    جميع القيم يجب أن تكون موجبة.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">👤 معلومات المريض</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        patient_name = st.text_input("اسم المريض", placeholder="الاسم الكامل", key="patient_name")
    
    with col2:
        patient_age = st.number_input("العمر", min_value=1, max_value=120, value=40, key="patient_age")
    
    with col3:
        patient_gender = st.selectbox("الجنس", ["أنثى", "ذكر", "غير محدد"], key="patient_gender")
    
    patient_notes = st.text_area("ملاحظات طبية", placeholder="أدخل أي معلومات إضافية عن حالة المريض...", 
                                height=100, key="patient_notes")
    
    st.markdown('<div class="section-title">📊 القياسات الطبية</div>', unsafe_allow_html=True)
    
    # استخدام أسماء الميزات الفعلية
    if predictor.features:
        num_features = len(predictor.features)
        st.info(f"عدد الميزات المطلوبة: {num_features}")
        
        # تقسيم الميزات إلى مجموعات
        features_group1 = predictor.features[:9]  # المتوسطات
        features_group2 = predictor.features[9:16]  # الانحراف المعياري
        features_group3 = predictor.features[16:]  # القيم القصوى
        
        tabs = st.tabs(["📊 المتوسطات", "📈 الانحراف المعياري", "📉 القيم القصوى"])
        
        input_values = []
        
        with tabs[0]:
            cols = st.columns(2)
            for i, feature in enumerate(features_group1):
                col_idx = 0 if i < 5 else 1
                with cols[col_idx]:
                    # تحديد النطاقات بناءً على نوع الميزة (مدى طبي واقعي)
                    if 'radius' in feature:
                        min_val, max_val, default = 5.0, 30.0, 12.5
                    elif 'texture' in feature:
                        min_val, max_val, default = 8.0, 40.0, 18.5
                    elif 'perimeter' in feature:
                        min_val, max_val, default = 40.0, 200.0, 85.0
                    elif 'area' in feature:
                        min_val, max_val, default = 150.0, 2500.0, 550.0
                    elif 'smoothness' in feature:
                        min_val, max_val, default = 0.05, 0.20, 0.095
                    elif 'compactness' in feature:
                        min_val, max_val, default = 0.02, 0.35, 0.085
                    elif 'concavity' in feature:
                        min_val, max_val, default = 0.0, 0.5, 0.07
                    elif 'concave_points' in feature:
                        min_val, max_val, default = 0.0, 0.25, 0.045
                    elif 'symmetry' in feature:
                        min_val, max_val, default = 0.1, 0.35, 0.18
                    elif 'fractal_dimension' in feature:
                        min_val, max_val, default = 0.04, 0.12, 0.065
                    else:
                        min_val, max_val, default = 0.01, 0.5, 0.1
                    
                    value = st.slider(
                        f"{feature}",
                        min_value=float(min_val),
                        max_value=float(max_val),
                        value=float(default),
                        step=0.1 if max_val > 10 else 0.001,
                        key=f"slider_{feature}"
                    )
                    input_values.append(value)
        
        with tabs[1]:
            cols = st.columns(2)
            for i, feature in enumerate(features_group2):
                col_idx = 0 if i < 4 else 1
                with cols[col_idx]:
                    # قيم الانحراف المعياري بناءً على نوع الميزة
                    if 'radius' in feature:
                        min_val, max_val, default = 0.1, 5.0, 0.6
                    elif 'texture' in feature:
                        min_val, max_val, default = 0.3, 5.0, 1.2
                    elif 'perimeter' in feature:
                        min_val, max_val, default = 0.8, 10.0, 2.5
                    elif 'area' in feature:
                        min_val, max_val, default = 10.0, 300.0, 45.0
                    elif 'smoothness' in feature:
                        min_val, max_val, default = 0.001, 0.03, 0.007
                    elif 'compactness' in feature:
                        min_val, max_val, default = 0.002, 0.1, 0.025
                    elif 'concavity' in feature:
                        min_val, max_val, default = 0.0, 0.2, 0.03
                    else:
                        min_val, max_val, default = 0.0, 5.0, 0.5
                    
                    value = st.slider(
                        f"{feature}",
                        min_value=float(min_val),
                        max_value=float(max_val),
                        value=float(default),
                        step=0.01 if max_val > 1 else 0.001,
                        key=f"slider_{feature}"
                    )
                    input_values.append(value)
        
        with tabs[2]:
            cols = st.columns(2)
            for i, feature in enumerate(features_group3):
                col_idx = 0 if i < 5 else 1
                with cols[col_idx]:
                    # قيم القصوى بناءً على نوع الميزة
                    if 'radius' in feature:
                        min_val, max_val, default = 5.0, 40.0, 16.0
                    elif 'texture' in feature:
                        min_val, max_val, default = 10.0, 50.0, 25.0
                    elif 'perimeter' in feature:
                        min_val, max_val, default = 50.0, 250.0, 110.0
                    elif 'area' in feature:
                        min_val, max_val, default = 200.0, 4000.0, 900.0
                    elif 'smoothness' in feature:
                        min_val, max_val, default = 0.07, 0.25, 0.13
                    elif 'compactness' in feature:
                        min_val, max_val, default = 0.03, 0.6, 0.25
                    elif 'concavity' in feature:
                        min_val, max_val, default = 0.0, 1.0, 0.3
                    elif 'concave_points' in feature:
                        min_val, max_val, default = 0.0, 0.3, 0.15
                    elif 'symmetry' in feature:
                        min_val, max_val, default = 0.15, 0.7, 0.3
                    elif 'fractal_dimension' in feature:
                        min_val, max_val, default = 0.05, 0.2, 0.1
                    else:
                        min_val, max_val, default = 0.0, 50.0, 10.0
                    
                    value = st.slider(
                        f"{feature}",
                        min_value=float(min_val),
                        max_value=float(max_val),
                        value=float(default),
                        step=0.1 if max_val > 10 else 0.01,
                        key=f"slider_{feature}"
                    )
                    input_values.append(value)
        
        patient_info = {
            'name': patient_name,
            'age': patient_age,
            'gender': patient_gender,
            'notes': patient_notes
        }
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔍 بدء التحليل الطبي", type="primary", use_container_width=True):
                if len(input_values) == num_features:
                    if not patient_name.strip():
                        st.warning("⚠️ يرجى إدخال اسم المريض")
                        return
                    
                    with st.spinner("🔄 جاري تحليل البيانات..."):
                        time.sleep(1)  # محاكاة وقت المعالجة
                        prediction, probability = predictor.predict(input_values)
                        
                        if prediction is not None and probability is not None:
                            patient_id = predictor.data_manager.save_prediction(
                                patient_info, input_values, prediction, probability, predictor.features
                            )
                            
                            if patient_id:
                                show_prediction_results(prediction, probability, patient_id, patient_info)
                            else:
                                st.error("❌ فشل في حفظ بيانات المريض")
                        else:
                            st.error("❌ حدث خطأ في عملية التنبؤ. تأكد من صحة البيانات المدخلة.")
                else:
                    st.error(f"❌ عدد القيم المدخلة ({len(input_values)}) لا يتطابق مع المطلوب ({num_features})")
        
        with col2:
            if st.button("🔄 إعادة تعيين النموذج", use_container_width=True):
                st.info("سيتم إعادة تعيين جميع الحقول")
                st.rerun()
    else:
        st.error("❌ لم يتم تحميل أسماء الميزات. تحقق من ملف feature_names.json")

def show_prediction_results(prediction, probability, patient_id, patient_info):
    """عرض نتائج التشخيص"""
    st.markdown("---")
    
    if prediction == 1:  # خبيث
        st.markdown(f"""
        <div class="risk-high">
            <h2>⚠️ تشخيص: حالة عالية الخطورة (خبيث)</h2>
            <div style='background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px; margin: 15px 0;'>
                <p style='font-size: 1.2rem; margin: 10px 0;'>
                <strong>رقم المريض:</strong> {patient_id}<br>
                <strong>الاسم:</strong> {patient_info['name']}<br>
                <strong>العمر:</strong> {patient_info['age']}<br>
                <strong>الجنس:</strong> {patient_info['gender']}
                </p>
            </div>
            <div style='text-align: center; margin: 20px 0;'>
                <div style='font-size: 2.5rem; font-weight: bold;'>{probability[1]*100:.2f}%</div>
                <p>احتمالية الإصابة بالورم الخبيث</p>
            </div>
            <div style='background: rgba(255,255,255,0.3); padding: 15px; border-radius: 8px; margin: 15px 0;'>
                <p style='text-align: center; margin: 0;'>
                ⚠️ <strong>التوصية:</strong> إحالة عاجلة إلى أخصائي الأورام لإجراء فحوصات إضافية
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:  # حميد
        st.markdown(f"""
        <div class="risk-low">
            <h2>✅ تشخيص: حالة منخفضة الخطورة (حميد)</h2>
            <div style='background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px; margin: 15px 0;'>
                <p style='font-size: 1.2rem; margin: 10px 0;'>
                <strong>رقم المريض:</strong> {patient_id}<br>
                <strong>الاسم:</strong> {patient_info['name']}<br>
                <strong>العمر:</strong> {patient_info['age']}<br>
                <strong>الجنس:</strong> {patient_info['gender']}
                </p>
            </div>
            <div style='text-align: center; margin: 20px 0;'>
                <div style='font-size: 2.5rem; font-weight: bold;'>{probability[0]*100:.2f}%</div>
                <p>احتمالية السلامة</p>
            </div>
            <div style='background: rgba(255,255,255,0.3); padding: 15px; border-radius: 8px; margin: 15px 0;'>
                <p style='text-align: center; margin: 0;'>
                ✅ <strong>التوصية:</strong> متابعة دورية كل 6 أشهر مع فحص سريري
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">📈 تحليل إحصائي</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure(data=[
            go.Pie(
                labels=['حميد', 'خبيث'],
                values=[probability[0]*100, probability[1]*100],
                hole=0.5,
                marker_colors=['#2ecc71', '#e74c3c'],
                textinfo='label+percent'
            )
        ])
        fig.update_layout(
            title="توزيع الاحتمالات",
            height=350,
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(data=[
            go.Bar(
                x=['سلامة', 'خباثة'],
                y=[probability[0]*100, probability[1]*100],
                marker_color=['#2ecc71', '#e74c3c'],
                text=[f'{probability[0]*100:.1f}%', f'{probability[1]*100:.1f}%'],
                textposition='auto'
            )
        ])
        fig.update_layout(
            title="المقارنة الاحتمالية",
            yaxis_title="النسبة المئوية %",
            height=350,
            yaxis_range=[0, 100]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # خيارات إضافية
    st.markdown('<div class="section-title">📋 خيارات إضافية</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 حفظ التقرير", use_container_width=True):
            st.success("✅ تم حفظ التقرير في سجلات المرضى")
    
    with col2:
        if st.button("🖨️ طباعة النتائج", use_container_width=True):
            st.info("🚧 هذه الميزة قيد التطوير")
    
    with col3:
        if st.button("📧 مشاركة النتائج", use_container_width=True):
            st.info("🚧 هذه الميزة قيد التطوير")

def show_patient_records(predictor):
    """عرض سجل المرضى"""
    st.markdown('<h1 class="main-title">📋 سجل المرضى</h1>', unsafe_allow_html=True)
    
    # خيارات البحث والتصفية
    st.markdown('<div class="section-title">🔍 البحث والتصفية</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_name = st.text_input("اسم المريض", placeholder="أدخل اسم المريض")
    
    with col2:
        search_type = st.selectbox("نوع البحث", ["يحتوي على", "يطابق بالضبط"])
    
    with col3:
        date_range = st.date_input("الفترة الزمنية", [])
    
    # أزرار التصفية
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        show_all = st.button("عرض الكل", use_container_width=True)
    
    with col_filter2:
        show_malignant = st.button("الحالات الخبيثة فقط", use_container_width=True)
    
    with col_filter3:
        show_benign = st.button("الحالات الحميدة فقط", use_container_width=True)
    
    # جلب البيانات
    df = predictor.data_manager.get_patient_history(st.session_state.get('username'))
    
    if len(df) > 0:
        # تطبيق الفلاتر
        filtered_df = df.copy()
        
        if search_name:
            if search_type == "يحتوي على":
                filtered_df = filtered_df[filtered_df['patient_name'].str.contains(search_name, case=False, na=False)]
            else:
                filtered_df = filtered_df[filtered_df['patient_name'].str.lower() == search_name.lower()]
        
        if show_malignant:
            filtered_df = filtered_df[filtered_df['prediction'] == 'خبيث']
        elif show_benign:
            filtered_df = filtered_df[filtered_df['prediction'] == 'حميد']
        
        # إحصائيات
        st.markdown('<div class="section-title">📊 الإحصائيات</div>', unsafe_allow_html=True)
        
        total_filtered = len(filtered_df)
        malignant_filtered = len(filtered_df[filtered_df['prediction'] == 'خبيث'])
        benign_filtered = len(filtered_df[filtered_df['prediction'] == 'حميد'])
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.metric("عدد الحالات المصفاة", total_filtered)
        
        with col_stat2:
            st.metric("الحالات الخبيثة", malignant_filtered)
        
        with col_stat3:
            st.metric("الحالات الحميدة", benign_filtered)
        
        # عرض البيانات
        if total_filtered > 0:
            st.markdown('<div class="section-title">👥 سجلات المرضى</div>', unsafe_allow_html=True)
            
            # اختيار الأعمدة للعرض
            display_columns = ['patient_id', 'patient_name', 'age', 'gender', 
                             'timestamp', 'prediction', 'probability_1', 'doctor']
            
            display_df = filtered_df[display_columns].copy()
            display_df = display_df.rename(columns={
                'patient_id': 'رقم المريض',
                'patient_name': 'اسم المريض',
                'age': 'العمر',
                'gender': 'الجنس',
                'timestamp': 'التاريخ والوقت',
                'prediction': 'التشخيص',
                'probability_1': 'نسبة الخطورة %',
                'doctor': 'الطبيب المعالج'
            })
            
            # تنسيق التاريخ
            display_df['التاريخ والوقت'] = pd.to_datetime(display_df['التاريخ والوقت']).dt.strftime('%Y-%m-%d %H:%M')
            
            # إضافة تلوين للجدول
            def color_cells(val):
                if val == 'خبيث':
                    return 'background-color: #ffcccc'
                elif val == 'حميد':
                    return 'background-color: #ccffcc'
                return ''
            
            styled_df = display_df.style.applymap(color_cells, subset=['التشخيص'])
            
            st.dataframe(styled_df, use_container_width=True, height=400)
            
            # خيارات التصدير
            st.markdown('<div class="section-title">📥 خيارات التصدير</div>', unsafe_allow_html=True)
            
            col_exp1, col_exp2, col_exp3 = st.columns(3)
            
            with col_exp1:
                if st.button("💾 تصدير إلى CSV", use_container_width=True):
                    csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="تحميل ملف CSV",
                        data=csv,
                        file_name=f"نتائج_البحث_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col_exp2:
                if st.button("📊 تصدير إلى Excel", use_container_width=True):
                    # محاكاة التصدير إلى Excel
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                        filtered_df.to_excel(writer, index=False, sheet_name='سجلات المرضى')
                    excel_buffer.seek(0)
                    
                    st.download_button(
                        label="تحميل ملف Excel",
                        data=excel_buffer,
                        file_name=f"سجلات_المرضى_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            
            with col_exp3:
                if st.button("📄 تصدير تقرير PDF", use_container_width=True):
                    st.info("🚧 هذه الميزة قيد التطوير")
        
        else:
            st.warning("⚠️ لا توجد نتائج تطابق معايير البحث")
    
    else:
        st.info("📭 لا توجد سجلات للمرضى حتى الآن")
        
        if st.button("➕ إضافة أول مريض", use_container_width=True):
            st.switch_page("👨‍⚕️ تشخيص مريض جديد")

def show_statistics(predictor):
    """عرض التحليلات الإحصائية"""
    st.markdown('<h1 class="main-title">📊 التحاليل الإحصائية</h1>', unsafe_allow_html=True)
    
    df = predictor.data_manager.get_patient_history()
    
    if len(df) > 0:
        # إحصائيات عامة
        col1, col2, col3, col4 = st.columns(4)
        
        total_patients = len(df)
        malignant_cases = len(df[df['prediction'] == 'خبيث'])
        benign_cases = len(df[df['prediction'] == 'حميد'])
        
        with col1:
            st.metric("إجمالي المرضى", total_patients)
        
        with col2:
            st.metric("الحالات الخبيثة", malignant_cases)
        
        with col3:
            st.metric("الحالات الحميدة", benign_cases)
        
        with col4:
            if total_patients > 0:
                malignant_percentage = (malignant_cases / total_patients) * 100
                st.metric("نسبة الخبيث", f"{malignant_percentage:.1f}%")
            else:
                st.metric("نسبة الخبيث", "0%")
        
        st.markdown('<div class="section-title">📈 مخططات إحصائية</div>', unsafe_allow_html=True)
        
        # مخططات متعددة
        tab1, tab2, tab3, tab4 = st.tabs(["التوزيع", "الأعمار", "الخطورة", "الزمني"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # مخطط دائري
                fig1 = go.Figure(data=[
                    go.Pie(
                        labels=['حميد', 'خبيث'],
                        values=[benign_cases, malignant_cases],
                        hole=0.3,
                        marker_colors=['#2ecc71', '#e74c3c']
                    )
                ])
                fig1.update_layout(
                    title="توزيع التشخيصات",
                    height=400
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # مخطط شريطي
                fig2 = go.Figure(data=[
                    go.Bar(
                        x=['حميد', 'خبيث'],
                        y=[benign_cases, malignant_cases],
                        marker_color=['#2ecc71', '#e74c3c'],
                        text=[f'{benign_cases}', f'{malignant_cases}'],
                        textposition='auto'
                    )
                ])
                fig2.update_layout(
                    title="مقارنة عدد الحالات",
                    yaxis_title="عدد الحالات",
                    height=400
                )
                st.plotly_chart(fig2, use_container_width=True)
        
        with tab2:
            # مخطط توزيع الأعمار
            fig3 = px.histogram(
                df, 
                x='age',
                title='توزيع الأعمار',
                nbins=20,
                color='prediction',
                color_discrete_map={'خبيث': '#e74c3c', 'حميد': '#2ecc71'},
                labels={'age': 'العمر', 'count': 'عدد الحالات'}
            )
            fig3.update_layout(height=400)
            st.plotly_chart(fig3, use_container_width=True)
        
        with tab3:
            # مخطط توزيع الخطورة
            if 'probability_1' in df.columns:
                fig4 = px.histogram(
                    df,
                    x='probability_1',
                    title='توزيع نسبة الخطورة',
                    nbins=20,
                    color='prediction',
                    color_discrete_map={'خبيث': '#e74c3c', 'حميد': '#2ecc71'},
                    labels={'probability_1': 'نسبة الخطورة %', 'count': 'عدد الحالات'}
                )
                fig4.update_layout(height=400)
                st.plotly_chart(fig4, use_container_width=True)
        
        with tab4:
            # مخطط زمني
            if len(df) > 1 and 'timestamp' in df.columns:
                try:
                    df['date'] = pd.to_datetime(df['timestamp']).dt.date
                    daily_counts = df.groupby(['date', 'prediction']).size().unstack(fill_value=0)
                    
                    fig5 = go.Figure()
                    
                    if 'خبيث' in daily_counts.columns:
                        fig5.add_trace(go.Scatter(
                            x=daily_counts.index,
                            y=daily_counts['خبيث'],
                            mode='lines+markers',
                            name='خبيث',
                            line=dict(color='#e74c3c', width=2)
                        ))
                    
                    if 'حميد' in daily_counts.columns:
                        fig5.add_trace(go.Scatter(
                            x=daily_counts.index,
                            y=daily_counts['حميد'],
                            mode='lines+markers',
                            name='حميد',
                            line=dict(color='#2ecc71', width=2)
                        ))
                    
                    fig5.update_layout(
                        title='التشخيصات حسب التاريخ',
                        xaxis_title='التاريخ',
                        yaxis_title='عدد الحالات',
                        height=400,
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig5, use_container_width=True)
                except Exception as e:
                    st.warning(f"⚠️ تعذر إنشاء المخطط الزمني: {str(e)}")
        
        # جدول إحصائي
        st.markdown('<div class="section-title">📋 ملخص إحصائي</div>', unsafe_allow_html=True)
        
        summary_data = {
            'المقياس': [
                'إجمالي الحالات',
                'الحالات الخبيثة',
                'الحالات الحميدة',
                'نسبة الخبيث',
                'نسبة الحميد',
                'متوسط العمر',
                'أصغر عمر',
                'أكبر عمر'
            ],
            'القيمة': [
                total_patients,
                malignant_cases,
                benign_cases,
                f"{(malignant_cases/total_patients*100):.1f}%" if total_patients > 0 else "0%",
                f"{(benign_cases/total_patients*100):.1f}%" if total_patients > 0 else "0%",
                f"{df['age'].mean():.1f}" if total_patients > 0 else "0",
                f"{df['age'].min()}" if total_patients > 0 else "0",
                f"{df['age'].max()}" if total_patients > 0 else "0"
            ]
        }
        
        if 'probability_1' in df.columns and total_patients > 0:
            summary_data['المقياس'].extend(['متوسط نسبة الخطورة', 'أعلى نسبة خطورة', 'أقل نسبة خطورة'])
            summary_data['القيمة'].extend([
                f"{df['probability_1'].mean():.1f}%",
                f"{df['probability_1'].max():.1f}%",
                f"{df['probability_1'].min():.1f}%"
            ])
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    else:
        st.info("📊 لا توجد بيانات كافية لعرض الإحصائيات")

def show_system_management(predictor, auth_system):
    """عرض صفحة إدارة النظام"""
    st.markdown('<h1 class="main-title">⚙️ إدارة النظام</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["النموذج الطبي", "إعدادات النظام", "النسخ الاحتياطي"])
    
    with tab1:
        st.markdown("### 📊 حالة النموذج الطبي")
        
        col1, col2 = st.columns(2)
        
        with col1:
            model_status = "✅ محمل" if predictor.model_loaded else "❌ غير محمل"
            st.metric("حالة النموذج", model_status)
        
        with col2:
            features_count = len(predictor.features) if predictor.features else 0
            st.metric("عدد الميزات", features_count)
        
        st.markdown("---")
        
        # إعدادات تحميل النموذج
        st.markdown("### 📁 إعدادات الملفات")
        
        col_path1, col_path2, col_path3 = st.columns(3)
        
        with col_path1:
            model_path = st.text_input("مسار النموذج", value="logistic_model.pkl")
        
        with col_path2:
            scaler_path = st.text_input("مسار الـ Scaler", value="scaler.pkl")
        
        with col_path3:
            features_path = st.text_input("مسار أسماء الميزات", value="feature_names.json")
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("🔄 تحميل النموذج", use_container_width=True):
                with st.spinner("جاري تحميل النموذج..."):
                    if predictor.load_model(model_path, scaler_path, features_path):
                        st.success("✅ تم تحميل النموذج بنجاح!")
                        st.rerun()
        
        with col_btn2:
            if st.button("🔍 فحص الملفات", use_container_width=True):
                files_info = []
                for path, name in [(model_path, "النموذج"), (scaler_path, "الـ Scaler"), (features_path, "أسماء الميزات")]:
                    if os.path.exists(path):
                        size = os.path.getsize(path) / 1024  # KB
                        files_info.append(f"✅ {name}: موجود ({size:.1f} KB)")
                    else:
                        files_info.append(f"❌ {name}: غير موجود")
                
                for info in files_info:
                    st.write(info)
        
        with col_btn3:
            if st.button("🧹 مسح الذاكرة المؤقتة", use_container_width=True):
                if 'predictor' in st.session_state:
                    del st.session_state['predictor']
                st.success("✅ تم مسح الذاكرة المؤقتة")
                st.rerun()
        
        # معلومات إضافية عن النموذج
        if predictor.model_loaded and predictor.model is not None:
            st.markdown("---")
            st.markdown("### ℹ️ معلومات النموذج")
            
            try:
                model_type = type(predictor.model).__name__
                st.write(f"**نوع النموذج:** {model_type}")
                
                if hasattr(predictor.model, 'coef_'):
                    num_coefficients = len(predictor.model.coef_[0])
                    st.write(f"**عدد المعاملات:** {num_coefficients}")
                
                if hasattr(predictor.model, 'intercept_'):
                    st.write(f"**قيمة التقاطع:** {predictor.model.intercept_[0]:.4f}")
                
            except Exception as e:
                st.write(f"**ملاحظة:** تعذر استخراج معلومات النموذج: {str(e)}")
    
    with tab2:
        st.markdown("### ⚙️ إعدادات عامة")
        
        # إعدادات الواجهة
        st.markdown("#### 🎨 إعدادات الواجهة")
        
        col_ui1, col_ui2 = st.columns(2)
        
        with col_ui1:
            theme = st.selectbox("السمة", ["فاتح", "غامق", "تلقائي"])
        
        with col_ui2:
            language = st.selectbox("اللغة", ["العربية", "الإنجليزية"])
        
        # إعدادات البيانات
        st.markdown("#### 💾 إعدادات البيانات")
        
        col_data1, col_data2 = st.columns(2)
        
        with col_data1:
            auto_save = st.checkbox("الحفظ التلقائي", value=True)
        
        with col_data2:
            backup_frequency = st.selectbox("تكرار النسخ الاحتياطي", ["يومي", "أسبوعي", "شهري"])
        
        if st.button("💾 حفظ الإعدادات", use_container_width=True):
            st.success("✅ تم حفظ الإعدادات بنجاح")
    
    with tab3:
        st.markdown("### 💾 النسخ الاحتياطي")
        
        col_backup1, col_backup2 = st.columns(2)
        
        with col_backup1:
            if st.button("📥 إنشاء نسخة احتياطية", use_container_width=True):
                try:
                    # محاكاة إنشاء نسخة احتياطية
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_files = []
                    
                    for file in ['patient_records.csv', 'logistic_model.pkl', 'scaler.pkl', 'feature_names.json']:
                        if os.path.exists(file):
                            backup_files.append(file)
                    
                    if backup_files:
                        st.success(f"✅ تم إنشاء نسخة احتياطية لـ {len(backup_files)} ملفات")
                        st.info(f"**الملفات المضمنة:** {', '.join(backup_files)}")
                    else:
                        st.warning("⚠️ لم يتم العثور على ملفات للنسخ الاحتياطي")
                
                except Exception as e:
                    st.error(f"❌ فشل في إنشاء النسخة الاحتياطية: {str(e)}")
        
        with col_backup2:
            if st.button("📤 استعادة نسخة احتياطية", use_container_width=True):
                st.info("🚧 هذه الميزة قيد التطوير")
        
        # قائمة النسخ الاحتياطية المتاحة
        st.markdown("#### 📋 النسخ الاحتياطية المتاحة")
        
        backup_data = [
            {"التاريخ": "2024-01-15", "الحجم": "2.3 MB", "الملفات": "4"},
            {"التاريخ": "2024-01-08", "الحجم": "2.1 MB", "الملفات": "4"},
            {"التاريخ": "2024-01-01", "الحجم": "1.9 MB", "الملفات": "4"},
        ]
        
        if backup_data:
            backup_df = pd.DataFrame(backup_data)
            st.dataframe(backup_df, use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد نسخ احتياطية متاحة")

def show_user_management(auth_system):
    """عرض صفحة إدارة المستخدمين (للمشرف فقط)"""
    if st.session_state.get("role") != "admin":
        st.error("❌ غير مصرح بالوصول إلى هذه الصفحة")
        return
    
    st.markdown('<h1 class="main-title">👥 إدارة المستخدمين</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["المستخدمين الحاليين", "إضافة مستخدم جديد", "سجل النشاط"])
    
    with tab1:
        st.markdown("### 📋 قائمة المستخدمين")
        
        users_data = []
        for username, role in auth_system.user_roles.items():
            users_data.append({
                "اسم المستخدم": username,
                "الدور": role,
                "الحالة": "نشط"
            })
        
        if users_data:
            users_df = pd.DataFrame(users_data)
            st.dataframe(users_df, use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد مستخدمين مسجلين")
    
    with tab2:
        st.markdown("### ➕ إضافة مستخدم جديد")
        
        col_user1, col_user2 = st.columns(2)
        
        with col_user1:
            new_username = st.text_input("اسم المستخدم الجديد", placeholder="أدخل اسم المستخدم")
        
        with col_user2:
            new_role = st.selectbox("الدور", ["طبيب", "مساعد طبي", "إداري"])
        
        new_password = st.text_input("كلمة المرور", type="password", placeholder="أدخل كلمة مرور قوية")
        confirm_password = st.text_input("تأكيد كلمة المرور", type="password", placeholder="أعد إدخال كلمة المرور")
        
        if st.button("➕ إضافة المستخدم", use_container_width=True):
            if not new_username or not new_password:
                st.error("❌ يرجى إدخال جميع الحقول")
            elif new_password != confirm_password:
                st.error("❌ كلمات المرور غير متطابقة")
            else:
                if auth_system.add_user(new_username, new_password, new_role):
                    st.success(f"✅ تم إضافة المستخدم '{new_username}' بنجاح")
                else:
                    st.error(f"❌ اسم المستخدم '{new_username}' موجود مسبقاً")
    
    with tab3:
        st.markdown("### 📊 سجل النشاط")
        
        # محاكاة سجل النشاط
        activity_data = [
            {"التاريخ": "2024-01-15 10:30", "المستخدم": "dr.ahmed", "النشاط": "تسجيل دخول", "التفاصيل": "الدخول إلى النظام"},
            {"التاريخ": "2024-01-15 11:45", "المستخدم": "dr.ahmed", "النشاط": "تشخيص مريض", "التفاصيل": "تشخيص حالة جديدة (PAT0012)"},
            {"التاريخ": "2024-01-14 09:15", "المستخدم": "dr.amira", "النشاط": "تسجيل دخول", "التفاصيل": "الدخول إلى النظام"},
            {"التاريخ": "2024-01-14 14:20", "المستخدم": "dr.amira", "النشاط": "تصدير بيانات", "التفاصيل": "تصدير سجلات المرضى"},
            {"التاريخ": "2024-01-13 16:10", "المستخدم": "admin", "النشاط": "إدارة النظام", "التفاصيل": "تحديث إعدادات النظام"},
        ]
        
        activity_df = pd.DataFrame(activity_data)
        st.dataframe(activity_df, use_container_width=True, height=300)

def show_medical_info():
    """عرض المعلومات الطبية"""
    st.markdown('<h1 class="main-title">ℹ️ معلومات طبية</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["سرطان الثدي", "أنواع الأورام", "الفحوصات", "الوقاية"])
    
    with tab1:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 🎗️ سرطان الثدي")
            st.write("سرطان الثدي هو نمو غير طبيعي لخلايا أنسجة الثدي يبدأ عادة في قنوات الحليب أو الفصوص.")
            
            st.markdown("#### 📊 الإحصائيات:")
            st.markdown("""
            - أكثر أنواع السرطان شيوعاً لدى النساء عالمياً
            - يمثل حوالي 25% من جميع حالات السرطان لدى النساء  
            - تزداد نسبة الإصابة مع التقدم في العمر
            - يمكن اكتشافه مبكراً وعلاجه بنجاح في معظم الحالات
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            with st.container():
                st.markdown('<div class="medical-card">', unsafe_allow_html=True)
                st.markdown("#### ✅ أورام حميدة (غير سرطانية)")
                st.markdown("""
                - **الورم الغدي الليفي:** أكثر أورام الثدي الحميدة شيوعاً
                - **تكيسات الثدي:** أكياس مليئة بالسوائل
                - **التهاب الضرع:** التهاب أنسجة الثدي
                - **الورم الحليمي القنوي:** نمو صغير داخل قنوات الحليب
                """)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            with st.container():
                st.markdown('<div class="medical-card">', unsafe_allow_html=True)
                st.markdown("#### ⚠️ أورام خبيثة (سرطانية)")
                st.markdown("""
                - **سرطان القنوات:** الأكثر شيوعاً (80% من الحالات)
                - **سرطان الفصوص:** يبدأ في فصوص الثدي
                - **السرطان الالتهابي:** نادر وسريع الانتشار
                - **سرطان باجيت:** يصيب حلمة الثدي
                """)
                st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 🔍 الفحوصات الدورية")
            
            st.markdown("#### 1. الفحص الذاتي:")
            st.markdown("""
            - يجب إجراؤه شهرياً بعد انتهاء الدورة الشهرية
            - البحث عن كتل، تغيرات في الجلد، إفرازات
            """)
            
            st.markdown("#### 2. الفحص السريري:")
            st.markdown("""
            - من قبل الطبيب كل 1-3 سنوات للنساء فوق 20 سنة
            - سنوياً للنساء فوق 40 سنة
            """)
            
            st.markdown("#### 3. التصوير الإشعاعي (الماموجرام):")
            st.markdown("""
            - كل 1-2 سنوات للنساء 40-49 سنة
            - سنوياً للنساء فوق 50 سنة
            """)
            
            st.markdown("#### 4. الموجات فوق الصوتية:")
            st.markdown("""
            - مكمل للماموجرام خاصة للنساء ذوات الثدي الكثيف
            """)
            
            st.markdown("#### 5. الرنين المغناطيسي:")
            st.markdown("""
            - للحالات عالية الخطورة فقط
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        col_pre1, col_pre2 = st.columns(2)
        
        with col_pre1:
            with st.container():
                st.markdown('<div class="medical-card">', unsafe_allow_html=True)
                st.markdown("#### ✅ عوامل الوقاية")
                st.markdown("""
                - الحفاظ على وزن صحي
                - ممارسة النشاط البدني بانتظام
                - الرضاعة الطبيعية
                - تجنب التدخين والكحول
                - التغذية الصحية الغنية بالفواكه والخضروات
                """)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col_pre2:
            with st.container():
                st.markdown('<div class="medical-card">', unsafe_allow_html=True)
                st.markdown("#### ⚠️ عوامل الخطورة")
                st.markdown("""
                - التاريخ العائلي للمرض
                - العمر (فوق 50 سنة)
                - البدء المبكر للدورة الشهرية
                - انقطاع الطمث المتأخر
                - العلاج الهرموني لفترات طويلة
                - التعرض للإشعاع
                """)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("#### 📞 متى تزور الطبيب؟")
            st.write("يجب مراجعة الطبيب فوراً عند ملاحظة أي من هذه الأعراض:")
            st.markdown("""
            - كتلة جديدة في الثدي أو تحت الإبط
            - تغير في حجم أو شكل الثدي
            - إفرازات من الحلمة (خاصة الدموية)
            - تغيرات في جلد الثدي (تجعد، احمرار، تقشر)
            - ألم مستمر في الثدي أو الحلمة
            """)
            st.markdown('</div>', unsafe_allow_html=True)
def main():
    """الدالة الرئيسية للتطبيق"""
    
    # تهيئة نظام المصادقة
    auth_system = AuthenticationSystem()
    
    # تهيئة حالة الجلسة
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    # إنشاء وتحميل النموذج
    predictor = BreastCancerPredictor()
    
    # تخزين النموذج في حالة الجلسة
    if 'predictor' not in st.session_state:
        st.session_state['predictor'] = predictor
    
    # استخدام النموذج من حالة الجلسة
    predictor = st.session_state['predictor']
    
    # عرض الواجهة المناسبة
    if not st.session_state['logged_in']:
        show_login_page(auth_system)
    else:
        show_doctor_dashboard(auth_system, predictor)

if __name__ == "__main__":
    main()