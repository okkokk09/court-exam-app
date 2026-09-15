# -*- coding: utf-8 -*-
import streamlit as st
import db
import quiz_engine
import legal_engine
import styles

def render_review_view():
    st.markdown(
        '<div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%); padding: 24px 28px; border-radius: 16px; color: white; margin-bottom: 24px; border: 1px solid #818cf8;">'
        '<h2 style="margin: 0 0 8px 0; color: #ffffff;">🔄 โหมดทบทวนข้อผิดซ้ำ (Mistake Review & Mastery)</h2>'
        '<p style="margin: 0; color: #c7d2fe; font-size: 1rem;">'
        'ระบบดึงข้อสอบที่คุณเคยตอบผิดจากฐานข้อมูล SQLite มาให้ฝึกทำซ้ำจนกว่าจะแม่นยำ ปิดจุดอ่อนก่อนลงสนามจริง'
        '</p>'
        '</div>',
        unsafe_allow_html=True
    )
    
    # Filter selection
    subject = st.session_state.get('selected_subject', 'law')
    cur_user = st.session_state.get('current_user', 'เฟิส')
    session_mistakes = [q for q in st.session_state.get('mistakes', []) if q.get('subject', 'law') == subject or not q.get('subject')]
    
    filter_options = []
    if session_mistakes:
        filter_options.append(('session_mistakes', f"🎯 ข้อที่เพิ่งตอบผิดจากรอบล่าสุด ({len(session_mistakes)} ข้อ)"))
        
    filter_options.extend([
        ('frequent_mistakes', '🔥 ข้อที่ตอบผิดบ่อยที่สุด (Top Frequent Mistakes)'),
        ('recent_mistakes', '⏰ ข้อที่ตอบผิดล่าสุด (Recent Errors)'),
        ('unmastered', '🛡️ ข้อที่ยังไม่แม่นยำ (Unmastered)'),
        ('all_mistakes', '📚 ข้อที่เคยตอบผิดทั้งหมด (All Logged Mistakes)')
    ])
    
    col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
    with col_f1:
        filter_opt = st.selectbox(
            "🎯 ตัวกรองข้อผิด:",
            filter_options,
            format_func=lambda x: x[1],
            key="review_filter_select"
        )
        filter_type = filter_opt[0]
        
    with col_f2:
        limit_count = st.number_input("จำนวนข้อที่ต้องการดึง:", min_value=5, max_value=100, value=20, step=5)

    with col_f3:
        st.write("")
        st.write("")
        if st.button("🔄 รีเฟรชข้อสอบ", use_container_width=True, help="ล้างแคชและดึงสถิติล่าสุดจากฐานข้อมูล"):
            if 'review_current_state' in st.session_state:
                del st.session_state['review_current_state']
            if 'review_loaded_qs' in st.session_state:
                del st.session_state['review_loaded_qs']
            st.rerun()
        
    # Reload & shuffle mistake questions if filter/subject/user changes
    review_state_key = (filter_type, limit_count, subject, cur_user)
    if st.session_state.get('review_current_state') != review_state_key or 'review_loaded_qs' not in st.session_state:
        if filter_type == 'session_mistakes':
            raw_mistakes = list(session_mistakes)
        else:
            raw_mistakes = db.get_mistake_questions(limit=limit_count, filter_type=filter_type, subject=subject, username=cur_user)
            
        if st.session_state.get('shuffle_options', True):
            st.session_state.review_loaded_qs = quiz_engine.shuffle_questions_list(raw_mistakes)
        else:
            st.session_state.review_loaded_qs = raw_mistakes
        st.session_state.review_current_state = review_state_key
        st.session_state.review_q_idx = 0
        st.session_state.review_show_answer = False
        st.session_state.review_answers = {}
        
    mistake_questions = st.session_state.get('review_loaded_qs', [])
    
    if not mistake_questions:
        st.info("🎉 ยอดเยี่ยมมาก! ยังไม่มีรายการข้อสอบที่ตอบผิดในวิชานี้ หรือคุณได้ฝึกซ้ำจนครบแล้ว (ไปลองทำโหมดจำลองสอบเพื่อเริ่มเก็บสถิติ)")
        if st.button("🚀 ไปโหมดจำลองสอบ", type="primary"):
            st.session_state.current_page = 'exam'
            st.rerun()
        return
        
    st.write(f"พบข้อสอบที่เคยตอบผิด **{len(mistake_questions)}** ข้อ (🔀 สลับตำแหน่งตัวเลือกแล้ว)")
    
    # Sub-tabs for Review View
    tab1, tab2 = st.tabs(["📝 ฝึกทำซ้ำทีละข้อ (Interactive Re-test)", "📑 บัตรคำช่วยจำ & สรุปข้อผิด (Flashcards)"])
    
    # Tab 1: Interactive Re-test
    with tab1:
        render_interactive_review(mistake_questions)
        
    # Tab 2: Flashcards
    with tab2:
        render_flashcards_view(mistake_questions)

def render_interactive_review(questions):
    total = len(questions)
    idx = st.session_state.get('review_q_idx', 0)
    if idx >= total:
        idx = 0
        st.session_state.review_q_idx = 0
        
    q = questions[idx]
    
    if 'review_answers' not in st.session_state:
        st.session_state.review_answers = {}
    review_answers = st.session_state.review_answers
    answered_info = review_answers.get(idx, None)

    # Two-column layout: Left Question & Choices, Right Mistake Navigator Palette
    col_main, col_sidebar = st.columns([2.2, 1.3])
    
    with col_main:
        # Progress & Stats header
        is_fixed = (q.get('times_wrong', 0) == 0) or (answered_info is not None and answered_info.get('is_correct'))
        
        if is_fixed:
            stat_badges = (
                f'<span style="font-size: 0.85rem; color: #10b981; font-weight: 700; background: #ecfdf5; padding: 4px 12px; border-radius: 8px; border: 1px solid #a7f3d0;">'
                f'🎉 ซ่อมผ่านแล้ว (ปลดออกจากคลังข้อผิดเรียบร้อย ✅)</span> &nbsp;|&nbsp; '
                f'<span style="font-size: 0.85rem; color: #10b981; font-weight: 600;">✅ ตอบถูกสะสม: {q.get("times_correct", 0)} ครั้ง</span>'
            )
        else:
            stat_badges = (
                f'<span style="font-size: 0.85rem; color: #ef4444; font-weight: 600;">❌ เคยตอบผิด: {q.get("times_wrong", 0)} ครั้ง</span> &nbsp;|&nbsp; '
                f'<span style="font-size: 0.85rem; color: #10b981; font-weight: 600;">✅ ตอบถูกสะสม: {q.get("times_correct", 0)} ครั้ง</span>'
            )

        header_html = (
            f'<div style="display: flex; justify-content: space-between; align-items: center; background: #f8fafc; padding: 12px 18px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 16px;">'
            f'<div><span style="font-weight: 700; color: #1e3a8a;">ข้อที่ {idx + 1} จาก {total}</span></div>'
            f'<div>{stat_badges}</div>'
            f'</div>'
        )
        st.markdown(header_html, unsafe_allow_html=True)
        
        # Progress
        ans_count = len(review_answers)
        st.progress((idx + 1) / total, text=f"กำลังทำข้อที่ {idx + 1}/{total} (ตอบเสร็จแล้ว {ans_count}/{total} ข้อ)")
        
        # Question Card
        with st.container(border=True):
            st.markdown(f'''
            <div class="question-header">
                <div>
                    <span class="q-number" style="background: #fee2e2; color: #991b1b;">ข้อที่ {idx + 1} / {total}</span>
                </div>
                <div style="font-size: 0.85rem; color: #94a3b8;">
                    ID: {q['id']}
                </div>
            </div>
            ''', unsafe_allow_html=True)
            st.markdown(q['question'], unsafe_allow_html=True)
            st.write("")
        
        options = q['options']
        choice_letters = styles.get_choice_letters()
        correct_idx = q.get('answer_index', 0)
        
        # Check if this question has been answered
        if answered_info is None:
            st.markdown("<p style='font-size: 1rem; font-weight: 600; color: #4338ca; margin-bottom: 10px;'>⚡ แตะเลือกคำตอบ (ตรวจพร้อมเฉลยทันที):</p>", unsafe_allow_html=True)
            for c_idx, opt in enumerate(options):
                c_letter = choice_letters[c_idx]
                if st.button(f"**{c_letter}.**  {opt}", key=f"rev_btn_{q['id']}_{idx}_{c_idx}", use_container_width=True):
                    is_correct = (c_idx == correct_idx)
                    cur_u = st.session_state.get('current_user', 'เฟิส')
                    db.record_answer(q['id'], c_idx, is_correct, clear_mistake_on_correct=True, username=cur_u)
                    # Update in-memory question stats immediately so user sees live update!
                    if is_correct:
                        q['times_correct'] = q.get('times_correct', 0) + 1
                        q['times_wrong'] = 0 # Cleared!
                        if 'mistakes' in st.session_state:
                            st.session_state.mistakes = [m for m in st.session_state.mistakes if m.get('id') != q['id']]
                    else:
                        q['times_wrong'] = q.get('times_wrong', 0) + 1
                        
                    st.session_state.review_answers[idx] = {'selected': c_idx, 'is_correct': is_correct}
                    st.rerun()
                    
            st.write("")
            c_btn1, c_btn2, c_btn3 = st.columns([1, 1, 1.2])
            with c_btn1:
                if st.button("⬅️ ข้อก่อนหน้า", disabled=(idx == 0), key="rev_prev_unans", use_container_width=True):
                    st.session_state.review_q_idx -= 1
                    st.rerun()
            with c_btn2:
                if st.button("ข้ามไปข้อถัดไป ➡️", disabled=(idx == total - 1), key="rev_next_unans", use_container_width=True):
                    st.session_state.review_q_idx += 1
                    st.rerun()
            with c_btn3:
                if st.button("🗑️ ปลดข้อนี้ออกจากคลังข้อผิด", key="rev_clear_unans", use_container_width=True, help="ลบข้อนี้ออกจากคลังข้อผิดทันที"):
                    cur_u = st.session_state.get('current_user', 'เฟิส')
                    db.clear_question_mistake(q['id'], username=cur_u)
                    q['times_wrong'] = 0
                    st.session_state.review_answers[idx] = {'selected': correct_idx, 'is_correct': True}
                    st.rerun()
        else:
            user_choice = answered_info['selected']
            is_correct = answered_info['is_correct']
            
            if is_correct:
                st.success("🎉 **ยอดเยี่ยมมาก! คุณซ่อมข้อนี้ถูกต้องแล้ว** (ระบบได้ปลดข้อนี้ออกจากคลังข้อผิด และอัปเดตสถิติเรียบร้อย ✅)")
            else:
                st.error(f"❌ **ยังไม่ถูกต้อง** (เฉลยที่ถูกต้องคือ: **{choice_letters[correct_idx]}. {options[correct_idx]}**)")
            
            st.markdown("<p style='font-size: 1rem; font-weight: 600; color: #4338ca; margin-bottom: 10px;'>🎯 ผลการตรวจคำตอบ:</p>", unsafe_allow_html=True)
            for c_idx, opt in enumerate(options):
                c_letter = choice_letters[c_idx]
                if c_idx == correct_idx and c_idx == user_choice:
                    st.success(f"**{c_letter}.**  {opt}  *(คำตอบของคุณ - ถูกต้อง! ✅)*")
                elif c_idx == correct_idx:
                    st.success(f"**{c_letter}.**  {opt}  *(เฉลยที่ถูกต้อง 🎯)*")
                elif c_idx == user_choice:
                    st.error(f"**{c_letter}.**  {opt}  *(คุณเลือกข้อนี้ ❌)*")
                else:
                    st.markdown(
                        f'<div style="padding: 10px 14px; background: #f8fafc; border-radius: 8px; margin-bottom: 6px; border: 1px solid #e2e8f0; color: #475569; font-size: 0.95rem;">'
                        f'<b>{c_letter}.</b> {opt}</div>',
                        unsafe_allow_html=True
                    )
                    
            # Explanation Box
            subj = q.get('subject', 'computer' if str(q.get('id', '')).startswith('COM') else 'law')
            ref_label = "📖 หมวดหมู่วิชา" if subj == 'computer' else "📖 อ้างอิง"
            ref_val = (q.get('topic') or q.get('category', 'ทั่วไป')) if subj == 'computer' else q.get('law_ref', 'พ.ร.บ.ระเบียบบริหารราชการศาลยุติธรรม')
            exp_box_class = 'explanation-box' if is_correct else 'explanation-wrong-box'
            exp_text = q.get('explanation', '')
            st.markdown(
                f'<div class="{exp_box_class}">'
                f'<span class="law-ref-pill">{ref_label}: {ref_val}</span><br>'
                f'<b>เหตุผลและคำอธิบาย:</b> {exp_text}</div>',
                unsafe_allow_html=True
            )
            
            # Legal References & Precedents Engine
            legal_engine.render_legal_reference_expander(q, expanded=False)
            
            st.write("")
            c_btn1, c_btn2, c_btn3, c_btn4 = st.columns([1, 1.4, 1, 1.2])
            with c_btn1:
                if st.button("⬅️ ข้อก่อนหน้า", disabled=(idx == 0), key="rev_prev_ans", use_container_width=True):
                    st.session_state.review_q_idx -= 1
                    st.rerun()
            with c_btn2:
                if st.button("ข้อถัดไป ➡️", disabled=(idx == total - 1), type="primary", key="rev_next_ans", use_container_width=True):
                    st.session_state.review_q_idx += 1
                    st.rerun()
            with c_btn3:
                if st.button("🔄 ตอบใหม่", key="rev_retry_btn", use_container_width=True, help="ล้างคำตอบของข้อนี้เพื่อลองเลือกใหม่อีกครั้ง"):
                    del st.session_state.review_answers[idx]
                    st.rerun()
            with c_btn4:
                if st.button("🗑️ ปลดข้อผิด", key="rev_clear_ans", use_container_width=True, help="ลบข้อนี้ออกจากคลังข้อผิดอย่างถาวร"):
                    cur_u = st.session_state.get('current_user', 'เฟิส')
                    db.clear_question_mistake(q['id'], username=cur_u)
                    q['times_wrong'] = 0
                    st.toast("✅ ปลดข้อนี้ออกจากคลังข้อผิดเรียบร้อยแล้ว", icon="🗑️")
                    st.rerun()

    # Sidebar / Right Navigator Palette
    with col_sidebar:
        st.markdown("<h4 style='margin: 0 0 10px 0;'>📌 แผงเลือกข้อทบทวน</h4>", unsafe_allow_html=True)
        
        # Legend
        st.markdown(
            '<div style="font-size: 0.78rem; display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; background: rgba(0,0,0,0.04); padding: 8px 12px; border-radius: 8px;">'
            '<span>🔵 <b>กำลังทำ</b></span> '
            '<span>🟢 <b>แก้ถูก</b></span> '
            '<span>🔴 <b>ยังผิด</b></span> '
            '<span>⚪ <b>ยังไม่ทำ</b></span>'
            '</div>',
            unsafe_allow_html=True
        )
        
        # Grid of questions
        grid_cols = st.columns(5)
        for i in range(total):
            col_target = grid_cols[i % 5]
            is_cur = (i == idx)
            ans_info = review_answers.get(i, None)
            if ans_info is not None:
                label = f"{i+1}🟢" if ans_info['is_correct'] else f"{i+1}🔴"
            elif is_cur:
                label = f"{i+1}🔵"
            else:
                label = f"{i+1}⚪"
                
            btn_type = "primary" if is_cur else "secondary"
            if col_target.button(label, key=f"rev_nav_{i}", type=btn_type, use_container_width=True):
                st.session_state.review_q_idx = i
                st.rerun()
                
            st.write("---")
            
        # Stats summary in right column
        ans_count = len(review_answers)
        correct_count = sum(1 for a in review_answers.values() if a['is_correct'])
        wrong_count = sum(1 for a in review_answers.values() if not a['is_correct'])
        acc = int((correct_count / ans_count * 100)) if ans_count > 0 else 0
        acc_color = '#10b981' if acc >= 60 else '#ef4444'
        
        st.markdown(
            f'<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; margin-bottom: 12px;">'
            f'<div style="font-weight: 700; color: #4338ca; margin-bottom: 8px; font-size: 0.9rem;">🎯 สรุปผลการซ่อมข้อผิด</div>'
            f'<div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;"><span style="color: #64748b;">ทบทวนแล้ว:</span><b style="color: #0f172a;">{ans_count} / {total} ข้อ</b></div>'
            f'<div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;"><span style="color: #10b981;">แก้ไขถูก:</span><b style="color: #10b981;">{correct_count} ข้อ</b></div>'
            f'<div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;"><span style="color: #ef4444;">ยังผิดอยู่:</span><b style="color: #ef4444;">{wrong_count} ข้อ</b></div>'
            f'<div style="display: flex; justify-content: space-between; font-size: 0.85rem;"><span style="color: #64748b;">อัตราแก้สำเร็จ:</span><b style="color: {acc_color};">{acc}%</b></div>'
            f'</div>',
            unsafe_allow_html=True
        )

        if ans_count == total and total > 0:
            st.success(f"🎉 **ซ่อมครบทั้ง {total} ข้อแล้ว!** (แก้ถูก {correct_count} ข้อ)")
            if wrong_count > 0:
                if st.button(f"🔁 ทำซ้ำเฉพาะข้อที่ยังผิด ({wrong_count} ข้อ)", type="primary", use_container_width=True, key="rev_retry_wrongs"):
                    wrong_indices = [i for i, a in review_answers.items() if not a['is_correct']]
                    st.session_state.review_loaded_qs = [questions[i] for i in wrong_indices]
                    st.session_state.review_answers = {}
                    st.session_state.review_q_idx = 0
                    st.rerun()
            if st.button("🔄 ดึงข้อผิดชุดใหม่", use_container_width=True, key="rev_load_fresh"):
                if 'review_current_state' in st.session_state:
                    del st.session_state['review_current_state']
                if 'review_loaded_qs' in st.session_state:
                    del st.session_state['review_loaded_qs']
                st.rerun()

def render_flashcards_view(questions):
    st.markdown("คลิกที่แต่ละข้อเพื่อเปิดดูเฉลย คำอธิบาย และมาตรากฎหมายอ้างอิง")
    choice_letters = styles.get_choice_letters()
    
    for i, q in enumerate(questions):
        with st.expander(f"ข้อ {i+1} [{q.get('category', 'ทั่วไป')}]: {q['question'][:65]}... (ผิด {q['times_wrong']} ครั้ง)"):
            st.markdown(f"**คำถาม:** {q['question']}")
            
            for c_idx, opt in enumerate(q['options']):
                c_letter = choice_letters[c_idx]
                if c_idx == q['answer_index']:
                    st.success(f"**{c_letter}.** {opt}  👈 **เฉลยที่ถูกต้อง**")
                else:
                    st.write(f"**{c_letter}.** {opt}")
                    
            exp_ref = q.get('law_ref', 'พ.ร.บ.ระเบียบบริหารราชการศาลยุติธรรม')
            exp_detail = q.get('explanation', '')
            st.markdown(
                f'<div class="explanation-box">'
                f'<span class="law-ref-pill">📖 อ้างอิง: {exp_ref}</span><br>'
                f'<b>คำอธิบาย:</b> {exp_detail}</div>',
                unsafe_allow_html=True
            )
            
            # Legal References & Precedents Engine
            legal_engine.render_legal_reference_expander(q, expanded=False)
            
            fc_col1, fc_col2 = st.columns([3, 1])
            with fc_col2:
                if st.button("🗑️ ปลดออกจากคลังข้อผิด", key=f"fc_clear_{q['id']}_{i}", use_container_width=True, help="ลบข้อนี้ออกจากคลังข้อผิดทันที"):
                    cur_u = st.session_state.get('current_user', 'เฟิส')
                    db.clear_question_mistake(q['id'], username=cur_u)
                    q['times_wrong'] = 0
                    st.toast("✅ ปลดข้อนี้ออกจากคลังข้อผิดเรียบร้อยแล้ว", icon="🗑️")
                    st.rerun()
