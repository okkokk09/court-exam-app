# -*- coding: utf-8 -*-
import streamlit as st
import db
import quiz_engine
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
    
    col1, col2 = st.columns([2, 1])
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
        shuffle_choices_opt = st.checkbox("🔀 สลับตำแหน่งตัวเลือก (ก-ง)", value=st.session_state.get('shuffle_options', True))
        
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
        st.session_state.practice_show_answer = False
        
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
    bookmarks = db.get_all_bookmarks()
    is_bm = q['id'] in bookmarks
    
    st.markdown(f'''
    <div style="display: flex; justify-content: space-between; align-items: center; background: #f8fafc; padding: 12px 18px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 16px;">
        <div>
            <span style="font-weight: 700; color: #047857;">ข้อที่ {idx + 1} จาก {total}</span>
            <span class="q-category-tag" style="margin-left: 8px;">{q.get('category', 'ทั่วไป')}</span>
            <span style="font-size: 0.85rem; color: #64748b; margin-left: 8px;">[{q.get('topic', '')}]</span>
        </div>
        <div>
            <span style="font-size: 0.85rem; color: #64748b;">ID: {q['id']}</span>
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
    formatted_options = [f"{choice_letters[i]}.  {opt}" for i, opt in enumerate(options)]
    
    st.markdown("<p style='font-size: 1rem; font-weight: 600; color: #047857; margin-bottom: 8px;'>📝 เลือกคำตอบของคุณ:</p>", unsafe_allow_html=True)
    selected_idx = st.radio(
        "ตัวเลือกคำตอบ",
        options=list(range(len(options))),
        format_func=lambda i: formatted_options[i],
        key=f"practice_radio_{q['id']}_{idx}",
        index=None,
        label_visibility="collapsed"
    )
    
    st.write("")
    c1, c2, c3, c4 = st.columns([1, 1, 1.5, 1])
    with c1:
        if st.button("⬅️ ข้อก่อน", disabled=(idx == 0), key="prac_prev", use_container_width=True):
            st.session_state.practice_q_idx -= 1
            st.session_state.practice_show_answer = False
            st.rerun()
    with c2:
        if st.button("ข้อถัดไป ➡️", disabled=(idx == total - 1), key="prac_next", use_container_width=True):
            st.session_state.practice_q_idx += 1
            st.session_state.practice_show_answer = False
            st.rerun()
    with c3:
        if st.button("🎯 ตรวจคำตอบ & เฉลย", type="primary", key="prac_check", use_container_width=True):
            if selected_idx is None:
                st.warning("กรุณาเลือกคำตอบก่อน")
            else:
                st.session_state.practice_show_answer = True
                is_correct = (selected_idx == q['answer_index'])
                db.record_answer(q['id'], selected_idx, is_correct)
                st.rerun()
    with c4:
        bm_label = "🚩 ปักหมุดแล้ว" if is_bm else "🏳️ ปักหมุด"
        if st.button(bm_label, key="prac_bm", use_container_width=True):
            db.toggle_bookmark(q['id'])
            st.rerun()

    # Feedback Box
    if st.session_state.get('practice_show_answer', False) and selected_idx is not None:
        is_correct = (selected_idx == q['answer_index'])
        if is_correct:
            st.success(f"🎉 ถูกต้อง! {choice_letters[q['answer_index']]}. {options[q['answer_index']]}")
        else:
            st.error(f"❌ ยังไม่ถูกต้อง (คำตอบที่ถูกคือ: {choice_letters[q['answer_index']]}. {options[q['answer_index']]})")
            
        st.markdown(f'''
        <div class="{'explanation-box' if is_correct else 'explanation-wrong-box'}">
            <span class="law-ref-pill">📖 อ้างอิง: {q.get('law_ref', 'พ.ร.บ.ระเบียบบริหารราชการศาลยุติธรรม')}</span><br>
            <b>เหตุผลและคำอธิบาย:</b> {q.get('explanation', '')}
        </div>
        ''', unsafe_allow_html=True)
