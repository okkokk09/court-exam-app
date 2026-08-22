# -*- coding: utf-8 -*-
import streamlit as st
import db
import quiz_engine
import styles

def render_review_view():
    st.markdown('''
    <div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%); padding: 24px 28px; border-radius: 16px; color: white; margin-bottom: 24px; border: 1px solid #818cf8;">
        <h2 style="margin: 0 0 8px 0; color: #ffffff;">🔄 โหมดทบทวนข้อผิดซ้ำ (Mistake Review & Mastery)</h2>
        <p style="margin: 0; color: #c7d2fe; font-size: 1rem;">
            ระบบดึงข้อสอบที่คุณเคยตอบผิดจากฐานข้อมูล SQLite มาให้ฝึกทำซ้ำจนกว่าจะแม่นยำ ปิดจุดอ่อนก่อนลงสนามจริง
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Filter selection
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        filter_opt = st.selectbox(
            "🎯 ตัวกรองข้อผิด:",
            [
                ('frequent_mistakes', '🔥 ข้อที่ตอบผิดบ่อยที่สุด (Top Frequent Mistakes)'),
                ('recent_mistakes', '⏰ ข้อที่ตอบผิดล่าสุด (Recent Errors)'),
                ('unmastered', '🛡️ ข้อที่ยังไม่แม่นยำ (Unmastered)'),
                ('all_mistakes', '📚 ข้อที่เคยตอบผิดทั้งหมด (All Logged Mistakes)')
            ],
            format_func=lambda x: x[1],
            key="review_filter_select"
        )
        filter_type = filter_opt[0]
        
    with col_f2:
        limit_count = st.number_input("จำนวนข้อที่ต้องการดึง:", min_value=5, max_value=100, value=20, step=5)
        
    subject = st.session_state.get('selected_subject', 'law')
    mistake_questions = db.get_mistake_questions(limit=limit_count, filter_type=filter_type, subject=subject)
    
    if not mistake_questions:
        st.info("🎉 ยอดเยี่ยมมาก! ยังไม่มีรายการข้อสอบที่ตอบผิดในวิชานี้ หรือคุณได้ฝึกซ้ำจนครบแล้ว (ไปลองทำโหมดจำลองสอบเพื่อเริ่มเก็บสถิติ)")
        if st.button("🚀 ไปโหมดจำลองสอบ", type="primary"):
            st.session_state.current_page = 'exam'
            st.rerun()
        return
        
    st.write(f"พบข้อสอบที่เคยตอบผิด **{len(mistake_questions)}** ข้อ")
    
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
    
    # Progress & Stats header
    st.markdown(f'''
    <div style="display: flex; justify-content: space-between; align-items: center; background: #f8fafc; padding: 12px 18px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 16px;">
        <div>
            <span style="font-weight: 700; color: #1e3a8a;">ข้อที่ {idx + 1} จาก {total}</span>
            <span class="q-category-tag" style="margin-left: 8px;">{q.get('category', 'ทั่วไป')}</span>
        </div>
        <div>
            <span style="font-size: 0.85rem; color: #ef4444; font-weight: 600;">❌ เคยตอบผิด: {q['times_wrong']} ครั้ง</span> |
            <span style="font-size: 0.85rem; color: #10b981; font-weight: 600;">✅ เคยตอบถูก: {q['times_correct']} ครั้ง</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Question Card
    st.markdown(f'''
    <div class="question-card" style="border-left: 5px solid #ef4444;">
        <div class="q-text" style="margin-bottom: 16px;">
            {q['question']}
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    options = q['options']
    choice_letters = styles.get_choice_letters()
    formatted_options = [f"{choice_letters[i]}.  {opt}" for i, opt in enumerate(options)]
    
    st.markdown("<p style='font-size: 1rem; font-weight: 600; color: #4338ca; margin-bottom: 8px;'>📝 เลือกคำตอบของคุณ:</p>", unsafe_allow_html=True)
    selected_idx = st.radio(
        "ตัวเลือกคำตอบ",
        options=list(range(len(options))),
        format_func=lambda i: formatted_options[i],
        key=f"review_radio_{q['id']}_{idx}",
        index=None,
        label_visibility="collapsed"
    )
    
    st.write("")
    c_btn1, c_btn2, c_btn3 = st.columns([1, 1, 2])
    
    with c_btn1:
        if st.button("⬅️ ข้อก่อน", disabled=(idx == 0), use_container_width=True):
            st.session_state.review_q_idx -= 1
            st.session_state.review_show_answer = False
            st.rerun()
            
    with c_btn2:
        if st.button("ข้อถัดไป ➡️", disabled=(idx == total - 1), use_container_width=True):
            st.session_state.review_q_idx += 1
            st.session_state.review_show_answer = False
            st.rerun()
            
    with c_btn3:
        if st.button("🎯 ตรวจคำตอบ & ดูเฉลย", type="primary", use_container_width=True):
            if selected_idx is None:
                st.warning("กรุณาเลือกคำตอบก่อนกดตรวจ")
            else:
                st.session_state.review_show_answer = True
                is_correct = (selected_idx == q['answer_index'])
                # Update DB immediately
                db.record_answer(q['id'], selected_idx, is_correct)
                st.rerun()
                
    # Display Instant Feedback
    if st.session_state.get('review_show_answer', False) and selected_idx is not None:
        is_correct = (selected_idx == q['answer_index'])
        if is_correct:
            st.success("🎉 ถูกต้องแล้ว! ระบบได้อัปเดตสถิติลดความเสี่ยงของข้อนี้เรียบร้อย")
        else:
            st.error(f"❌ ยังไม่ถูกต้อง (เฉลยที่ถูกคือ: {choice_letters[q['answer_index']]}. {options[q['answer_index']]})")
            
        st.markdown(f'''
        <div class="{'explanation-box' if is_correct else 'explanation-wrong-box'}">
            <span class="law-ref-pill">📖 อ้างอิง: {q.get('law_ref', 'พ.ร.บ.ระเบียบบริหารราชการศาลยุติธรรม')}</span><br>
            <b>เหตุผลและคำอธิบาย:</b> {q.get('explanation', '')}
        </div>
        ''', unsafe_allow_html=True)

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
                    
            st.markdown(f'''
            <div class="explanation-box">
                <span class="law-ref-pill">📖 อ้างอิง: {q.get('law_ref', 'พ.ร.บ.ระเบียบบริหารราชการศาลยุติธรรม')}</span><br>
                <b>คำอธิบาย:</b> {q.get('explanation', '')}
            </div>
            ''', unsafe_allow_html=True)
