# -*- coding: utf-8 -*-
import streamlit as st
import time
import quiz_engine
import db
import styles
import legal_engine

def render_exam_view():
    if not st.session_state.exam_active and not st.session_state.exam_submitted:
        render_exam_lobby()
    elif st.session_state.exam_active and not st.session_state.exam_submitted:
        render_exam_in_progress()
    elif st.session_state.exam_submitted:
        render_exam_results()

def render_exam_lobby():
    subject = st.session_state.get('selected_subject', 'law')
    is_com = (subject == 'computer')
    
    # 1. Subject Selector Bar right at the top
    st.markdown("<p style='font-size: 1.05rem; font-weight: 700; color: #1e3a8a; margin-bottom: 8px;'>🎯 เลือกวิชาที่ต้องการจำลองสอบ & ดูสถิติ:</p>", unsafe_allow_html=True)
    sel_c1, sel_c2 = st.columns(2)
    law_q_count = len(db.get_all_questions(subject='law'))
    com_q_count = len(db.get_all_questions(subject='computer'))
    
    with sel_c1:
        law_btn_type = "primary" if not is_com else "secondary"
        if st.button(f"⚖️ วิชากฎหมายศาลยุติธรรม ({law_q_count} ข้อ)", type=law_btn_type, use_container_width=True, key="lobby_btn_law"):
            if st.session_state.selected_subject != 'law':
                st.session_state.selected_subject = 'law'
                st.rerun()
    with sel_c2:
        com_btn_type = "primary" if is_com else "secondary"
        if st.button(f"💻 วิชาคอมพิวเตอร์และสารสนเทศ ({com_q_count} ข้อ)", type=com_btn_type, use_container_width=True, key="lobby_btn_com"):
            if st.session_state.selected_subject != 'computer':
                st.session_state.selected_subject = 'computer'
                st.rerun()

    st.write("")
    
    # Re-check subject after possible switch
    subject = st.session_state.get('selected_subject', 'law')
    is_com = (subject == 'computer')
    
    lobby_title = "💻 โหมดจำลองทำข้อสอบเสมือนจริง: วิชาคอมพิวเตอร์และสารสนเทศ" if is_com else "🏛️ โหมดจำลองทำข้อสอบเสมือนจริง: วิชากฎหมายศาลยุติธรรม"
    lobby_desc = (
        "ฝึกทำข้อสอบปรนัยความรู้ความสามารถด้านคอมพิวเตอร์และเทคโนโลยีสารสนเทศ ฮาร์ดแวร์ ซอฟต์แวร์ MS Office เครือข่าย ความปลอดภัยไซเบอร์ พ.ร.บ.คอมฯ และ AI"
        if is_com else
        "ฝึกทำข้อสอบปรนัย กฎหมายระเบียบบริหารราชการศาลยุติธรรม พ.ศ. 2543 (และแก้ไขเพิ่มเติม) ภายใต้สภาวะการสอบจริง"
    )
    
    banner_bg = 'linear-gradient(135deg, #0f172a 0%, #0369a1 100%)' if is_com else 'linear-gradient(135deg, #0b2239 0%, #1e3a8a 100%)'
    banner_border = '#38bdf8' if is_com else '#d4af37'
    
    st.markdown(f'''
    <div style="background: {banner_bg}; padding: 24px 28px; border-radius: 16px; color: white; margin-bottom: 24px; border: 1px solid {banner_border};">
        <h2 style="margin: 0 0 8px 0; color: #f8fafc;">{lobby_title}</h2>
        <p style="margin: 0; color: #cbd5e1; font-size: 1rem;">
            {lobby_desc}
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
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
        
        st.markdown(f'''
        <div style="background: #ffffff; border: 2px solid {active_color}; border-radius: 14px; padding: 18px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0;">
                <span style="font-weight: 700; color: {active_color}; font-size: 0.95rem;">
                    {'💻 คอมพิวเตอร์และสารสนเทศ' if is_com else '⚖️ กฎหมายระเบียบบริหารศาลฯ'}
                </span>
                <span style="background: {'#e0f2fe' if is_com else '#eff6ff'}; color: {active_color}; font-size: 0.78rem; font-weight: 700; padding: 3px 8px; border-radius: 12px;">
                    กำลังเลือก
                </span>
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
        </div>
        ''', unsafe_allow_html=True)
        
        # Quick Switch or Peek at the other subject
        other_subject = 'law' if is_com else 'computer'
        other_label = '⚖️ สลับไปดู/สอบวิชากฎหมาย' if is_com else '💻 สลับไปดู/สอบวิชาคอมพิวเตอร์'
        if st.button(other_label, key="lobby_sw_other", use_container_width=True):
            st.session_state.selected_subject = other_subject
            st.rerun()

def render_exam_in_progress():
    questions = st.session_state.exam_questions
    total_q = len(questions)
    current_idx = st.session_state.current_q_idx
    q = questions[current_idx]
    
    # Check timer
    remaining_secs = quiz_engine.get_remaining_seconds(st.session_state)
    if remaining_secs <= 0 and st.session_state.exam_active:
        st.warning("⚠️ หมดเวลา 60 นาทีแล้ว! ระบบกำลังส่งข้อสอบและประมวลผล...")
        quiz_engine.calculate_and_save_exam_results(st.session_state)
        time.sleep(1)
        st.rerun()
        
    time_str = quiz_engine.format_time_mmss(remaining_secs)
    is_critical = remaining_secs < 300 # Less than 5 mins
    
    # Top Header & Timer Row
    col_t1, col_t2, col_t3 = st.columns([2.8, 1.2, 1.0])
    with col_t1:
        st.markdown(f'''
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <span class="nav-badge">⚖️ โหมดจำลองสอบจริง</span>
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
    col_main, col_sidebar = st.columns([2.8, 1.2])
    
    with col_main:
        is_bookmarked = current_idx in st.session_state.bookmarked_indices
        
        # Question Card Header
        bookmark_icon = "🚩" if is_bookmarked else "🏳️"
        st.markdown(f'''
        <div class="question-card">
            <div class="question-header">
                <div>
                    <span class="q-number">ข้อที่ {current_idx + 1}</span>
                    <span class="q-category-tag" style="margin-left: 8px;">{q.get('category', 'ทั่วไป')}</span>
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
        n_c1, n_c2, n_c3, n_c4 = st.columns([1, 1, 1, 1])
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
        with n_c4:
            if current_idx in st.session_state.user_answers:
                if st.button("🗑️ ล้างคำตอบ", use_container_width=True):
                    del st.session_state.user_answers[current_idx]
                    st.rerun()

    # Question Navigator Grid Sidebar
    with col_sidebar:
        st.markdown("<h4 style='margin: 0 0 10px 0;'>📌 แผงนำทางข้อสอบ</h4>", unsafe_allow_html=True)
        
        # Legend
        st.markdown('''
        <div style="font-size: 0.78rem; display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">
            <span>🔵 กำลังทำ</span>
            <span>🟢 ตอบแล้ว</span>
            <span>⚪ ยังไม่ตอบ</span>
            <span>🚩 ปักหมุด</span>
        </div>
        ''', unsafe_allow_html=True)
        
        # Draw 5-column button grid
        grid_cols = st.columns(5)
        for i in range(total_q):
            col_target = grid_cols[i % 5]
            is_cur = (i == current_idx)
            is_ans = i in st.session_state.user_answers
            is_bm = i in st.session_state.bookmarked_indices
            
            label = f"{i+1}"
            if is_bm:
                label += "🚩"
                
            btn_type = "primary" if is_cur else ("secondary")
            
            if col_target.button(label, key=f"nav_btn_{i}", type=btn_type, use_container_width=True):
                st.session_state.current_q_idx = i
                st.rerun()
                
        st.write("---")
        unanswered = total_q - len(st.session_state.user_answers)
        if unanswered > 0:
            st.info(f"ยังไม่ได้ตอบอีก {unanswered} ข้อ")
        else:
            st.success("ตอบครบทุกข้อแล้ว!")
            
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
    
    # Hero Score Card
    banner_color = "#059669" if passed else "#dc2626"
    status_text = "🎉 ยินดีด้วย! คุณสอบผ่านเกณฑ์ (60%)" if passed else "💪 ยังไม่ผ่านเกณฑ์ พยายามใหม่อีกนิดนะ!"
    
    st.markdown(f'''
    <div class="result-hero">
        <div style="font-size: 1.2rem; color: #f8fafc; font-weight: 600; margin-bottom: 16px;">{status_text}</div>
        <div class="score-circle" style="border-color: {banner_color};">
            <div class="score-number">{score}</div>
            <div class="score-total">เต็ม {total}</div>
        </div>
        <h2 style="margin: 0; font-size: 2rem; color: #ffffff;">{percentage}%</h2>
        <p style="color: #94a3b8; margin-top: 6px;">เวลาที่ใช้: {res['time_spent_str']} นาที</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # 4 Stat Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-label">ตอบถูก</div>
            <div class="stat-value" style="color: #10b981;">{score} ข้อ</div>
        </div>
        ''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-label">ตอบผิด</div>
            <div class="stat-value" style="color: #ef4444;">{res['wrong_count']} ข้อ</div>
        </div>
        ''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-label">ไม่ได้ตอบ</div>
            <div class="stat-value" style="color: #64748b;">{res['unanswered_count']} ข้อ</div>
        </div>
        ''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-label">บันทึกข้อผิดลง SQLite</div>
            <div class="stat-value" style="color: #3b82f6;">สำเร็จ ✅</div>
        </div>
        ''', unsafe_allow_html=True)
        
    st.write("")
    
    # Action Buttons
    act_c1, act_c2, act_c3 = st.columns([1, 1, 1])
    with act_c1:
        if st.button("🔄 สอบใหม่อีกครั้ง", type="primary", use_container_width=True):
            st.session_state.exam_submitted = False
            st.session_state.exam_active = False
            st.rerun()
    with act_c2:
        if st.button("🎯 ไปทบทวนเฉพาะข้อที่ผิด (Review Mode)", use_container_width=True):
            st.session_state.current_page = 'review'
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
