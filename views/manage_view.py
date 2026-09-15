# -*- coding: utf-8 -*-
import streamlit as st
import json
import db
import styles

def render_manage_view():
    st.markdown('''
    <div style="background: linear-gradient(135deg, #374151 0%, #1f2937 100%); padding: 24px 28px; border-radius: 16px; color: white; margin-bottom: 24px; border: 1px solid #9ca3af;">
        <h2 style="margin: 0 0 8px 0; color: #ffffff;">⚙️ คลังข้อสอบ & การจัดการ (Question Bank Manager)</h2>
        <p style="margin: 0; color: #d1d5db; font-size: 1rem;">
            ค้นหา ตรวจสอบข้อสอบทั้งหมดในระบบ และเพิ่มข้อสอบใหม่ได้ตามต้องการ
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔍 ค้นหาและดูคลังข้อสอบ", "➕ เพิ่มข้อสอบใหม่", "🚩 ข้อสอบที่ปักหมุดไว้"])
    
    # Tab 1: Search & Browse
    with tab1:
        render_search_tab()
        
    # Tab 2: Add Question
    with tab2:
        render_add_tab()
        
    # Tab 3: Bookmarks
    with tab3:
        render_bookmarks_tab()

def render_search_tab():
    subject = st.session_state.get('selected_subject', 'law')
    
    c_s, c1, c2 = st.columns([1.5, 2, 1.5])
    with c_s:
        subj_filter = st.selectbox(
            "📖 กรองตามวิชา:",
            [('all', '📚 ทุกวิชาในระบบ'), ('law', '⚖️ กฎหมายศาลยุติธรรม'), ('computer', '💻 คอมพิวเตอร์และสารสนเทศ')],
            index=0 if subject == 'all' else (1 if subject == 'law' else 2),
            format_func=lambda x: x[1]
        )
        chosen_subj = None if subj_filter[0] == 'all' else subj_filter[0]
        
    all_questions = db.get_all_questions(subject=chosen_subj)
    categories = ["ทั้งหมด"] + [c[0] for c in db.get_all_categories(subject=chosen_subj)]
    
    with c1:
        search_query = st.text_input("🔍 ค้นหาคำสำคัญ, มาตรา หรือเนื้อหาข้อสอบ:", placeholder="เช่น ก.บ.ศ., CPU, มาตรา 10, Excel...")
    with c2:
        cat_filter = st.selectbox("📂 กรองตามหมวดหมู่:", categories)
        
    filtered = []
    for q in all_questions:
        if cat_filter != "ทั้งหมด" and q['category'] != cat_filter:
            continue
        if search_query:
            q_text = q['question'] + " " + q.get('explanation', '') + " " + q.get('law_ref', '') + " " + q.get('topic', '')
            if search_query.lower() not in q_text.lower():
                continue
        filtered.append(q)
        
    st.write(f"พบข้อสอบ **{len(filtered)}** ข้อ (จากทั้งหมด {len(all_questions)} ข้อ)")
    
    choice_letters = styles.get_choice_letters()
    for i, q in enumerate(filtered):
        subj_icon = "💻" if q.get('subject') == 'computer' else "⚖️"
        with st.expander(f"{subj_icon} {q['id']} [{q['category']}]: {q['question'][:75]}..."):
            st.markdown(f"**วิชา:** {'คอมพิวเตอร์และสารสนเทศ' if q.get('subject') == 'computer' else 'กฎหมายศาลยุติธรรม'} | **หัวข้อ:** {q.get('topic', '-')}")
            st.markdown(f"**คำถาม:** {q['question']}")
            
            for c_idx, opt in enumerate(q['options']):
                c_letter = choice_letters[c_idx]
                if c_idx == q['answer_index']:
                    st.success(f"**{c_letter}.** {opt}  👈 **เฉลยที่ถูกต้อง**")
                else:
                    st.write(f"**{c_letter}.** {opt}")
                    
            st.markdown(f'''
            <div class="explanation-box">
                <span class="law-ref-pill">📖 อ้างอิง: {q.get('law_ref', 'พ.ร.บ.')}</span><br>
                <b>คำอธิบาย:</b> {q.get('explanation', '')}
            </div>
            ''', unsafe_allow_html=True)

def render_add_tab():
    st.subheader("📝 แบบฟอร์มเพิ่มข้อสอบใหม่เข้าสู่คลัง")
    
    cur_subj = st.session_state.get('selected_subject', 'law')
    
    with st.form("add_question_form"):
        f_subj = st.selectbox(
            "วิชาข้อสอบ:",
            [('law', '⚖️ วิชากฎหมายระเบียบบริหารศาลยุติธรรม'), ('computer', '💻 วิชาคอมพิวเตอร์และเทคโนโลยีสารสนเทศ')],
            index=0 if cur_subj == 'law' else 1,
            format_func=lambda x: x[1]
        )[0]
        
        cat_options = [c[0] for c in db.get_all_categories(subject=f_subj)]
        if not cat_options:
            if f_subj == 'computer':
                cat_options = ["ฮาร์ดแวร์และอุปกรณ์คอมพิวเตอร์", "ซอฟต์แวร์และระบบปฏิบัติการ", "โปรแกรมสำนักงานและงานเอกสาร", "ระบบเครือข่ายและอินเทอร์เน็ต", "ความมั่นคงปลอดภัยและ พ.ร.บ. คอมพิวเตอร์", "เทคโนโลยีดิจิทัลและ AI"]
            else:
                cat_options = ["บททั่วไปและคำนิยาม", "สำนักงานศาลยุติธรรม", "คณะกรรมการบริหารศาลยุติธรรม (ก.บ.ศ.)", "คณะกรรมการข้าราชการศาลยุติธรรม (ก.ศ.)", "การบริหารงานบุคคล", "งบประมาณและการเงิน"]
            
        f_cat = st.selectbox("หมวดหมู่:", cat_options + ["กำหนดหมวดหมู่ใหม่..."])
        if f_cat == "กำหนดหมวดหมู่ใหม่...":
            f_cat = st.text_input("ระบุชื่อหมวดหมู่ใหม่:")
            
        f_topic = st.text_input("หัวข้อย่อย (Topic):", placeholder="เช่น หน่วยความจำ RAM หรือ คุณสมบัติ ก.บ.ศ.")
        f_question = st.text_area("คำถามข้อสอบ:", placeholder="พิมพ์คำถามข้อสอบ...")
        
        c1, c2 = st.columns(2)
        with c1:
            opt_a = st.text_input("ตัวเลือก ก:")
            opt_b = st.text_input("ตัวเลือก ข:")
        with c2:
            opt_c = st.text_input("ตัวเลือก ค:")
            opt_d = st.text_input("ตัวเลือก ง:")
            
        f_ans = st.selectbox("ตัวเลือกที่ถูกต้อง (เฉลย):", [0, 1, 2, 3], format_func=lambda x: f"ตัวเลือก {['ก', 'ข', 'ค', 'ง'][x]}")
        f_law_ref = st.text_input("หัวข้อ/กฎหมายอ้างอิง:", placeholder="เช่น พ.ร.บ.คอมพิวเตอร์ฯ มาตรา 14 หรือ มาตรา 10 (1)")
        f_explanation = st.text_area("คำอธิบายเฉลยละเอียด:", placeholder="ระบุเหตุผลและหลักวิชาการ/กฎหมาย...")
        
        submitted = st.form_submit_button("💾 บันทึกข้อสอบเข้าสู่ฐานข้อมูล", type="primary")
        
        if submitted:
            if not f_question or not opt_a or not opt_b or not opt_c or not opt_d:
                st.error("กรุณากรอกคำถามและตัวเลือก ก-ง ให้ครบถ้วน")
            else:
                new_id = db.add_custom_question(
                    category=f_cat,
                    topic=f_topic,
                    question=f_question,
                    options=[opt_a, opt_b, opt_c, opt_d],
                    answer_index=f_ans,
                    explanation=f_explanation,
                    law_ref=f_law_ref,
                    subject=f_subj
                )
                st.success(f"บันทึกข้อสอบสำเร็จ! รหัสข้อสอบ: {new_id}")
                st.rerun()

def render_bookmarks_tab():
    cur_user = st.session_state.get('current_user', 'User 1')
    bookmarks = db.get_all_bookmarks(username=cur_user)
    if not bookmarks:
        st.info(f"ยังไม่มีข้อสอบที่ปักหมุดไว้สำหรับ {cur_user} (คุณสามารถกดปุ่มปักหมุดในโหมดสอบหรือโหมดฝึกฝนได้)")
        return
        
    all_q = {q['id']: q for q in db.get_all_questions()}
    st.write(f"รายการข้อสอบที่ปักหมุดไว้ ({cur_user}) **{len(bookmarks)}** ข้อ:")
    
    choice_letters = styles.get_choice_letters()
    for qid in bookmarks:
        if qid in all_q:
            q = all_q[qid]
            with st.expander(f"🚩 {q['id']} [{q['category']}]: {q['question'][:70]}..."):
                st.markdown(f"**คำถาม:** {q['question']}")
                for c_idx, opt in enumerate(q['options']):
                    c_letter = choice_letters[c_idx]
                    if c_idx == q['answer_index']:
                        st.success(f"**{c_letter}.** {opt}  👈 **เฉลย**")
                    else:
                        st.write(f"**{c_letter}.** {opt}")
                if st.button(f"🗑️ ปลดปักหมุด {qid}", key=f"unbm_{qid}"):
                    db.toggle_bookmark(qid, username=cur_user)
                    st.rerun()
