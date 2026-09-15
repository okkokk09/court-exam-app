# -*- coding: utf-8 -*-
import streamlit as st
import db
import quiz_engine
import legal_engine
import styles

def render_practice_view():
    st.markdown('''
    <div style="background: linear-gradient(135deg, #065f46 0%, #047857 50%, #059669 100%); padding: 24px 28px; border-radius: 16px; color: white; margin-bottom: 24px; border: 1px solid #34d399;">
        <h2 style="margin: 0 0 8px 0; color: #ffffff;">📚 โหมดฝึกทำแยกหมวดหมู่ (Topic Practice)</h2>
        <p style="margin: 0; color: #d1fae5; font-size: 1rem;">
            ฝึกทำข้อสอบเจาะลึกเฉพาะหมวดหมู่ที่ต้องการ สลับตำแหน่งตัวเลือกอัตโนมัติป้องกันการจำตำแหน่ง
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    subject = st.session_state.get('selected_subject', 'law')
    categories = db.get_all_categories(subject=subject)
    cat_names = ["ทั้งหมด"] + [c[0] for c in categories]
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        selected_cat = st.selectbox(
            "📂 เลือกหมวดหมู่ที่ต้องการฝึกทำ:",
            cat_names,
            index=0,
            key="practice_cat_select"
        )
    with col2:
        st.write("")
        st.write("")
        shuffle_choices_opt = st.checkbox("🔀 สลับตัวเลือก (ก-ง)", value=st.session_state.get('shuffle_options', True))
    with col3:
        st.write("")
        st.write("")
        if st.button("🔄 เริ่มหมวดนี้ใหม่", use_container_width=True, help="ล้างข้อที่ทำค้างไว้และเริ่มข้อที่ 1 ใหม่โดยไม่กระทบสถิติ"):
            st.session_state.practice_q_idx = 0
            st.session_state.practice_show_answer = False
            raw_qs = db.get_all_questions(category=selected_cat if selected_cat != "ทั้งหมด" else None, subject=subject)
            st.session_state.practice_loaded_qs = quiz_engine.shuffle_questions_list(raw_qs) if shuffle_choices_opt else raw_qs
            st.rerun()
        
    # Check if category changed to reload questions
    current_cat_state = st.session_state.get('practice_current_cat', None)
    current_subj_state = st.session_state.get('practice_current_subj', None)
    
    if current_cat_state != selected_cat or current_subj_state != subject or 'practice_loaded_qs' not in st.session_state:
        raw_qs = db.get_all_questions(category=selected_cat if selected_cat != "ทั้งหมด" else None, subject=subject)
        if shuffle_choices_opt:
            st.session_state.practice_loaded_qs = quiz_engine.shuffle_questions_list(raw_qs)
        else:
            st.session_state.practice_loaded_qs = raw_qs
        st.session_state.practice_current_cat = selected_cat
        st.session_state.practice_current_subj = subject
        st.session_state.practice_q_idx = 0
        st.session_state.practice_answers = {}
        
    questions = st.session_state.get('practice_loaded_qs', [])
        
    if not questions:
        st.warning("ไม่พบข้อสอบในหมวดหมู่นี้")
        return
        
    total = len(questions)
    idx = st.session_state.get('practice_q_idx', 0)
    if idx >= total:
        idx = 0
        st.session_state.practice_q_idx = 0
        
    q = questions[idx]
    
    # Header bar
    cur_user = st.session_state.get('current_user', 'User 1')
    bookmarks = db.get_all_bookmarks(username=cur_user)
    is_bm = q['id'] in bookmarks

    if 'practice_answers' not in st.session_state:
        st.session_state.practice_answers = {}
    practice_answers = st.session_state.practice_answers

    # Two-column layout: Left Question & Choices, Right Quick Navigator Palette
    col_main, col_sidebar = st.columns([2.2, 1.3])

    with col_main:
        # Header bar
        st.markdown(f'''
        <div style="display: flex; justify-content: space-between; align-items: center; background: #f8fafc; padding: 12px 18px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 16px;">
            <div>
                <span style="font-weight: 700; color: #047857;">ข้อที่ {idx + 1} จาก {total}</span>
            </div>
            <div>
                <span style="font-size: 0.85rem; color: #64748b;">ID: {q['id']} ({cur_user})</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Progress
        st.progress((idx + 1) / total, text=f"ความคืบหน้า {idx + 1}/{total} ข้อ")
        
        # Question Card
        st.markdown(f'''
        <div class="question-card" style="border-left: 5px solid #059669;">
            <div class="q-text">
                {q['question']}
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        options = q['options']
        choice_letters = styles.get_choice_letters()
        correct_idx = q.get('answer_index', 0)
        
        # Check if this question has been answered
        answered_info = practice_answers.get(idx, None)
        
        if answered_info is None:
            st.markdown("<p style='font-size: 1rem; font-weight: 600; color: #047857; margin-bottom: 10px;'>⚡ แตะเลือกคำตอบ (ตรวจพร้อมเฉลยทันที):</p>", unsafe_allow_html=True)
            for c_idx, opt in enumerate(options):
                c_letter = choice_letters[c_idx]
                if st.button(f"**{c_letter}.**  {opt}", key=f"prac_btn_{q['id']}_{idx}_{c_idx}", use_container_width=True):
                    is_correct = (c_idx == correct_idx)
                    db.record_answer(q['id'], c_idx, is_correct, username=cur_user)
                    st.session_state.practice_answers[idx] = {'selected': c_idx, 'is_correct': is_correct}
                    st.rerun()
                    
            st.write("")
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                if st.button("⬅️ ข้อก่อนหน้า", disabled=(idx == 0), key="prac_prev_unans", use_container_width=True):
                    st.session_state.practice_q_idx -= 1
                    st.rerun()
            with c2:
                if st.button("ข้ามไปข้อถัดไป ➡️", disabled=(idx == total - 1), key="prac_next_unans", use_container_width=True):
                    st.session_state.practice_q_idx += 1
                    st.rerun()
            with c3:
                bm_label = "🚩 ปักหมุดแล้ว" if is_bm else "🏳️ ปักหมุด"
                if st.button(bm_label, key="prac_bm_unans", use_container_width=True):
                    db.toggle_bookmark(q['id'], username=cur_user)
                    st.rerun()
        else:
            user_choice = answered_info['selected']
            is_correct = answered_info['is_correct']
            
            st.markdown("<p style='font-size: 1rem; font-weight: 600; color: #047857; margin-bottom: 10px;'>🎯 ผลการตรวจคำตอบ:</p>", unsafe_allow_html=True)
            for c_idx, opt in enumerate(options):
                c_letter = choice_letters[c_idx]
                if c_idx == correct_idx and c_idx == user_choice:
                    st.success(f"**{c_letter}.**  {opt}  *(คำตอบของคุณ - ถูกต้อง! ✅)*")
                elif c_idx == correct_idx:
                    st.success(f"**{c_letter}.**  {opt}  *(เฉลยที่ถูกต้อง 🎯)*")
                elif c_idx == user_choice:
                    st.error(f"**{c_letter}.**  {opt}  *(คุณเลือกข้อนี้ ❌)*")
                else:
                    st.markdown(f'''
                    <div style="padding: 10px 14px; background: #f8fafc; border-radius: 8px; margin-bottom: 6px; border: 1px solid #e2e8f0; color: #475569; font-size: 0.95rem;">
                        <b>{c_letter}.</b> {opt}
                    </div>
                    ''', unsafe_allow_html=True)
                    
            # Explanation Box
            st.markdown(f'''
            <div class="{'explanation-box' if is_correct else 'explanation-wrong-box'}">
                <span class="law-ref-pill">📖 อ้างอิง: {q.get('law_ref', 'พ.ร.บ.ระเบียบบริหารราชการศาลยุติธรรม')}</span><br>
                <b>เหตุผลและคำอธิบาย:</b> {q.get('explanation', '')}
            </div>
            ''', unsafe_allow_html=True)
            
            # Legal References & Precedents Engine
            legal_engine.render_legal_reference_expander(q, expanded=True)
            
            st.write("")
            c1, c2, c3, c4 = st.columns([1, 1.5, 1, 1])
            with c1:
                if st.button("⬅️ ข้อก่อนหน้า", disabled=(idx == 0), key="prac_prev_ans", use_container_width=True):
                    st.session_state.practice_q_idx -= 1
                    st.rerun()
            with c2:
                if st.button("ข้อถัดไป ➡️", disabled=(idx == total - 1), type="primary", key="prac_next_ans", use_container_width=True):
                    st.session_state.practice_q_idx += 1
                    st.rerun()
            with c3:
                if st.button("🔄 ตอบข้อนี้ใหม่", key="prac_retry_btn", use_container_width=True, help="ล้างคำตอบของข้อนี้เพื่อลองเลือกใหม่อีกครั้ง"):
                    del st.session_state.practice_answers[idx]
                    st.rerun()
            with c4:
                bm_label = "🚩 ปักหมุดแล้ว" if is_bm else "🏳️ ปักหมุด"
                if st.button(bm_label, key="prac_bm_ans", use_container_width=True):
                    db.toggle_bookmark(q['id'], username=cur_user)
                    st.rerun()

    # Sidebar / Right Navigator Palette
    with col_sidebar:
        st.markdown("<h4 style='margin: 0 0 10px 0;'>📌 แผงเลือกข้อฝึกทำ</h4>", unsafe_allow_html=True)
        
        # Legend
        st.markdown('''
        <div style="font-size: 0.78rem; display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; background: rgba(0,0,0,0.04); padding: 8px 12px; border-radius: 8px;">
            <span>🔵 <b>กำลังทำ</b></span>
            <span>🟢 <b>ถูก</b></span>
            <span>🔴 <b>ผิด</b></span>
            <span>⚪ <b>ยังไม่ตอบ</b></span>
            <span>🚩 <b>หมุด</b></span>
        </div>
        ''', unsafe_allow_html=True)
        
        # Grid of questions
        grid_cols = st.columns(5)
        for i in range(total):
            col_target = grid_cols[i % 5]
            is_cur = (i == idx)
            ans_info = practice_answers.get(i, None)
            is_q_bm = questions[i]['id'] in bookmarks
            
            if is_q_bm:
                label = f"{i+1}🚩"
            elif ans_info is not None:
                label = f"{i+1}🟢" if ans_info['is_correct'] else f"{i+1}🔴"
            elif is_cur:
                label = f"{i+1}🔵"
            else:
                label = f"{i+1}⚪"
                
            btn_type = "primary" if is_cur else "secondary"
            if col_target.button(label, key=f"prac_nav_{i}", type=btn_type, use_container_width=True):
                st.session_state.practice_q_idx = i
                st.rerun()
                
        st.write("---")
        
        # Stats summary in right column
        ans_count = len(practice_answers)
        correct_count = sum(1 for a in practice_answers.values() if a['is_correct'])
        wrong_count = sum(1 for a in practice_answers.values() if not a['is_correct'])
        acc = int((correct_count / ans_count * 100)) if ans_count > 0 else 0
        
        st.markdown(f'''
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; margin-bottom: 12px;">
            <div style="font-weight: 700; color: #047857; margin-bottom: 8px; font-size: 0.9rem;">📊 สรุปการฝึกทำชุดนี้</div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                <span style="color: #64748b;">ทำแล้ว:</span>
                <b style="color: #0f172a;">{ans_count} / {total} ข้อ</b>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                <span style="color: #10b981;">ตอบถูก:</span>
                <b style="color: #10b981;">{correct_count} ข้อ</b>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                <span style="color: #ef4444;">ตอบผิด:</span>
                <b style="color: #ef4444;">{wrong_count} ข้อ</b>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                <span style="color: #64748b;">ความแม่นยำ:</span>
                <b style="color: {'#10b981' if acc >= 60 else '#ef4444'};">{acc}%</b>
            </div>
        </div>
        ''', unsafe_allow_html=True)
