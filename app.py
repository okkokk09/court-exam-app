# -*- coding: utf-8 -*-
import importlib
import streamlit as st
import db
import quiz_engine
import styles
import exam_config
import views.exam_view
import views.review_view
import views.practice_view
import views.stats_view
import views.manage_view
import views.knowledge_view
import views.subjective_view

# Ensure hot-reload resilience on Streamlit Cloud
importlib.reload(db)
importlib.reload(quiz_engine)
importlib.reload(styles)
importlib.reload(exam_config)
importlib.reload(views.exam_view)
importlib.reload(views.review_view)
importlib.reload(views.practice_view)
importlib.reload(views.stats_view)
importlib.reload(views.manage_view)
importlib.reload(views.knowledge_view)
importlib.reload(views.subjective_view)

from views.exam_view import render_exam_view
from views.review_view import render_review_view
from views.practice_view import render_practice_view
from views.stats_view import render_stats_view
from views.manage_view import render_manage_view
from views.knowledge_view import render_knowledge_view
from views.subjective_view import render_subjective_view

# 1. Initialize Session State
quiz_engine.init_session_state(st.session_state)

# 2. Page Configuration
if 'exam_category' not in st.session_state:
    st.session_state.exam_category = exam_config.DEFAULT_CATEGORY
exam_cfg = exam_config.get_active(st.session_state)
full_exam_enabled = exam_cfg.get('full_exam_enabled', True)
if not full_exam_enabled and st.session_state.get('current_page') == 'full_exam':
    st.session_state.current_page = 'exam'

cur_subject = st.session_state.get('selected_subject', 'law')
is_com_subj = (cur_subject == 'computer')
is_full_page = (st.session_state.get('current_page') == 'full_exam') or (st.session_state.get('exam_active') and st.session_state.get('exam_mode') == 'full_simulation')
is_subjective_page = (st.session_state.get('current_page') == 'subjective')
is_knowledge_page = (st.session_state.get('current_page') == 'knowledge')

if is_full_page:
    page_title = f"จำลองสอบจริงเต็มรูปแบบ {exam_cfg['short_name']} (200 คะแนน 180 นาที)"
    page_icon = "🏆"
elif is_subjective_page:
    page_title = f"สนามฝึกข้อเขียนอัตนัย 100 คะแนน | {exam_cfg['short_name']}"
    page_icon = "✍️"
elif is_knowledge_page:
    page_title = f"คลังสรุปจุดหลอกกฎหมาย | {exam_cfg['short_name']}"
    page_icon = "📖"
elif is_com_subj:
    page_title = f"{exam_cfg['name']} | วิชา{exam_cfg['computer_label']}"
    page_icon = "💻"
else:
    page_title = f"{exam_cfg['name']} | วิชา{exam_cfg['law_label']}"
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
    header_html = f'''<div class="app-header" style="background: linear-gradient(135deg, #0b2239 0%, #1e3a8a 50%, #1e40af 100%); border-left: 5px solid #d4af37;">
<div>
<h1 style="color: #fef08a;">🏆 ระบบจำลองสอบจริงเต็มรูปแบบ {exam_cfg['short_name']} (200 คะแนน 180 นาที)</h1>
<p style="color: #e2e8f0;">ภาคความรู้ความสามารถเฉพาะตำแหน่ง | ข้อ 1-30: {exam_cfg['law_short']} (60 คะแนน) • ข้อ 31-100: {exam_cfg['computer_short']} (140 คะแนน)</p>
</div>
<div style="text-align: right;">
<span class="nav-badge" style="background: rgba(212, 175, 55, 0.25); border-color: #d4af37; color: #fef08a;">FULL EXAM 200 PTS</span>
</div>
</div>'''
elif is_subjective_page:
    header_html = f'''<div class="app-header" style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%); border-left: 5px solid #818cf8;">
<div>
<h1 style="color: #ffffff;">✍️ สนามฝึกข้อเขียนอัตนัย (Subjective Exam Lab - 100 คะแนน)</h1>
<p style="color: #c7d2fe;">SQL Query Lab (SQLite) • ER-Diagram & System Design (Mermaid.js) • Code & Security Vulnerability Fix (OWASP)</p>
</div>
<div style="text-align: right;">
<span class="nav-badge" style="background: rgba(129, 140, 248, 0.25); border-color: #818cf8; color: #e0e7ff;">SUBJECTIVE 100 PTS</span>
</div>
</div>'''
elif is_knowledge_page:
    header_html = f'''<div class="app-header" style="background: linear-gradient(135deg, #14532d 0%, #166534 50%, #15803d 100%); border-left: 5px solid #4ade80;">
<div>
<h1 style="color: #ffffff;">📖 คลังสรุปจุดหลอกกฎหมาย (OAG Legal Traps & Cheatsheets)</h1>
<p style="color: #bbf7d0;">สรุปประเด็นตัวเลข โครงสร้างองค์กร อำนาจหน้าที่ และจุดที่มักออกข้อสอบหลอก สำหรับสำนักงานอัยการสูงสุด</p>
</div>
<div style="text-align: right;">
<span class="nav-badge" style="background: rgba(74, 222, 128, 0.25); border-color: #4ade80; color: #f0fdf4;">KNOWLEDGE BASE</span>
</div>
</div>'''
elif is_com_subj:
    header_html = f'''<div class="app-header">
<div>
<h1>💻 {exam_cfg['name']} — วิชา{exam_cfg['computer_label']}</h1>
<p>ตำแหน่ง{exam_cfg['position']} | {exam_cfg['computer_desc']}</p>
</div>
<div style="text-align: right;">
<span class="nav-badge">{exam_cfg['badge']}</span>
</div>
</div>'''
else:
    header_html = f'''<div class="app-header">
<div>
<h1>⚖️ {exam_cfg['name']} — วิชา{exam_cfg['law_label']}</h1>
<p>ตำแหน่ง{exam_cfg['position']} | {exam_cfg['law_desc']}</p>
</div>
<div style="text-align: right;">
<span class="nav-badge">{exam_cfg['badge']}</span>
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
if not is_full_page and not is_subjective_page and not is_knowledge_page:
    col_btn1, col_btn2, col_blank = st.columns([1.3, 1.3, 2.4])
    with col_btn1:
        law_type = "primary" if not is_com_subj else "secondary"
        if st.button(f"⚖️ วิชา{exam_cfg['law_short']}", type=law_type, use_container_width=True, disabled=st.session_state.get('exam_active', False)):
            if st.session_state.selected_subject != 'law':
                switch_subject('law')
                st.rerun()

    with col_btn2:
        com_type = "primary" if is_com_subj else "secondary"
        if st.button(f"💻 วิชา{exam_cfg['computer_short']}", type=com_type, use_container_width=True, disabled=st.session_state.get('exam_active', False)):
            if st.session_state.selected_subject != 'computer':
                switch_subject('computer')
                st.rerun()

    st.write("")

# 6. Sidebar Navigation
with st.sidebar:
    sidebar_icon = "🏆" if is_full_page else ("✍️" if is_subjective_page else ("📖" if is_knowledge_page else ("💻" if is_com_subj else exam_cfg['icon'])))
    sidebar_title = "สอบจริงเต็มรูปแบบ" if is_full_page else ("ข้อเขียนอัตนัย" if is_subjective_page else ("จุดหลอกกฎหมาย" if is_knowledge_page else ("วิชาคอมพิวเตอร์" if is_com_subj else exam_cfg['short_name'])))
    st.markdown(f'''<div style="text-align: center; padding: 10px 0 16px 0;">
<div style="font-size: 2.5rem;">{sidebar_icon}</div>
<h3 style="margin: 4px 0 0 0; color: #1e3a8a;">{sidebar_title}</h3>
<p style="font-size: 0.82rem; color: #64748b; margin: 0;">ตำแหน่ง{exam_cfg['position']}</p>
</div>''', unsafe_allow_html=True)
    
    # Fixed user profile to 'เฟิส'
    st.session_state.current_user = 'เฟิส'
    
    # Subject Switcher in Sidebar
    if is_full_page:
        st.markdown(f'''<div style="background: rgba(212, 175, 55, 0.12); border: 1.5px solid #d4af37; border-radius: 10px; padding: 10px 12px; margin-bottom: 8px; text-align: center;">
<div style="font-weight: 700; color: #d97706; font-size: 0.88rem;">🏆 รวม 2 หมวดวิชา (100 ข้อ)</div>
<div style="font-size: 0.78rem; color: #64748b; margin-top: 3px;">ข้อ 1-30: {exam_cfg['law_short']} (60 คะแนน)<br>ข้อ 31-100: คอมพิวเตอร์ (140 คะแนน)</div>
</div>''', unsafe_allow_html=True)
    elif is_subjective_page:
        st.markdown(f'''<div style="background: #eef2ff; border: 1.5px solid #6366f1; border-radius: 10px; padding: 10px 12px; margin-bottom: 8px; text-align: center;">
<div style="font-weight: 700; color: #4338ca; font-size: 0.88rem;">✍️ ฝึกข้อเขียนอัตนัย (100 คะแนน)</div>
<div style="font-size: 0.78rem; color: #64748b; margin-top: 3px;">SQL Lab • ERD Design • Code Fix</div>
</div>''', unsafe_allow_html=True)
    elif is_knowledge_page:
        st.markdown(f'''<div style="background: #f0fdf4; border: 1.5px solid #22c55e; border-radius: 10px; padding: 10px 12px; margin-bottom: 8px; text-align: center;">
<div style="font-weight: 700; color: #15803d; font-size: 0.88rem;">📖 สรุปจุดหลอกกฎหมาย</div>
<div style="font-size: 0.78rem; color: #64748b; margin-top: 3px;">กฎหมาย 6 ฉบับ + นโยบาย อสส.</div>
</div>''', unsafe_allow_html=True)
    elif st.session_state.get('exam_active', False) and not st.session_state.get('exam_submitted', False):
        active_subj = st.session_state.get('exam_subject', cur_subject)
        is_active_com = (active_subj == 'computer')
        badge_color = '#0284c7' if is_active_com else '#1e40af'
        badge_bg = '#e0f2fe' if is_active_com else '#eff6ff'
        badge_title = f"💻 กำลังสอบ: วิชา{exam_cfg['computer_short']}" if is_active_com else f"⚖️ กำลังสอบ: วิชา{exam_cfg['law_short']}"
        st.markdown(f'''<div style="background: {badge_bg}; border: 1.5px solid {badge_color}; border-radius: 10px; padding: 10px 12px; margin-bottom: 8px; text-align: center;">
<div style="font-weight: 700; color: {badge_color}; font-size: 0.88rem;">{badge_title}</div>
<div style="font-size: 0.78rem; color: #64748b; margin-top: 3px;">ข้อสอบกำลังดำเนินอยู่</div>
</div>''', unsafe_allow_html=True)
    else:
        st.markdown("**📖 เลือกวิชาข้อสอบ (Subject):**")
        subject_options = {
            'law': f"⚖️ {exam_cfg['law_short']}",
            'computer': f"💻 {exam_cfg['computer_short']}"
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
        'full_exam': '🏆 สอบจริงเต็มรูปแบบ (Mock Exam 200 คะแนน)',
        'exam': '🏛️ จำลองสอบรายวิชา (Quick Exam)',
        'review': '🔄 ทบทวนข้อผิดซ้ำ (Mistake Bank)',
        'practice': '📚 ฝึกทำแยก 9 หมวดวิชา (Practice)',
        'subjective': '✍️ สนามฝึกข้อเขียนอัตนัย (100 คะแนน)',
        'knowledge': '📖 คลังสรุปจุดหลอกกฎหมาย',
        'stats': '📊 แดชบอร์ดสถิติ & กู้คืนข้อมูล',
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
    
    # Important Dates Countdown Widget in Sidebar
    from datetime import datetime, timezone, timedelta
    tz_bkk = timezone(timedelta(hours=7))
    now = datetime.now(tz_bkk)
    app_dl = datetime(2026, 12, 17, 23, 59, 59, tzinfo=tz_bkk)
    pay_dl = datetime(2026, 12, 18, 21, 0, 0, tzinfo=tz_bkk)
    d_app = app_dl - now
    d_pay = pay_dl - now
    d_app_str = f"{d_app.days} วัน {d_app.seconds // 3600} ชม." if d_app.total_seconds() > 0 else "สิ้นสุดแล้ว"
    d_pay_str = f"{d_pay.days} วัน {d_pay.seconds // 3600} ชม." if d_pay.total_seconds() > 0 else "สิ้นสุดแล้ว"
    
    st.markdown(f'''
    <div style="background: #0f172a; padding: 12px 14px; border-radius: 12px; font-size: 0.82rem; border: 1.5px solid #38bdf8; margin-bottom: 14px; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <div style="font-weight: 700; color: #38bdf8; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; font-size: 0.88rem;">
            <span>⏱️</span> <span>นับถอยหลังวันสำคัญ อสส.</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 0.8rem;">
            <span style="color: #94a3b8;">⏳ ปิดรับสมัคร:</span>
            <b style="color: #60a5fa;">17 ธ.ค. ({d_app_str})</b>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
            <span style="color: #94a3b8;">💳 ปิดจ่ายเงิน:</span>
            <b style="color: #34d399;">18 ธ.ค. 21น. ({d_pay_str})</b>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
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
            <div style="font-weight: 700; color: #0f172a; margin-bottom: 6px;">📈 สรุปภาพรวม ({ "คอมพิวเตอร์" if is_com_subj else exam_cfg['law_short'] })</div>
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
    st.caption(f"พัฒนาสำหรับเตรียมสอบ{exam_cfg['short_name']} © 2026")

# 7. Main View Router
if st.session_state.current_page in ('exam', 'full_exam'):
    render_exam_view()
elif st.session_state.current_page == 'review':
    render_review_view()
elif st.session_state.current_page == 'practice':
    render_practice_view()
elif st.session_state.current_page == 'subjective':
    render_subjective_view()
elif st.session_state.current_page == 'knowledge':
    render_knowledge_view()
elif st.session_state.current_page == 'stats':
    render_stats_view()
elif st.session_state.current_page == 'manage':
    render_manage_view()
