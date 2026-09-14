# -*- coding: utf-8 -*-
import streamlit as st
import time
import quiz_engine
import db
import styles
import legal_engine

def render_exam_view():
    if not st.session_state.exam_active and not st.session_state.exam_submitted:
        is_full_page = (st.session_state.get('current_page') == 'full_exam')
        if is_full_page:
            render_full_exam_lobby()
        else:
            render_quick_exam_lobby()
    elif st.session_state.exam_active and not st.session_state.exam_submitted:
        render_exam_in_progress()
    elif st.session_state.exam_submitted:
        render_exam_results()

def render_full_exam_lobby():
    st.markdown('''<div style="background: linear-gradient(135deg, #0b2239 0%, #1e3a8a 50%, #1e40af 100%); padding: 26px 30px; border-radius: 18px; color: white; margin-bottom: 24px; border: 2px solid #d4af37; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 14px;">
<div style="display: flex; align-items: center; gap: 10px;">
<span style="font-size: 2.2rem;">🏆</span>
<div>
<h2 style="margin: 0; color: #fef08a; font-size: 1.7rem; font-weight: 700;">จำลองสอบจริงเต็มรูปแบบ (Full Exam Simulation)</h2>
<p style="margin: 2px 0 0 0; color: #e2e8f0; font-size: 0.95rem;">จำลองสภาวะสอบเสมือนจริงของสำนักงานศาลยุติธรรม ภาคความรู้ความสามารถเฉพาะตำแหน่ง</p>
</div>
</div>
<div>
<span style="background: rgba(212, 175, 55, 0.25); border: 1.5px solid #d4af37; color: #fef08a; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.9rem;">💯 200 คะแนนเต็ม | ⏱️ 180 นาที</span>
</div>
</div>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; background: rgba(0,0,0,0.25); padding: 14px 18px; border-radius: 12px; margin-bottom: 8px; border: 1px solid rgba(255,255,255,0.1);">
<div>
<span style="color: #93c5fd; font-size: 0.85rem; font-weight: 600;">⚖️ หมวดกฎหมายระเบียบศาลฯ:</span><br>
<b style="color: #ffffff; font-size: 1rem;">30 ข้อ (60 คะแนน)</b>
</div>
<div>
<span style="color: #93c5fd; font-size: 0.85rem; font-weight: 600;">💻 หมวดคอมพิวเตอร์และสารสนเทศ:</span><br>
<b style="color: #ffffff; font-size: 1rem;">70 ข้อ (140 คะแนน)</b>
</div>
<div>
<span style="color: #93c5fd; font-size: 0.85rem; font-weight: 600;">🎯 เกณฑ์การตัดสินผลสอบ:</span><br>
<b style="color: #34d399; font-size: 0.95rem;">ผ่าน 60% (120 คะแนน) | ลุ้น Top 10 (170+ คะแนน)</b>
</div>
</div>
</div>''', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1.2])
    with col1:
        st.subheader("📋 กติกาและข้อกำหนดการสอบจริงเต็มรูปแบบ")
        st.markdown('''
        - **จำนวนข้อสอบ:** **100 ข้อ** (ข้อละ 2 คะแนน รวมเป็น **200 คะแนนเต็ม**)
        - **ลำดับข้อสอบในชุด:** รวม 2 หมวดวิชาไว้ในชุดเดียว โดยจัดเรียงลำดับ:
          * ⚖️ **ข้อ 1 - 30:** หมวดกฎหมายและระเบียบศาลยุติธรรม (30 ข้อ / 60 คะแนน)
          * 💻 **ข้อ 31 - 100:** หมวดคอมพิวเตอร์และเทคโนโลยีสารสนเทศ (70 ข้อ / 140 คะแนน)
        - **เวลาทำข้อสอบ:** **180 นาที (3 ชั่วโมงเต็ม)** มีระบบนับถอยหลัง `HH:MM:SS` และ **Auto-Submit** อัตโนมัติเมื่อหมดเวลา
        - **การสลับตำแหน่ง:** 🔀 **สุ่มสลับตำแหน่งตัวเลือก (ก, ข, ค, ง) อัตโนมัติ** ทุกรอบเพื่อป้องกันการท่องจำตำแหน่ง
        - **ระบบนำทาง:** สามารถปักหมุดข้อที่ลังเล (🚩) และกระโดดข้ามไปทำข้อที่ว่างได้จากแผงนำทาง 100 ข้อ
        - **Mistake Bank:** บันทึกข้อที่ตอบผิดลงฐานข้อมูล SQLite เพื่อนำมา **วนทำซ้ำเฉพาะข้อที่ผิด** จนกว่าจะถูกต้อง 100%
        ''')
        
        st.write("")
        if st.button("🚀 เริ่มทำข้อสอบจำลองจริงเต็มรูปแบบ (100 ข้อ / 200 คะแนน / 180 นาที)", type="primary", use_container_width=True, key="btn_start_full_sim_lobby"):
            quiz_engine.start_full_simulation_exam(st.session_state, duration_minutes=180)
            st.rerun()

    with col2:
        st.markdown("**📊 สถิติการสอบจริงของคุณ (200 คะแนน):**")
        full_stats = db.get_full_simulation_stats()
        total_sims = full_stats['total_exams']
        
        if total_sims > 0:
            latest = full_stats['latest_session']
            latest_pts = (latest['score'] * 2) if latest else 0
            latest_pct = latest['percentage'] if latest else 0.0
            latest_date = latest['created_at'] if latest else '-'
            
            # Badge for latest status
            if latest_pts >= 170:
                latest_badge = '<span style="background: #fef3c7; color: #b45309; padding: 2px 8px; border-radius: 10px; font-weight: 700; font-size: 0.78rem;">🌟 ลุ้นติด Top 10</span>'
            elif latest_pts >= 120:
                latest_badge = '<span style="background: #d1fae5; color: #047857; padding: 2px 8px; border-radius: 10px; font-weight: 700; font-size: 0.78rem;">✅ สอบผ่านเกณฑ์</span>'
            else:
                latest_badge = '<span style="background: #fee2e2; color: #b91c1c; padding: 2px 8px; border-radius: 10px; font-weight: 700; font-size: 0.78rem;">❌ ยังไม่ผ่าน</span>'
                
            st.markdown(f'''<div style="background: #ffffff; border: 2px solid #d4af37; border-radius: 14px; padding: 18px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(212, 175, 55, 0.15);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0;">
<span style="font-weight: 700; color: #1e3a8a; font-size: 0.95rem;">🏆 ประวัติและผลคะแนนของคุณ</span>
<span style="background: rgba(212, 175, 55, 0.2); color: #b45309; font-size: 0.78rem; font-weight: 700; padding: 3px 8px; border-radius: 12px;">สอบไปแล้ว {total_sims} ครั้ง</span>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 7px; font-size: 0.88rem;">
<span style="color: #64748b;">🎯 คะแนนสูงสุด:</span>
<b style="color: #059669; font-size: 0.98rem;">{full_stats['max_points']} / 200 คะแนน ({round(full_stats['max_points']/2, 1)}%)</b>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 7px; font-size: 0.88rem;">
<span style="color: #64748b;">📊 คะแนนเฉลี่ย:</span>
<b style="color: #d97706; font-size: 0.95rem;">{full_stats['avg_points']} / 200 คะแนน ({full_stats['avg_score']}%)</b>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 7px; font-size: 0.88rem;">
<span style="color: #64748b;">✅ สอบผ่านเกณฑ์ (120+):</span>
<b style="color: #047857; font-size: 0.95rem;">{full_stats['passed_count']} / {total_sims} ครั้ง</b>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 7px; font-size: 0.88rem;">
<span style="color: #64748b;">🌟 ระดับ Top 10 (170+):</span>
<b style="color: #b45309; font-size: 0.95rem;">{full_stats['top10_count']} ครั้ง</b>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 7px; font-size: 0.88rem; padding-top: 6px; border-top: 1px dashed #e2e8f0;">
<span style="color: #64748b;">🕒 สอบรอบล่าสุด:</span>
<div>
<b style="color: #1e40af; font-size: 0.95rem;">{latest_pts}/200</b> {latest_badge}
</div>
</div>
<div style="display: flex; justify-content: space-between; font-size: 0.88rem;">
<span style="color: #64748b;">🔴 ข้อผิดค้างทบทวน:</span>
<b style="color: #dc2626; font-size: 0.95rem;">{full_stats['mistake_count']} ข้อ</b>
</div>
</div>''', unsafe_allow_html=True)
        else:
            st.markdown(f'''<div style="background: #ffffff; border: 2px solid #cbd5e1; border-radius: 14px; padding: 18px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0;">
<span style="font-weight: 700; color: #1e3a8a; font-size: 0.95rem;">🏆 ประวัติและผลคะแนนของคุณ</span>
<span style="background: #f1f5f9; color: #64748b; font-size: 0.78rem; font-weight: 700; padding: 3px 8px; border-radius: 12px;">ยังไม่มีประวัติ</span>
</div>
<div style="text-align: center; padding: 14px 0; color: #64748b; font-size: 0.9rem;">
<span style="font-size: 2rem;">📝</span><br>
คุณยังไม่เคยทำข้อสอบจำลองจริงชุดเต็ม 100 ข้อ<br>
<b style="color: #1e40af;">กดปุ่มเริ่มสอบเพื่อประเมินความพร้อมและบันทึกสถิติแรกของคุณ!</b>
</div>
</div>''', unsafe_allow_html=True)
            
        # Compact Question Bank Info
        law_all = len(db.get_all_questions(subject='law'))
        com_all = len(db.get_all_questions(subject='computer'))
        st.markdown(f'''<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 14px; font-size: 0.82rem; color: #64748b; display: flex; justify-content: space-between;">
<span>คลังข้อสอบ: <b>{law_all + com_all} ข้อ</b></span>
<span>(กฎหมาย {law_all} + คอม {com_all})</span>
</div>''', unsafe_allow_html=True)

def render_quick_exam_lobby():
    subject = st.session_state.get('selected_subject', 'law')
    is_com = (subject == 'computer')
    
    st.markdown(f'''<div style="background: {'linear-gradient(135deg, #0369a1 0%, #0284c7 100%)' if is_com else 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)'}; padding: 20px 24px; border-radius: 14px; color: white; margin-bottom: 20px;">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
<div>
<h3 style="margin: 0; color: #ffffff; font-size: 1.35rem; font-weight: 700;">
{'💻 จำลองสอบรายวิชา: คอมพิวเตอร์และเทคโนโลยีสารสนเทศ' if is_com else '⚖️ จำลองสอบรายวิชา: กฎหมายระเบียบบริหารศาลยุติธรรม'}
</h3>
<p style="margin: 3px 0 0 0; color: #e2e8f0; font-size: 0.9rem;">
กำหนดจำนวนข้อและเวลาสอบได้ตามความต้องการ พร้อมจับเวลาและบันทึกสถิติรายวิชา
</p>
</div>
<div>
<span style="background: rgba(255,255,255,0.2); color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
QUICK SUBJECT EXAM
</span>
</div>
</div>
</div>''', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1.2])
    
    with col1:
        st.subheader("📋 กติกาและการจำลองสอบ")
        subject_name = "วิชาคอมพิวเตอร์และเทคโนโลยีสารสนเทศ" if is_com else "คลังข้อสอบกฎหมายระเบียบบริหารศาลฯ"
        available_q = len(db.get_all_questions(subject=subject))
        
        st.markdown(f'''
        - **วิชาที่กำลังจะสอบ:** **{subject_name}**
        - **จำนวนข้อสอบในคลัง:** {available_q} ข้อ
        - **เกณฑ์ผ่าน:** ได้คะแนน 60% ขึ้นไป
        - **การสลับตัวเลือก:** 🔀 **สลับตำแหน่งตัวเลือก (ก, ข, ค, ง) อัตโนมัติทุกครั้ง** เพื่อป้องกันการท่องจำตำแหน่ง
        - **ระบบนำทาง:** สามารถข้ามข้อ ย้อนกลับ ปักหมุดข้อที่ลังเล และตรวจเช็กข้อที่ยังไม่ได้ทำได้ตลอดเวลา
        - **การบันทึกสถิติ:** ข้อที่ตอบผิดจะถูกบันทึกลงฐานข้อมูล SQLite โดยอัตโนมัติ เพื่อนำไปฝึกซ้ำใน **"โหมดทบทวนข้อผิดซ้ำ"**
        ''')
        
        c_a, c_b = st.columns(2)
        with c_a:
            default_count_opts = [c for c in [50, 40, 30, 20, 10] if c <= available_q] or [available_q]
            q_count = st.selectbox("🎯 จำนวนข้อสอบที่ต้องการทำ:", default_count_opts, index=0)
        with c_b:
            duration_opt = st.selectbox("⏱️ เวลาในการทำข้อสอบ:", [60, 45, 30, 20, 15], index=0, format_func=lambda x: f"{x} นาที")
            
        st.write("")
        btn_label = f"🚀 เริ่มทำข้อสอบวิชา{'คอมพิวเตอร์' if is_com else 'กฎหมาย'} ({q_count} ข้อ / {duration_opt} นาที)"
        if st.button(btn_label, type="primary", use_container_width=True):
            quiz_engine.start_simulation_exam(st.session_state, count=q_count, duration_minutes=duration_opt, subject=subject)
            st.rerun()

    with col2:
        st.markdown(f"**📊 สถิติเฉพาะวิชาที่เลือก ({'คอมพิวเตอร์' if is_com else 'กฎหมายศาล'}):**")
        
        current_stats = db.get_dashboard_stats(subject=subject)
        active_color = '#0284c7' if is_com else '#1e40af'
        
        st.markdown(f'''<div style="background: #ffffff; border: 2px solid {active_color}; border-radius: 14px; padding: 18px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0;">
<span style="font-weight: 700; color: {active_color}; font-size: 0.95rem;">
{'💻 คอมพิวเตอร์และสารสนเทศ' if is_com else '⚖️ กฎหมายระเบียบบริหารศาลฯ'}
</span>
<span style="background: {'#e0f2fe' if is_com else '#eff6ff'}; color: {active_color}; font-size: 0.78rem; font-weight: 700; padding: 3px 8px; border-radius: 12px;">กำลังเลือก</span>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 7px; font-size: 0.88rem;">
<span style="color: #64748b;">คลังข้อสอบวิชานี้:</span>
<b style="color: {active_color}; font-size: 0.95rem;">{available_q} ข้อ</b>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 7px; font-size: 0.88rem;">
<span style="color: #64748b;">สอบไปแล้วทั้งหมด:</span>
<b style="color: #047857; font-size: 0.95rem;">{current_stats['total_exams']} ครั้ง</b>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 7px; font-size: 0.88rem;">
<span style="color: #64748b;">คะแนนเฉลี่ยที่ผ่านมา:</span>
<b style="color: #d97706; font-size: 0.95rem;">{current_stats['avg_score']}%</b>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 7px; font-size: 0.88rem;">
<span style="color: #64748b;">ข้อผิดค้างทบทวน:</span>
<b style="color: #dc2626; font-size: 0.95rem;">{current_stats['mistake_count']} ข้อ</b>
</div>
<div style="display: flex; justify-content: space-between; font-size: 0.88rem;">
<span style="color: #64748b;">ความแม่นยำวิชานี้:</span>
<b style="color: #059669; font-size: 0.95rem;">{current_stats['overall_accuracy']}%</b>
</div>
</div>''', unsafe_allow_html=True)

def render_exam_in_progress():
    questions = st.session_state.exam_questions
    total_q = len(questions)
    current_idx = st.session_state.current_q_idx
    q = questions[current_idx]
    
    # Check timer
    remaining_secs = quiz_engine.get_remaining_seconds(st.session_state)
    is_full_sim = (st.session_state.get('exam_mode') == 'full_simulation')
    duration_mins = st.session_state.get('duration_seconds', 3600) // 60
    
    if remaining_secs <= 0 and st.session_state.exam_active:
        st.warning(f"⚠️ หมดเวลา {duration_mins} นาทีแล้ว! ระบบกำลังส่งข้อสอบและประมวลผล...")
        quiz_engine.calculate_and_save_exam_results(st.session_state)
        time.sleep(1)
        st.rerun()
        
    time_str = quiz_engine.format_time_hhmmss(remaining_secs)
    is_critical = remaining_secs < 300 # Less than 5 mins
    
    # Top Header & Timer Row
    col_t1, col_t2, col_t3 = st.columns([2.2, 1.3, 1.0])
    with col_t1:
        if is_full_sim:
            curr_subj = "⚖️ หมวดกฎหมาย (ข้อ 1-30)" if current_idx < 30 else "💻 หมวดคอมพิวเตอร์ (ข้อ 31-100)"
            mode_name = f"🏆 สอบจริงเต็มรูปแบบ | {curr_subj}"
        elif st.session_state.get('exam_mode') == 'mistakes_retest':
            mode_name = "🎯 วนทำซ้ำเฉพาะข้อที่ผิด (Mistake Bank)"
        elif st.session_state.get('exam_mode') == 'review_test':
            mode_name = "🔄 โหมดทบทวนข้อผิด"
        else:
            mode_name = "⚖️ โหมดจำลองสอบรายวิชา"
            
        st.markdown(f'''
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <span class="nav-badge">{mode_name}</span>
            <span style="color: #64748b; font-size: 0.9rem;">ข้อที่ {current_idx + 1} จาก {total_q}</span>
        </div>
        ''', unsafe_allow_html=True)
        progress_val = (len(st.session_state.user_answers) / total_q)
        st.progress(progress_val, text=f"ทำแล้ว {len(st.session_state.user_answers)}/{total_q} ข้อ ({int(progress_val*100)}%)")
        
    with col_t2:
        crit_class = "timer-critical" if is_critical else ""
        st.markdown(f'''
        <div class="timer-container {crit_class}">
            <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">⏱️ เวลาที่เหลือ</div>
            <div class="timer-clock">{time_str}</div>
        </div>
        ''', unsafe_allow_html=True)

    with col_t3:
        st.write("")
        if st.button("🚪 เลิกทำ (ไม่นับผล)", key="top_abandon_btn", use_container_width=True, help="ยกเลิกการสอบชุดนี้ทันที โดยไม่นำคะแนนไปบันทึกลงสถิติ"):
            st.session_state.confirm_abandon = True
            st.session_state.confirm_submit = False
            st.rerun()

    st.write("")
    
    # Main Exam Workspace: Question Area (left) + Question Navigator Palette (right)
    col_main, col_sidebar = st.columns([2.2, 1.3])
    
    with col_main:
        is_bookmarked = current_idx in st.session_state.bookmarked_indices
        
        # Question Card Header
        bookmark_icon = "🚩" if is_bookmarked else "🏳️"
        st.markdown(f'''
        <div class="question-card">
            <div class="question-header">
                <div>
                    <span class="q-number">ข้อที่ {current_idx + 1}</span>
                </div>
                <div style="font-size: 0.85rem; color: #94a3b8;">
                    ID: {q['id']}
                </div>
            </div>
            <div class="q-text">
                {q['question']}
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Choices Form
        options = q['options']
        choice_letters = styles.get_choice_letters()
        formatted_options = [f"{choice_letters[i]}.  {opt}" for i, opt in enumerate(options)]
        
        current_answer = st.session_state.user_answers.get(current_idx, None)
        
        st.markdown("<p style='font-size: 1rem; font-weight: 600; color: #1e3a8a; margin-bottom: 8px;'>📝 เลือกคำตอบที่ถูกต้องที่สุด:</p>", unsafe_allow_html=True)
        selected_option = st.radio(
            "ตัวเลือกคำตอบ",
            options=list(range(len(options))),
            format_func=lambda i: formatted_options[i],
            index=current_answer if current_answer is not None else None,
            key=f"radio_q_{current_idx}",
            label_visibility="collapsed"
        )
        
        if selected_option is not None:
            st.session_state.user_answers[current_idx] = selected_option

        st.write("")
        # Navigation Buttons Row
        n_c1, n_c2, n_c3 = st.columns([1, 1, 1])
        with n_c1:
            if st.button("⬅️ ข้อก่อนหน้า", disabled=(current_idx == 0), use_container_width=True):
                st.session_state.current_q_idx -= 1
                st.rerun()
        with n_c2:
            if st.button("➡️ ข้อถัดไป", disabled=(current_idx == total_q - 1), use_container_width=True):
                st.session_state.current_q_idx += 1
                st.rerun()
        with n_c3:
            bm_label = "ปลดปักหมุด" if is_bookmarked else "🚩 ปักหมุดทบทวน"
            if st.button(bm_label, use_container_width=True):
                if is_bookmarked:
                    st.session_state.bookmarked_indices.remove(current_idx)
                else:
                    st.session_state.bookmarked_indices.add(current_idx)
                st.rerun()

    # Question Navigator Grid Sidebar
    with col_sidebar:
        st.markdown("<h4 style='margin: 0 0 8px 0;'>📌 แผงนำทางข้อสอบ</h4>", unsafe_allow_html=True)
        
        # Legend
        st.markdown('''
        <div style="font-size: 0.8rem; display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; background: rgba(0,0,0,0.04); padding: 8px 12px; border-radius: 8px;">
            <span>🔵 <b>กำลังทำ</b></span>
            <span>🟢 <b>ตอบแล้ว</b></span>
            <span>⚪ <b>ยังไม่ตอบ</b></span>
            <span>🚩 <b>ปักหมุด</b></span>
        </div>
        ''', unsafe_allow_html=True)
        
        # Draw 5-column button grid
        grid_cols = st.columns(5)
        unanswered_list = []
        
        for i in range(total_q):
            col_target = grid_cols[i % 5]
            is_cur = (i == current_idx)
            is_ans = i in st.session_state.user_answers
            is_bm = i in st.session_state.bookmarked_indices
            
            if not is_ans and not is_cur:
                unanswered_list.append(i + 1)
                
            if is_bm:
                label = f"{i+1}🚩"
            elif is_ans:
                label = f"{i+1}🟢"
            elif is_cur:
                label = f"{i+1}🔵"
            else:
                label = f"{i+1}⚪"
                
            btn_type = "primary" if is_cur else "secondary"
            
            if col_target.button(label, key=f"nav_btn_{i}", type=btn_type, use_container_width=True):
                st.session_state.current_q_idx = i
                st.rerun()
                
        st.write("---")
        unanswered = total_q - len(st.session_state.user_answers)
        if unanswered > 0:
            st.warning(f"⚠️ **ยังไม่ได้ตอบอีก {unanswered} ข้อ**")
            if unanswered_list:
                first_unans = unanswered_list[0] - 1
                if st.button(f"⚡ ข้ามไปทำข้อ {first_unans + 1} (ข้อว่างแรก)", use_container_width=True, help="กระโดดไปยังข้อที่ยังไม่ได้ตอบทันที"):
                    st.session_state.current_q_idx = first_unans
                    st.rerun()
        else:
            st.success("🎉 ตอบครบทุกข้อแล้ว!")
            
        if st.button("✅ ส่งข้อสอบเพื่อตรวจผล", type="primary", use_container_width=True):
            st.session_state.confirm_submit = True
            st.session_state.confirm_abandon = False

        if st.session_state.get('confirm_submit', False):
            st.warning(f"ยืนยันการส่งข้อสอบ? (ตอบแล้ว {len(st.session_state.user_answers)}/{total_q} ข้อ)")
            s_c1, s_c2 = st.columns(2)
            with s_c1:
                if st.button("ยืนยันส่ง", type="primary", key="btn_confirm_submit_yes", use_container_width=True):
                    st.session_state.confirm_submit = False
                    quiz_engine.calculate_and_save_exam_results(st.session_state)
                    st.rerun()
            with s_c2:
                if st.button("ทำต่อ", key="btn_confirm_submit_no", use_container_width=True):
                    st.session_state.confirm_submit = False
                    st.rerun()

        st.write("")
        if st.button("🚫 เลิกทำข้อสอบ (ไม่บันทึกสถิติ)", use_container_width=True, help="ยกเลิกการสอบชุดนี้ทันที โดยไม่นำผลคะแนนและข้อสอบไปบันทึกลงสถิติ"):
            st.session_state.confirm_abandon = True
            st.session_state.confirm_submit = False

        if st.session_state.get('confirm_abandon', False):
            st.error("⚠️ **ยืนยันการเลิกทำข้อสอบ?**\n\nระบบจะยกเลิกการสอบชุดนี้ทันที โดย**ไม่นับคะแนน ไม่บันทึกสถิติ และไม่บันทึกข้อผิดพลาด**ใดๆ ทั้งสิ้น")
            ab_c1, ab_c2 = st.columns(2)
            with ab_c1:
                if st.button("🔴 ยืนยันยกเลิก", type="primary", key="btn_abandon_confirm_yes", use_container_width=True):
                    quiz_engine.abandon_exam(st.session_state)
                    st.toast("ยกเลิกการสอบเรียบร้อยแล้ว (ไม่บันทึกสถิติ)", icon="🚪")
                    st.rerun()
            with ab_c2:
                if st.button("ทำข้อสอบต่อ", key="btn_abandon_confirm_no", use_container_width=True):
                    st.session_state.confirm_abandon = False
                    st.rerun()

def render_exam_results():
    res = st.session_state.exam_result
    if not res:
        st.warning("ไม่พบผลสอบ กรุณาเริ่มทำข้อสอบใหม่")
        if st.button("กลับหน้าหลัก"):
            st.session_state.exam_submitted = False
            st.session_state.exam_active = False
            st.rerun()
        return

    score = res['score']
    total = res['total_questions']
    percentage = res['percentage']
    passed = res['passed']
    is_full_sim = res.get('is_full_simulation', False)
    earned_pts = res.get('earned_points', score * (2 if is_full_sim else 1))
    max_pts = res.get('total_points', total * (2 if is_full_sim else 1))
    
    tier = res.get('tier', 'passed' if passed else 'failed')
    tier_title = res.get('tier_title', '🎉 ยินดีด้วย! คุณสอบผ่านเกณฑ์ (60%)' if passed else '💪 ยังไม่ผ่านเกณฑ์ พยายามใหม่อีกนิดนะ!')
    tier_badge = res.get('tier_badge', 'PASSED' if passed else 'FAILED')
    tier_color = res.get('tier_color', '#059669' if passed else '#dc2626')
    tier_desc = res.get('tier_desc', '')
    banner_color = "#059669" if passed else "#dc2626"
    status_text = "🎉 ยินดีด้วย! คุณสอบผ่านเกณฑ์ (60%)" if passed else "💪 ยังไม่ผ่านเกณฑ์ พยายามใหม่อีกนิดนะ!"
    
    # Hero Score Card
    if is_full_sim:
        st.markdown(f'''
        <div class="result-hero" style="border: 2px solid {tier_color};">
            <div style="display: flex; justify-content: center; gap: 10px; margin-bottom: 12px;">
                <span style="background: {tier_color}; color: white; padding: 4px 16px; border-radius: 20px; font-weight: 700; font-size: 0.9rem; letter-spacing: 0.5px;">
                    {tier_badge}
                </span>
            </div>
            <div style="font-size: 1.35rem; color: #f8fafc; font-weight: 700; margin-bottom: 8px;">{tier_title}</div>
            <p style="color: #cbd5e1; font-size: 0.95rem; margin: 0 auto 16px auto; max-width: 650px;">{tier_desc}</p>
            <div class="score-circle" style="border-color: {tier_color}; width: 170px; height: 170px;">
                <div class="score-number" style="font-size: 3rem; color: #fef08a;">{earned_pts}</div>
                <div class="score-total" style="font-size: 0.85rem;">เต็ม {max_pts} คะแนน</div>
            </div>
            <h2 style="margin: 10px 0 0 0; font-size: 2.2rem; color: #ffffff;">{percentage}%</h2>
            <p style="color: #94a3b8; margin-top: 6px;">ทำถูก {score} จาก {total} ข้อ | เวลาที่ใช้: {res['time_spent_str']}</p>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div class="result-hero">
            <div style="font-size: 1.2rem; color: #f8fafc; font-weight: 600; margin-bottom: 16px;">{status_text}</div>
            <div class="score-circle" style="border-color: {banner_color};">
                <div class="score-number">{score}</div>
                <div class="score-total">เต็ม {total} ข้อ</div>
            </div>
            <h2 style="margin: 0; font-size: 2rem; color: #ffffff;">{percentage}%</h2>
            <p style="color: #94a3b8; margin-top: 6px;">เวลาที่ใช้: {res['time_spent_str']}</p>
        </div>
        ''', unsafe_allow_html=True)
        
    # Subject Breakdown for Full Simulation
    if is_full_sim:
        subj_stats = res.get('subject_stats', {})
        law_st = subj_stats.get('law', {'total': 30, 'correct': 0, 'wrong': 0, 'unanswered': 0, 'points': 0, 'max_points': 60})
        com_st = subj_stats.get('computer', {'total': 70, 'correct': 0, 'wrong': 0, 'unanswered': 0, 'points': 0, 'max_points': 140})
        
        law_pct = round((law_st['correct'] / max(1, law_st['total'])) * 100, 1)
        com_pct = round((com_st['correct'] / max(1, com_st['total'])) * 100, 1)
        
        st.markdown("<h4 style='color: #1e3a8a; margin: 18px 0 10px 0;'>📊 ผลการสอบแยกรายหมวดวิชา (Subject Breakdown)</h4>", unsafe_allow_html=True)
        col_sb1, col_sb2 = st.columns(2)
        
        with col_sb1:
            law_bar_color = "#059669" if law_pct >= 60 else "#dc2626"
            st.markdown(f'''
            <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 12px; padding: 16px 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 700; color: #1e40af; font-size: 1rem;">⚖️ หมวดกฎหมายระเบียบศาลฯ</span>
                    <span style="background: #eff6ff; color: #1e40af; font-weight: 700; font-size: 0.85rem; padding: 2px 10px; border-radius: 12px;">{law_pct}%</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.92rem; margin-bottom: 4px;">
                    <span style="color: #64748b;">คะแนนที่ได้:</span>
                    <b style="color: #0f172a;">{law_st['points']} / {law_st['max_points']} คะแนน</b>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.92rem; margin-bottom: 8px;">
                    <span style="color: #64748b;">ตอบถูก:</span>
                    <b style="color: {law_bar_color};">{law_st['correct']} / {law_st['total']} ข้อ</b>
                </div>
                <div style="background: #e2e8f0; border-radius: 6px; height: 8px; overflow: hidden;">
                    <div style="background: {law_bar_color}; width: {law_pct}%; height: 100%;"></div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
        with col_sb2:
            com_bar_color = "#059669" if com_pct >= 60 else "#dc2626"
            st.markdown(f'''
            <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 12px; padding: 16px 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 700; color: #0284c7; font-size: 1rem;">💻 หมวดคอมพิวเตอร์และสารสนเทศ</span>
                    <span style="background: #e0f2fe; color: #0284c7; font-weight: 700; font-size: 0.85rem; padding: 2px 10px; border-radius: 12px;">{com_pct}%</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.92rem; margin-bottom: 4px;">
                    <span style="color: #64748b;">คะแนนที่ได้:</span>
                    <b style="color: #0f172a;">{com_st['points']} / {com_st['max_points']} คะแนน</b>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.92rem; margin-bottom: 8px;">
                    <span style="color: #64748b;">ตอบถูก:</span>
                    <b style="color: {com_bar_color};">{com_st['correct']} / {com_st['total']} ข้อ</b>
                </div>
                <div style="background: #e2e8f0; border-radius: 6px; height: 8px; overflow: hidden;">
                    <div style="background: {com_bar_color}; width: {com_pct}%; height: 100%;"></div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
        st.write("")
    
    # 4 Stat Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        correct_sub = f"{earned_pts}/{max_pts} คะแนน" if is_full_sim else f"{percentage}%"
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-label">ตอบถูก ({score}/{total} ข้อ)</div>
            <div class="stat-value" style="color: #10b981;">{score} ข้อ</div>
            <div style="font-size: 0.78rem; color: #059669; margin-top: 2px;">{correct_sub}</div>
        </div>
        ''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-label">ตอบผิด</div>
            <div class="stat-value" style="color: #ef4444;">{res['wrong_count']} ข้อ</div>
            <div style="font-size: 0.78rem; color: #dc2626; margin-top: 2px;">-{res['wrong_count'] * (2 if is_full_sim else 1)} คะแนน</div>
        </div>
        ''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-label">ไม่ได้ตอบ</div>
            <div class="stat-value" style="color: #64748b;">{res['unanswered_count']} ข้อ</div>
            <div style="font-size: 0.78rem; color: #64748b; margin-top: 2px;">0 คะแนน</div>
        </div>
        ''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-label">บันทึกข้อผิดลง SQLite</div>
            <div class="stat-value" style="color: #3b82f6;">สำเร็จ ✅</div>
            <div style="font-size: 0.78rem; color: #2563eb; margin-top: 2px;">Session #{res.get('session_id', '-')}</div>
        </div>
        ''', unsafe_allow_html=True)
        
    st.write("")
    
    # Mistake Bank & Action Buttons
    mistakes_list = st.session_state.get('mistakes', [])
    has_mistakes = len(mistakes_list) > 0
    
    if has_mistakes:
        mistake_count = len(mistakes_list)
        st.markdown(f'''
        <div style="background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border: 2px solid #ef4444; border-radius: 14px; padding: 16px 20px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.1);">
            <div>
                <div style="font-weight: 700; color: #991b1b; font-size: 1.05rem;">
                    🎯 คลังข้อผิดเฉพาะรอบนี้ (Mistake Bank): {mistake_count} ข้อ
                </div>
                <div style="font-size: 0.88rem; color: #b91c1c; margin-top: 2px;">
                    ระบบดึงเฉพาะข้อที่คุณตอบผิด/ยังไม่ได้ตอบในรอบนี้มาไว้ให้คุณวนฝึกซ้ำทันทีจนกว่าจะผ่าน 100%
                </div>
            </div>
            <div style="text-align: right;">
                <span style="background: #ef4444; color: white; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.82rem;">
                    {mistake_count} ข้อค้างทบทวน
                </span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        act_c1, act_c2, act_c3, act_c4 = st.columns([1.4, 1, 1, 1])
        with act_c1:
            if st.button(f"🔁 ทำซ้ำเฉพาะข้อที่ผิด ({mistake_count} ข้อ)", type="primary", use_container_width=True, key="btn_retest_mistakes", help="ดึงเฉพาะข้อที่ตอบผิดในรอบนี้มาวนสอบซ้ำ สลับตัวเลือกใหม่ จนกว่าจะตอบถูกครบทุกข้อ"):
                quiz_engine.start_mistakes_retest(st.session_state)
                st.rerun()
        with act_c2:
            retry_label = "🏆 สอบจริงเต็มรูปแบบใหม่" if is_full_sim else "🔄 สอบใหม่ทั้งชุด"
            if st.button(retry_label, use_container_width=True, help="เริ่มทำข้อสอบใหม่อีกครั้ง"):
                st.session_state.exam_submitted = False
                st.session_state.exam_active = False
                if is_full_sim:
                    quiz_engine.start_full_simulation_exam(st.session_state, duration_minutes=180)
                st.rerun()
        with act_c3:
            if st.button("📚 คลังข้อผิดทั้งหมด (Mistake Bank)", use_container_width=True, help="ไปที่โหมดทบทวนข้อผิดสะสมทั้งหมดจากฐานข้อมูล SQLite"):
                st.session_state.current_page = 'review'
                st.session_state.exam_submitted = False
                st.session_state.exam_active = False
                st.rerun()
        with act_c4:
            if st.button("📊 ดูแดชบอร์ดสถิติรวม", use_container_width=True):
                st.session_state.current_page = 'stats'
                st.session_state.exam_submitted = False
                st.session_state.exam_active = False
                st.rerun()
    else:
        st.success("🎉 ยอดเยี่ยมที่สุด! คุณทำข้อสอบรอบนี้ถูกต้องครบ 100% ไม่มีข้อผิดพลาดค้างทบทวน")
        act_c1, act_c2, act_c3 = st.columns([1, 1, 1])
        with act_c1:
            retry_label = "🏆 สอบจริงเต็มรูปแบบใหม่" if is_full_sim else "🔄 สอบชุดใหม่"
            if st.button(retry_label, type="primary", use_container_width=True):
                st.session_state.exam_submitted = False
                st.session_state.exam_active = False
                if is_full_sim:
                    quiz_engine.start_full_simulation_exam(st.session_state, duration_minutes=180)
                st.rerun()
        with act_c2:
            if st.button("📚 ไปฝึกทำแยกหมวดหมู่", use_container_width=True):
                st.session_state.current_page = 'practice'
                st.session_state.exam_submitted = False
                st.session_state.exam_active = False
                st.rerun()
        with act_c3:
            if st.button("📊 ดูแดชบอร์ดสถิติรวม", use_container_width=True):
                st.session_state.current_page = 'stats'
                st.session_state.exam_submitted = False
                st.session_state.exam_active = False
                st.rerun()
            
    st.write("---")
    
    # Detailed Review & Answer Explanations
    st.subheader("🔍 ตรวจคำตอบและเฉลยละเอียดรายข้อ")
    
    filter_view = st.radio(
        "เลือกดูข้อสอบ:",
        ["ทั้งหมด", "เฉพาะข้อที่ตอบผิด (Mistakes Only)", "เฉพาะข้อที่ตอบถูก (Correct Only)", "เฉพาะข้อที่ไม่ได้ตอบ"],
        horizontal=True
    )
    
    choice_letters = styles.get_choice_letters()
    details = res['details']
    
    for qid, d in details.items():
        status = d['status']
        if filter_view == "เฉพาะข้อที่ตอบผิด (Mistakes Only)" and status != 'wrong':
            continue
        elif filter_view == "เฉพาะข้อที่ตอบถูก (Correct Only)" and status != 'correct':
            continue
        elif filter_view == "เฉพาะข้อที่ไม่ได้ตอบ" and status != 'unanswered':
            continue
            
        status_badge = "✅ ตอบถูกต้อง" if status == 'correct' else ("❌ ตอบผิด" if status == 'wrong' else "⚪ ไม่ได้ตอบ")
        box_style = "explanation-box" if status == 'correct' else "explanation-wrong-box"
        
        with st.expander(f"ข้อที่ {d['q_idx'] + 1}: {d['question_text'][:70]}... [{status_badge}]", expanded=(status == 'wrong')):
            st.markdown(f"**คำถาม:** {d['question_text']}")
            
            # Render choices with color highlighting
            for c_idx, opt in enumerate(d['options']):
                c_letter = choice_letters[c_idx]
                prefix = f"**{c_letter}.** "
                if c_idx == d['correct_index'] and c_idx == d['selected']:
                    st.success(f"{prefix} {opt} (คำตอบของคุณ - ถูกต้อง ✅)")
                elif c_idx == d['correct_index']:
                    st.success(f"{prefix} {opt} (เฉลยที่ถูกต้อง 🎯)")
                elif c_idx == d['selected']:
                    st.error(f"{prefix} {opt} (คุณเลือกข้อนี้ ❌)")
                else:
                    st.write(f"{prefix} {opt}")
                    
            st.markdown(f'''
            <div class="{box_style}">
                <span class="law-ref-pill">📖 อ้างอิง: {d.get('law_ref', 'พ.ร.บ.ระเบียบบริหารราชการศาลยุติธรรม')}</span><br>
                <b>คำอธิบายเฉลย:</b> {d.get('explanation', 'ไม่มีคำอธิบายเพิ่มเติม')}
            </div>
            ''', unsafe_allow_html=True)
            
            # Legal References & Precedents Engine
            legal_engine.render_legal_reference_expander(d, expanded=False)
