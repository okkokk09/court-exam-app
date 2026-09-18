# -*- coding: utf-8 -*-
import importlib
import streamlit as st
import db
import quiz_engine
import styles
import views.exam_view
import views.review_view
import views.practice_view
import views.stats_view
import views.manage_view

# Ensure hot-reload resilience on Streamlit Cloud
importlib.reload(db)
importlib.reload(quiz_engine)
importlib.reload(styles)
importlib.reload(views.exam_view)
importlib.reload(views.review_view)
importlib.reload(views.practice_view)
importlib.reload(views.stats_view)
importlib.reload(views.manage_view)

from views.exam_view import render_exam_view
from views.review_view import render_review_view
from views.practice_view import render_practice_view
from views.stats_view import render_stats_view
from views.manage_view import render_manage_view

# 1. Initialize Session State
quiz_engine.init_session_state(st.session_state)

# 2. Page Configuration
cur_subject = st.session_state.get('selected_subject', 'law')
is_com_subj = (cur_subject == 'computer')
is_full_page = (st.session_state.get('current_page') == 'full_exam') or (st.session_state.get('exam_active') and st.session_state.get('exam_mode') == 'full_simulation')

if is_full_page:
    page_title = "จำลองสอบจริงเต็มรูปแบบ ศาลยุติธรรม (200 คะแนน 180 นาที)"
    page_icon = "🏆"
elif is_com_subj:
    page_title = "ฝึกทำข้อสอบ คอมพิวเตอร์และเทคโนโลยีสารสนเทศ"
    page_icon = "💻"
else:
    page_title = "ฝึกทำข้อสอบ กฎหมายระเบียบบริหารราชการศาลยุติธรรม"
    page_icon = "⚖️"

st.set_page_config(
    page_title=page_title,
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# 3. Theme State & Dynamic CSS Injection
current_theme = st.session_state.get('selected_theme', 'court_navy')
st.markdown(styles.get_custom_css(current_theme), unsafe_allow_html=True)

# 4. App Header Banner
if is_full_page:
    header_html = '''<div class="app-header" style="background: linear-gradient(135deg, #0b2239 0%, #1e3a8a 50%, #1e40af 100%); border-left: 5px solid #d4af37;">
<div>
<h1 style="color: #fef08a;">🏆 ระบบจำลองสอบจริงเต็มรูปแบบ ศาลยุติธรรม (200 คะแนน 180 นาที)</h1>
<p style="color: #e2e8f0;">ภาคความรู้ความสามารถเฉพาะตำแหน่ง | ข้อ 1-30: กฎหมายระเบียบศาลฯ (60 คะแนน) • ข้อ 31-100: คอมพิวเตอร์และสารสนเทศ (140 คะแนน)</p>
</div>
<div style="text-align: right;">
<span class="nav-badge" style="background: rgba(212, 175, 55, 0.25); border-color: #d4af37; color: #fef08a;">FULL EXAM 200 PTS</span>
</div>
</div>'''
elif is_com_subj:
    header_html = '''<div class="app-header">
<div>
<h1>💻 ระบบฝึกทำข้อสอบ คอมพิวเตอร์และเทคโนโลยีสารสนเทศ</h1>
<p>ฮาร์ดแวร์ ซอฟต์แวร์ MS Office เครือข่าย ความปลอดภัยไซเบอร์ พ.ร.บ.คอมฯ และ AI | เตรียมสอบศาลยุติธรรมและข้าราชการ</p>
</div>
<div style="text-align: right;">
<span class="nav-badge">COMPUTER & IT EXAM PREP</span>
</div>
</div>'''
else:
    header_html = '''<div class="app-header">
<div>
<h1>⚖️ ระบบฝึกทำข้อสอบ กฎหมายระเบียบบริหารราชการศาลยุติธรรม</h1>
<p>พ.ร.บ. ระเบียบบริหารราชการศาลยุติธรรม พ.ศ. ๒๕๔๓ (และฉบับแก้ไขเพิ่มเติม) | เตรียมสอบเจ้าพนักงานศาลยุติธรรมและนิติกร</p>
</div>
<div style="text-align: right;">
<span class="nav-badge">COURT OF JUSTICE EXAM PREP</span>
</div>
</div>'''
st.markdown(header_html, unsafe_allow_html=True)

def switch_subject(new_subj):
    st.session_state.selected_subject = new_subj
    st.session_state.exam_subject = new_subj
    st.session_state.exam_active = False
    st.session_state.exam_submitted = False
    st.session_state.practice_q_idx = 0
    st.session_state.review_q_idx = 0
    st.session_state.practice_selected = None
    st.session_state.practice_show_answer = False
    st.session_state.review_selected = None
    st.session_state.review_show_answer = False

# 5. Quick Subject Switcher Buttons (Top Toolbar - Only shown for single-subject pages)
if not is_full_page:
    col_btn1, col_btn2, col_blank = st.columns([1.3, 1.3, 2.4])
    with col_btn1:
        law_type = "primary" if not is_com_subj else "secondary"
        if st.button("⚖️ วิชากฎหมายศาลยุติธรรม", type=law_type, use_container_width=True, disabled=st.session_state.get('exam_active', False)):
            if st.session_state.selected_subject != 'law':
                switch_subject('law')
                st.rerun()

    with col_btn2:
        com_type = "primary" if is_com_subj else "secondary"
        if st.button("💻 วิชาคอมพิวเตอร์และสารสนเทศ", type=com_type, use_container_width=True, disabled=st.session_state.get('exam_active', False)):
            if st.session_state.selected_subject != 'computer':
                switch_subject('computer')
                st.rerun()

    st.write("")

# 6. Sidebar Navigation
with st.sidebar:
    sidebar_icon = "🏆" if is_full_page else ("💻" if is_com_subj else "🏛️")
    sidebar_title = "สอบจริงเต็มรูปแบบ" if is_full_page else ("วิชาคอมพิวเตอร์" if is_com_subj else "ศาลยุติธรรม")
    st.markdown(f'''<div style="text-align: center; padding: 10px 0 16px 0;">
<div style="font-size: 2.5rem;">{sidebar_icon}</div>
<h3 style="margin: 4px 0 0 0; color: #1e3a8a;">{sidebar_title}</h3>
<p style="font-size: 0.82rem; color: #64748b; margin: 0;">ระบบจำลองสอบ & ทบทวนข้อผิดซ้ำ</p>
</div>''', unsafe_allow_html=True)
    
    # Fixed user profile to 'เฟิส'
    st.session_state.current_user = 'เฟิส'
    
    # Subject Switcher in Sidebar
    if is_full_page:
        st.markdown('''<div style="background: rgba(212, 175, 55, 0.12); border: 1.5px solid #d4af37; border-radius: 10px; padding: 10px 12px; margin-bottom: 8px; text-align: center;">
<div style="font-weight: 700; color: #d97706; font-size: 0.88rem;">🏆 รวม 2 หมวดวิชา (100 ข้อ)</div>
<div style="font-size: 0.78rem; color: #64748b; margin-top: 3px;">ข้อ 1-30: กฎหมาย (60 คะแนน)<br>ข้อ 31-100: คอมพิวเตอร์ (140 คะแนน)</div>
</div>''', unsafe_allow_html=True)
    elif st.session_state.get('exam_active', False) and not st.session_state.get('exam_submitted', False):
        active_subj = st.session_state.get('exam_subject', cur_subject)
        is_active_com = (active_subj == 'computer')
        badge_color = '#0284c7' if is_active_com else '#1e40af'
        badge_bg = '#e0f2fe' if is_active_com else '#eff6ff'
        badge_title = '💻 กำลังสอบ: วิชาคอมพิวเตอร์และสารสนเทศ' if is_active_com else '⚖️ กำลังสอบ: วิชากฎหมายศาลยุติธรรม'
        st.markdown(f'''<div style="background: {badge_bg}; border: 1.5px solid {badge_color}; border-radius: 10px; padding: 10px 12px; margin-bottom: 8px; text-align: center;">
<div style="font-weight: 700; color: {badge_color}; font-size: 0.88rem;">{badge_title}</div>
<div style="font-size: 0.78rem; color: #64748b; margin-top: 3px;">ข้อสอบกำลังดำเนินอยู่</div>
</div>''', unsafe_allow_html=True)
    else:
        st.markdown("**📖 เลือกวิชาข้อสอบ (Subject):**")
        subject_options = {
            'law': '⚖️ กฎหมายศาลยุติธรรม (พ.ร.บ. 2543)',
            'computer': '💻 คอมพิวเตอร์ & สารสนเทศ'
        }
        chosen_subj = st.radio(
            "Subject Selection",
            options=list(subject_options.keys()),
            format_func=lambda x: subject_options[x],
            index=list(subject_options.keys()).index(cur_subject) if cur_subject in subject_options else 0,
            label_visibility="collapsed"
        )
        if chosen_subj != st.session_state.selected_subject:
            switch_subject(chosen_subj)
            st.rerun()
        
    st.write("---")
    st.markdown("**📌 เลือกโหมดการทำงาน:**")
    
    nav_options = {
        'full_exam': '🏆 สอบจริงเต็มรูปแบบ (200 คะแนน 180 นาที)',
        'exam': '🏛️ จำลองสอบรายวิชา (Quick Exam)',
        'review': '🔄 ทบทวนข้อผิดซ้ำ (Mistake Bank)',
        'practice': '📚 ฝึกทำแยกหมวดหมู่ (Practice)',
        'stats': '📊 แดชบอร์ดสถิติ & จุดอ่อน',
        'manage': '⚙️ คลังข้อสอบ & จัดการ'
    }
    
    # Handle page switching
    current_key = st.session_state.current_page
    if current_key not in nav_options:
        current_key = 'exam'
        st.session_state.current_page = 'exam'
        
    selected_page = st.radio(
        "Navigation",
        options=list(nav_options.keys()),
        format_func=lambda x: nav_options[x],
        index=list(nav_options.keys()).index(current_key),
        label_visibility="collapsed"
    )
    
    if selected_page != st.session_state.current_page:
        # If user is in an active exam, ask before leaving
        if st.session_state.exam_active and not st.session_state.exam_submitted:
            st.warning("⚠️ การเปลี่ยนหน้าจะทำให้การสอบรอบปัจจุบันสิ้นสุดลง")
            if st.button("ยืนยันเปลี่ยนหน้า", type="primary"):
                st.session_state.exam_active = False
                st.session_state.current_page = selected_page
                st.rerun()
        else:
            st.session_state.current_page = selected_page
            st.rerun()
            
    st.write("---")
    
    # Theme Customizer Widget
    st.markdown("**🎨 เลือกธีมสีข้อสอบ (Theme):**")
    theme_keys = list(styles.THEMES.keys())
    cur_theme_idx = theme_keys.index(st.session_state.selected_theme) if st.session_state.selected_theme in theme_keys else 0
    
    chosen_theme = st.selectbox(
        "เลือกธีมสี:",
        options=theme_keys,
        format_func=lambda k: styles.THEMES[k]['name'],
        index=cur_theme_idx,
        key="theme_selector_dropdown",
        label_visibility="collapsed"
    )
    if chosen_theme != st.session_state.selected_theme:
        st.session_state.selected_theme = chosen_theme
        st.rerun()
        
    st.write("---")
    
    # Choice Randomizer Widget
    st.markdown("**🔀 สลับตำแหน่งตัวเลือก (Choice Randomizer):**")
    cur_shuffle = st.session_state.get('shuffle_options', True)
    new_shuffle = st.toggle(
        "สลับตัวเลือก (ก-ง) ทุกครั้ง",
        value=cur_shuffle,
        key="shuffle_choices_sidebar_toggle",
        help="สุ่มสลับตำแหน่งตัวเลือก ก, ข, ค, ง ทุกครั้งที่เริ่มทำข้อสอบ เพื่อป้องกันการท่องจำตำแหน่ง"
    )
    if new_shuffle != cur_shuffle:
        st.session_state.shuffle_options = new_shuffle
        st.rerun()
        
    st.write("---")
    
    # Sidebar Quick Stats Widget
    active_user = st.session_state.get('current_user', 'เฟิส')
    if is_full_page:
        if not hasattr(db, 'get_full_simulation_stats'):
            importlib.reload(db)
        if hasattr(db, 'get_full_simulation_stats'):
            f_stats = db.get_full_simulation_stats(username=active_user)
        else:
            f_stats = {
                'total_bank_questions': 0, 'total_exams': 0, 'avg_score': 0.0,
                'max_points': 0, 'avg_points': 0.0, 'passed_count': 0, 'top10_count': 0,
                'latest_session': None, 'recent_sessions': [], 'mistake_count': 0,
                'mastered_count': 0, 'practiced_count': 0, 'overall_accuracy': 0.0
            }
        st.markdown(f'''
        <div style="background: #f1f5f9; padding: 14px; border-radius: 12px; font-size: 0.85rem; border: 1px solid #e2e8f0;">
            <div style="font-weight: 700; color: #0f172a; margin-bottom: 6px;">📈 สรุปสอบจริงเต็มรูปแบบ</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #64748b;">สอบไปแล้ว:</span>
                <b>{f_stats.get('total_exams', 0)} ครั้ง</b>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #64748b;">คะแนนสูงสุด:</span>
                <b style="color: #059669;">{f_stats.get('max_points', 0)} / 200 คะแนน</b>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #64748b;">คะแนนเฉลี่ย:</span>
                <b style="color: #d97706;">{f_stats.get('avg_points', 0.0)} / 200 คะแนน</b>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #64748b;">ข้อผิดค้างทบทวน:</span>
                <b style="color: #ef4444;">{f_stats.get('mistake_count', 0)} ข้อ</b>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        db_stats = db.get_dashboard_stats(subject=cur_subject, username=active_user)
        st.markdown(f'''
        <div style="background: #f1f5f9; padding: 14px; border-radius: 12px; font-size: 0.85rem; border: 1px solid #e2e8f0;">
            <div style="font-weight: 700; color: #0f172a; margin-bottom: 6px;">📈 สรุปภาพรวม ({ "คอมพิวเตอร์" if is_com_subj else "กฎหมายศาล" })</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #64748b;">คลังข้อสอบ:</span>
                <b>{db_stats['total_bank_questions']} ข้อ</b>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #64748b;">ฝึกไปแล้ว:</span>
                <b>{db_stats['practiced_count']} ข้อ</b>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #64748b;">ข้อผิดค้างทบทวน:</span>
                <b style="color: #ef4444;">{db_stats['mistake_count']} ข้อ</b>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #64748b;">ความแม่นยำ:</span>
                <b style="color: #10b981;">{db_stats['overall_accuracy']}%</b>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.write("")
    st.caption("พัฒนาสำหรับเตรียมสอบข้าราชการศาลยุติธรรม © 2026")

# 7. Main View Router
if st.session_state.current_page in ('exam', 'full_exam'):
    render_exam_view()
elif st.session_state.current_page == 'review':
    render_review_view()
elif st.session_state.current_page == 'practice':
    render_practice_view()
elif st.session_state.current_page == 'stats':
    render_stats_view()
elif st.session_state.current_page == 'manage':
    render_manage_view()

