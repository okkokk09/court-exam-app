# -*- coding: utf-8 -*-
import os
import re
import streamlit as st

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'knowledge_base')

TOPIC_TITLES = {
    '01_oag_org_act_2553.md': '⚖️ 1. พ.ร.บ.องค์กรอัยการและพนักงานอัยการ พ.ศ. 2553',
    '02_oag_civil_service_act_2553.md': '👥 2. พ.ร.บ.ระเบียบข้าราชการฝ่ายอัยการ พ.ศ. 2553',
    '03_cybersecurity_act_2562.md': '🛡️ 3. พ.ร.บ.การรักษาความมั่นคงปลอดภัยไซเบอร์ พ.ศ. 2562',
    '04_pdpa_2562.md': '🔒 4. พ.ร.บ.คุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562 (PDPA)',
    '05_saraban_2526.md': '📝 5. ระเบียบงานสารบรรณ พ.ศ. 2526 และที่แก้ไขเพิ่มเติม',
    '06_procurement_2560.md': '💼 6. ระเบียบการจัดซื้อจัดจ้างและการบริหารพัสดุฯ พ.ศ. 2560',
    '07_oag_policy_strategy.md': '🏛️ 7. นโยบาย ยุทธศาสตร์ และภารกิจสำนักงานอัยการสูงสุด'
}

def load_markdown_files():
    if not os.path.exists(KNOWLEDGE_DIR):
        os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
    files = sorted([f for f in os.listdir(KNOWLEDGE_DIR) if f.endswith('.md')])
    docs = {}
    for f in files:
        full_path = os.path.join(KNOWLEDGE_DIR, f)
        try:
            with open(full_path, 'r', encoding='utf-8') as fp:
                docs[f] = fp.read()
        except Exception:
            pass
    return docs

def render_knowledge_view():
    st.markdown('''
    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #3b82f6 100%); padding: 24px 28px; border-radius: 16px; color: white; margin-bottom: 24px; border: 1px solid #60a5fa;">
        <h2 style="margin: 0 0 8px 0; color: #ffffff;">📖 คลังสรุปจุดหลอกกฎหมาย & สาระสำคัญ (Knowledge Vault)</h2>
        <p style="margin: 0; color: #dbeafe; font-size: 1rem;">
            เจาะลึกตัวบทกฎหมาย 6 ฉบับ + นโยบาย อสส. คัดเฉพาะมาตราสำคัญ จุดหลอกยอดฮิต และข้อยกเว้นที่มักออกสอบ
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    docs = load_markdown_files()
    if not docs:
        st.warning("⚠️ ยังไม่พบไฟล์สรุปเนื้อหาในโฟลเดอร์ knowledge_base/")
        return
        
    c1, c2 = st.columns([2.5, 1.5])
    with c1:
        file_options = list(docs.keys())
        selected_file = st.selectbox(
            "📂 เลือกหัวข้อที่ต้องการอ่านสรุป:",
            options=file_options,
            format_func=lambda x: TOPIC_TITLES.get(x, x),
            key="knowledge_file_selector"
        )
    with c2:
        search_kw = st.text_input("🔍 ค้นหาคีย์เวิร์ดในเนื้อหา:", placeholder="เช่น มาตรา 14, เฉพาะเจาะจง, CII, 72 ชม...")
        
    st.write("---")
    
    content = docs.get(selected_file, "")
    
    if search_kw.strip():
        kw = search_kw.strip().lower()
        matched_files = []
        for fname, text in docs.items():
            if kw in text.lower():
                matched_files.append(fname)
        if matched_files:
            st.info(f"🔎 พบคำว่า **'{search_kw}'** ใน {len(matched_files)} เอกสาร: " + ", ".join([TOPIC_TITLES.get(f, f) for f in matched_files]))
        else:
            st.warning(f"❌ ไม่พบคีย์เวิร์ด '{search_kw}' ในคลังสรุป")
            
    # Clean and render markdown
    # Replace GitHub alerts with Streamlit markdown formatting
    styled_content = content
    styled_content = re.sub(
        r'> \[!WARNING\]\s*\n> (.*?)(?=\n\n|\n[^\>]|$)',
        r'<div style="background: rgba(239, 68, 68, 0.12); border-left: 4px solid #ef4444; padding: 12px 16px; border-radius: 4px 8px 8px 4px; margin: 14px 0;"><strong>⚠️ จุดหลอกยอดฮิต:</strong><br>\1</div>',
        styled_content,
        flags=re.DOTALL
    )
    styled_content = re.sub(
        r'> \[!TIP\]\s*\n> (.*?)(?=\n\n|\n[^\>]|$)',
        r'<div style="background: rgba(16, 185, 129, 0.12); border-left: 4px solid #10b981; padding: 12px 16px; border-radius: 4px 8px 8px 4px; margin: 14px 0;"><strong>💡 ข้อสังเกต / เทคนิคจำ:</strong><br>\1</div>',
        styled_content,
        flags=re.DOTALL
    )
    styled_content = re.sub(
        r'> \[!NOTE\]\s*\n> (.*?)(?=\n\n|\n[^\>]|$)',
        r'<div style="background: rgba(59, 130, 246, 0.12); border-left: 4px solid #3b82f6; padding: 12px 16px; border-radius: 4px 8px 8px 4px; margin: 14px 0;"><strong>ℹ️ ข้อมูลเพิ่มเติม:</strong><br>\1</div>',
        styled_content,
        flags=re.DOTALL
    )
    
    st.markdown(styled_content, unsafe_allow_html=True)
    
    st.write("---")
    st.caption("💡 แหล่งข้อมูลรวบรวมจากตัวบทกฎหมายฉบับแก้ไขเพิ่มเติมล่าสุด เพื่อใช้ติวสอบตำแหน่งนักวิชาการคอมพิวเตอร์ปฏิบัติการ สำนักงานอัยการสูงสุด")
