# -*- coding: utf-8 -*-
import streamlit as st
import json
from datetime import datetime
import exam_config
import db

def render_stats_view():
    cur_subj = st.session_state.get('selected_subject', 'law')
    is_com = (cur_subj == 'computer')
    cur_user = st.session_state.get('current_user', 'เฟิส')
    
    st.markdown('''
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%); padding: 24px 28px; border-radius: 16px; color: white; margin-bottom: 20px; border: 1px solid #64748b;">
        <h2 style="margin: 0 0 8px 0; color: #ffffff;">📊 แดชบอร์ดสถิติ & ประเมินผลสู่เป้าหมาย (Analytics & Benchmark)</h2>
        <p style="margin: 0; color: #94a3b8; font-size: 1rem;">
            วิเคราะห์ความพร้อมสู่การสอบแข่งขันนักวิชาการคอมพิวเตอร์ปฏิบัติการ สำนักงานอัยการสูงสุด (ภาค ข. 200 คะแนน)
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # 1. Target Benchmark Card (160/200 Points)
    render_target_benchmark_card()
    
    # Subject & Mode Switcher for Dashboard
    st.markdown("<p style='font-size: 1rem; font-weight: 700; color: #1e3a8a; margin-bottom: 8px;'>🎯 เลือกดูสถิติและผลการประเมิน:</p>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1.3, 1.3, 1.8, 1.3])
    
    view_mode = st.session_state.get('stats_view_mode', 'subject')
    
    with c1:
        law_type = "primary" if not is_com and view_mode == 'subject' else "secondary"
        if st.button("⚖️ สถิติวิชากฎหมาย", type=law_type, use_container_width=True, key="stats_btn_law"):
            st.session_state.selected_subject = 'law'
            st.session_state.stats_view_mode = 'subject'
            st.rerun()
    with c2:
        com_type = "primary" if is_com and view_mode == 'subject' else "secondary"
        if st.button("💻 สถิติวิชาคอมฯ", type=com_type, use_container_width=True, key="stats_btn_com"):
            st.session_state.selected_subject = 'computer'
            st.session_state.stats_view_mode = 'subject'
            st.rerun()
    with c3:
        full_type = "primary" if view_mode == 'full_exam' else "secondary"
        if st.button("🏆 สถิติสอบจริงเต็มรูปแบบ (200 คะแนน)", type=full_type, use_container_width=True, key="stats_btn_full"):
            st.session_state.stats_view_mode = 'full_exam'
            st.rerun()
    with c4:
        cmp_type = "primary" if view_mode == 'compare' else "secondary"
        if st.button("📊 เปรียบเทียบ 2 วิชา", type=cmp_type, use_container_width=True, key="stats_btn_cmp"):
            st.session_state.stats_view_mode = 'compare'
            st.rerun()

    st.write("")
    
    if view_mode == 'full_exam':
        render_full_exam_dashboard()
    elif view_mode == 'compare':
        render_comparison_dashboard()
    else:
        if is_com:
            render_subject_dashboard('computer', '💻 วิชาคอมพิวเตอร์และเทคโนโลยีสารสนเทศ', '#0284c7')
        else:
            render_subject_dashboard('law', '⚖️ วิชา' + exam_config.get_active(st.session_state)['law_label'], '#1e40af')

    # Backup & Restore Section (JSON Export/Import)
    render_backup_restore_section()

def render_target_benchmark_card():
    cur_user = st.session_state.get('current_user', 'เฟิส')
    law_stats = db.get_dashboard_stats(subject='law', username=cur_user)
    com_stats = db.get_dashboard_stats(subject='computer', username=cur_user)
    
    law_pct = law_stats.get('avg_score', 0.0)
    com_pct = com_stats.get('avg_score', 0.0)
    
    # 50 questions law (100 pts) + 50 questions computer (100 pts) = 200 pts
    law_pts = round((law_pct / 100.0) * 100, 1)
    com_pts = round((com_pct / 100.0) * 100, 1)
    projected_total = round(law_pts + com_pts, 1)
    
    progress_val = min(max(projected_total / 200.0, 0.0), 1.0)
    
    if projected_total >= 160:
        status_text = "🌟 ระดับบรรจุตัวจริง ลุ้นติดกลุ่ม Top 10 (พร้อมสอบ 100% รักษามาตรฐานนี้ไว้)"
        status_bg = "#ecfdf5"
        status_color = "#047857"
        status_border = "#10b981"
    elif projected_total >= 140:
        status_text = "🎯 ระดับสอบผ่านเกณฑ์มาตรฐานสูง (มีโอกาสสูงมากในการเรียกบรรจุ เพิ่มอีกนิดถึง Top 10)"
        status_bg = "#eff6ff"
        status_color = "#1d4ed8"
        status_border = "#3b82f6"
    elif projected_total >= 120:
        status_text = "⚠️ ผ่านเกณฑ์ขั้นต่ำ 60% (120/200) แต่ต้องเร่งเก็บคะแนนเพิ่มเพื่อลุ้นบรรจุรอบแรก (เป้า 160+)"
        status_bg = "#fffbeb"
        status_color = "#b45309"
        status_border = "#f59e0b"
    else:
        status_text = "🚨 ยังไม่ผ่านเกณฑ์ขั้นต่ำ 60% (ต้องทำคะแนนให้ได้อย่างน้อย 120 คะแนนขึ้นไป)"
        status_bg = "#fef2f2"
        status_color = "#b91c1c"
        status_border = "#ef4444"
        
    st.markdown(f'''
    <div style="background: white; border-radius: 14px; border: 2px solid {status_border}; padding: 20px 24px; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px;">
            <div>
                <span style="font-size: 1.15rem; font-weight: 800; color: #0f172a;">🎯 เป้าหมายคะแนนสอบบรรจุ: นักวิชาการคอมพิวเตอร์ปฏิบัติการ อสส.</span><br>
                <span style="font-size: 0.88rem; color: #64748b;">เกณฑ์ผ่าน 120/200 คะแนน (60%) | <b>เป้าหมายสู่ Top 10 บรรจุรอบแรก: 160/200 คะแนน (80%)</b></span>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 1.8rem; font-weight: 900; color: {status_color};">{projected_total}</span>
                <span style="font-size: 1.1rem; color: #64748b; font-weight: 700;"> / 200 คะแนน</span>
            </div>
        </div>
        
        <div style="margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: #64748b; margin-bottom: 4px; font-weight: 600;">
                <span>0 คะแนน</span>
                <span style="color: #b45309;">เกณฑ์ผ่าน (120 คะแนน)</span>
                <span style="color: #047857;">เป้าหมาย Top 10 (160 คะแนน)</span>
                <span>200 คะแนน</span>
            </div>
            <div style="background: #e2e8f0; border-radius: 999px; height: 14px; overflow: hidden; position: relative;">
                <div style="background: linear-gradient(90deg, #3b82f6 0%, #10b981 80%, #059669 100%); width: {progress_val*100}%; height: 100%; border-radius: 999px; transition: width 0.5s ease;"></div>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
            <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 10px 14px; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.9rem; color: #334155; font-weight: 600;">⚖️ หมวดกฎหมาย & ระเบียบฯ อสส.</span>
                <span style="font-size: 1rem; font-weight: 800; color: #1e40af;">{law_pts} / 100 ({law_pct}%)</span>
            </div>
            <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 10px 14px; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.9rem; color: #334155; font-weight: 600;">💻 หมวดคอมพิวเตอร์ & เทคโนโลยี</span>
                <span style="font-size: 1rem; font-weight: 800; color: #0284c7;">{com_pts} / 100 ({com_pct}%)</span>
            </div>
        </div>
        
        <div style="background: {status_bg}; border: 1px solid {status_border}; border-radius: 10px; padding: 10px 16px; font-size: 0.92rem; font-weight: 700; color: {status_color}; display: flex; align-items: center;">
            {status_text}
        </div>
    </div>
    ''', unsafe_allow_html=True)

def render_subject_dashboard(subj_key, subj_name, primary_color):
    cur_user = st.session_state.get('current_user', 'เฟิส')
    stats = db.get_dashboard_stats(subject=subj_key, username=cur_user)
    
    st.markdown(f"<h4 style='color: {primary_color}; margin-top: 6px;'>📌 ข้อมูลสถิติ: {subj_name}</h4>", unsafe_allow_html=True)
    
    # 4 Key Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-label">ทำข้อสอบไปแล้ว</div>
            <div class="stat-value" style="color: {primary_color};">{stats['practiced_count']} <span style="font-size: 1rem; color: #94a3b8;">/ {stats['total_bank_questions']} ข้อ</span></div>
        </div>
        ''', unsafe_allow_html=True)
    with m2:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-label">จำลองสอบวิชานี้</div>
            <div class="stat-value" style="color: #059669;">{stats['total_exams']} <span style="font-size: 1rem; color: #94a3b8;">ครั้ง</span></div>
        </div>
        ''', unsafe_allow_html=True)
    with m3:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-label">คะแนนเฉลี่ยวิชานี้</div>
            <div class="stat-value" style="color: #d97706;">{stats['avg_score']}%</div>
        </div>
        ''', unsafe_allow_html=True)
    with m4:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-label">ข้อผิดที่ต้องทบทวน</div>
            <div class="stat-value" style="color: #dc2626;">{stats['mistake_count']} <span style="font-size: 1rem; color: #94a3b8;">ข้อ</span></div>
        </div>
        ''', unsafe_allow_html=True)
        
    st.write("")
    
    col_left, col_right = st.columns([1.5, 1.5])
    
    # Category Breakdown
    with col_left:
        st.subheader("🎯 ความแม่นยำรายหมวดหมู่")
        cat_stats = stats['category_stats']
        
        if not cat_stats:
            st.info("ยังไม่มีข้อมูลสถิติรายหมวดหมู่สำหรับวิชานี้")
        else:
            for cat in cat_stats:
                acc = cat['accuracy']
                color = "green" if acc >= 70 else ("orange" if acc >= 50 else "red")
                
                st.markdown(f'''
                <div style="margin-bottom: 12px; background: white; padding: 12px 16px; border-radius: 10px; border: 1px solid #e2e8f0;">
                    <div style="display: flex; justify-content: space-between; font-weight: 600; font-size: 0.95rem; margin-bottom: 4px;">
                        <span>{cat['category']}</span>
                        <span style="color: {color};">{acc}% ({cat['practiced_in_cat']}/{cat['total_in_cat']} ข้อ)</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                st.progress(acc / 100.0)

    # Top Missed Questions
    with col_right:
        st.subheader("⚠️ 10 ข้อสอบที่ตอบผิดบ่อยที่สุด")
        top_wrongs = stats['top_mistakes']
        
        if not top_wrongs:
            st.success("ยังไม่มีข้อสอบที่ตอบผิดในวิชานี้ หรือคุณตอบถูกหมดทุกข้อ!")
        else:
            for i, item in enumerate(top_wrongs):
                st.markdown(f'''
                <div style="margin-bottom: 10px; background: #fff1f2; padding: 10px 14px; border-radius: 10px; border-left: 4px solid #f43f5e;">
                    <div style="font-size: 0.82rem; color: #9f1239; font-weight: 700;">
                        อันดับ {i+1} | ผิด {item['times_wrong']} ครั้ง (อ้างอิง: {item.get('law_ref', '-')})
                    </div>
                    <div style="font-size: 0.9rem; color: #1e293b; margin-top: 2px;">
                        {item['question'][:80]}...
                    </div>
                </div>
                ''', unsafe_allow_html=True)

    st.write("---")
    
    # Exam History
    st.subheader(f"📜 ประวัติการจำลองสอบย้อนหลัง ({subj_name})")
    history = db.get_exam_history(limit=10, subject=subj_key, username=cur_user)
    
    if not history:
        st.info("ยังไม่มีประวัติการจำลองสอบในวิชานี้")
    else:
        for sess in history:
            passed = sess['percentage'] >= 60.0
            badge = "✅ ผ่านเกณฑ์" if passed else "❌ ไม่ผ่านเกณฑ์"
            badge_color = "#059669" if passed else "#dc2626"
            mins = sess['time_spent_seconds'] // 60
            secs = sess['time_spent_seconds'] % 60
            
            st.markdown(f'''
            <div style="background: white; border-radius: 12px; padding: 14px 20px; margin-bottom: 10px; border: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-weight: 700; font-size: 1rem;">โหมด: {sess['mode']} ({sess['category']})</span><br>
                    <span style="font-size: 0.85rem; color: #64748b;">วันที่: {sess['created_at']} | เวลาที่ใช้: {mins:02d}:{secs:02d} นาที</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 1.2rem; font-weight: 800; color: {primary_color};">{sess['score']}/{sess['total_questions']} ({sess['percentage']}%)</span><br>
                    <span style="font-size: 0.8rem; font-weight: 700; color: {badge_color};">{badge}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)

def render_full_exam_dashboard():
    cur_user = st.session_state.get('current_user', 'เฟิส')
    if not hasattr(db, 'get_full_simulation_stats'):
        import importlib
        importlib.reload(db)
    if hasattr(db, 'get_full_simulation_stats'):
        stats = db.get_full_simulation_stats(username=cur_user)
    else:
        stats = {
            'total_bank_questions': 0, 'total_exams': 0, 'avg_score': 0.0,
            'max_points': 0, 'avg_points': 0.0, 'passed_count': 0, 'top10_count': 0,
            'latest_session': None, 'recent_sessions': [], 'mistake_count': 0,
            'mastered_count': 0, 'practiced_count': 0, 'overall_accuracy': 0.0
        }
    
    st.markdown(f"<h4 style='color: #d97706; margin-top: 6px;'>🏆 สถิติผลการสอบจริงเต็มรูปแบบ ({cur_user}) (200 คะแนน 180 นาที)</h4>", unsafe_allow_html=True)
    
    total_exams = stats.get('total_exams', 0)
    
    # 4 Key Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-label">จำลองสอบเต็มรูปแบบ</div>
            <div class="stat-value" style="color: #1e40af;">{total_exams} <span style="font-size: 1rem; color: #94a3b8;">ครั้ง</span></div>
            <div style="font-size: 0.78rem; color: #64748b; margin-top: 2px;">ชุดละ 100 ข้อ / 180 นาที</div>
        </div>
        ''', unsafe_allow_html=True)
    with m2:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-label">คะแนนสูงสุดที่ทำได้</div>
            <div class="stat-value" style="color: #059669;">{stats.get('max_points', 0)} <span style="font-size: 1rem; color: #94a3b8;">/ 200</span></div>
            <div style="font-size: 0.78rem; color: #059669; margin-top: 2px;">{round(stats.get('max_points', 0)/2, 1)}% ของคะแนนเต็ม</div>
        </div>
        ''', unsafe_allow_html=True)
    with m3:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-label">คะแนนเฉลี่ยรวม</div>
            <div class="stat-value" style="color: #d97706;">{stats.get('avg_points', 0.0)} <span style="font-size: 1rem; color: #94a3b8;">/ 200</span></div>
            <div style="font-size: 0.78rem; color: #d97706; margin-top: 2px;">เฉลี่ย {stats.get('avg_score', 0.0)}%</div>
        </div>
        ''', unsafe_allow_html=True)
    with m4:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-label">ผ่านเกณฑ์ / ลุ้น Top 10</div>
            <div class="stat-value" style="color: #b45309;">{stats.get('passed_count', 0)} <span style="font-size: 0.85rem; color: #64748b;">ผ่าน</span> | {stats.get('top10_count', 0)} <span style="font-size: 0.85rem; color: #b45309;">Top10</span></div>
            <div style="font-size: 0.78rem; color: #64748b; margin-top: 2px;">เกณฑ์ 120 คะแนน / 170+ คะแนน</div>
        </div>
        ''', unsafe_allow_html=True)
        
    st.write("")
    
    # Recent Exam Sessions Table
    st.subheader("📜 ประวัติการจำลองสอบจริงเต็มรูปแบบย้อนหลัง")
    history = stats.get('recent_sessions', [])
    
    if not history:
        st.info("ยังไม่มีประวัติการจำลองสอบจริงเต็มรูปแบบ (200 คะแนน) กดไปที่เมนู '🏆 สอบจริงเต็มรูปแบบ' เพื่อเริ่มสอบรอบแรก")
    else:
        for sess in history:
            score_pts = sess['score'] * 2
            passed = score_pts >= 120
            is_top10 = score_pts >= 170
            
            if is_top10:
                badge = "🌟 ระดับติดกลุ่ม Top 10 (85%+)"
                badge_color = "#d97706"
                card_border = "2px solid #d4af37"
            elif passed:
                badge = "✅ ผ่านเกณฑ์มาตรฐาน (60%+)"
                badge_color = "#059669"
                card_border = "1.5px solid #10b981"
            else:
                badge = "❌ ยังไม่ผ่านเกณฑ์ (<60%)"
                badge_color = "#dc2626"
                card_border = "1px solid #e2e8f0"
                
            mins = sess['time_spent_seconds'] // 60
            secs = sess['time_spent_seconds'] % 60
            time_str = f"{mins:02d}:{secs:02d} นาที" if mins < 60 else f"{mins//60} ชม. {mins%60:02d} นาที"
            
            st.markdown(f'''
            <div style="background: white; border-radius: 12px; padding: 16px 20px; margin-bottom: 12px; border: {card_border}; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                <div>
                    <span style="font-weight: 700; font-size: 1.05rem; color: #1e3a8a;">รอบที่ #{sess['id']} | สอบจริงเต็มรูปแบบ 100 ข้อ (200 คะแนน)</span><br>
                    <span style="font-size: 0.85rem; color: #64748b;">📅 วันที่: {sess['created_at']} | ⏱️ เวลาที่ใช้: {time_str}</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 1.35rem; font-weight: 800; color: #0f172a;">{score_pts} / 200 คะแนน</span>
                    <span style="font-size: 0.95rem; color: #64748b;"> ({sess['percentage']}%)</span><br>
                    <span style="font-size: 0.82rem; font-weight: 700; color: {badge_color};">{badge}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)

    st.write("---")

def render_comparison_dashboard():
    cur_user = st.session_state.get('current_user', 'เฟิส')
    law_stats = db.get_dashboard_stats(subject='law', username=cur_user)
    com_stats = db.get_dashboard_stats(subject='computer', username=cur_user)
    
    st.markdown(f"<h4>⚖️ vs 💻 เปรียบเทียบสถิติระหว่าง 2 วิชา ({cur_user})</h4>", unsafe_allow_html=True)
    
    c_law, c_com = st.columns(2)
    
    with c_law:
        st.markdown('''
        <div style="background: #eff6ff; border: 2px solid #3b82f6; border-radius: 14px; padding: 18px; margin-bottom: 16px;">
            <h4 style="color: #1e3a8a; margin: 0 0 12px 0;">⚖️ วิชากฎหมาย & ระเบียบฯ อสส.</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div class="stat-card" style="background: white !important;">
                    <div class="stat-label">คลังข้อสอบ</div>
                    <div class="stat-value" style="font-size: 1.4rem; color: #1e3a8a;">{} ข้อ</div>
                </div>
                <div class="stat-card" style="background: white !important;">
                    <div class="stat-label">สอบไปแล้ว</div>
                    <div class="stat-value" style="font-size: 1.4rem; color: #047857;">{} ครั้ง</div>
                </div>
                <div class="stat-card" style="background: white !important;">
                    <div class="stat-label">คะแนนเฉลี่ย</div>
                    <div class="stat-value" style="font-size: 1.4rem; color: #d97706;">{}%</div>
                </div>
                <div class="stat-card" style="background: white !important;">
                    <div class="stat-label">ข้อผิดค้างทบทวน</div>
                    <div class="stat-value" style="font-size: 1.4rem; color: #dc2626;">{} ข้อ</div>
                </div>
            </div>
        </div>
        '''.format(law_stats['total_bank_questions'], law_stats['total_exams'], law_stats['avg_score'], law_stats['mistake_count']), unsafe_allow_html=True)
        
    with c_com:
        st.markdown('''
        <div style="background: #f0fdf4; border: 2px solid #10b981; border-radius: 14px; padding: 18px; margin-bottom: 16px;">
            <h4 style="color: #065f46; margin: 0 0 12px 0;">💻 วิชาคอมพิวเตอร์และสารสนเทศ</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div class="stat-card" style="background: white !important;">
                    <div class="stat-label">คลังข้อสอบ</div>
                    <div class="stat-value" style="font-size: 1.4rem; color: #0284c7;">{} ข้อ</div>
                </div>
                <div class="stat-card" style="background: white !important;">
                    <div class="stat-label">สอบไปแล้ว</div>
                    <div class="stat-value" style="font-size: 1.4rem; color: #047857;">{} ครั้ง</div>
                </div>
                <div class="stat-card" style="background: white !important;">
                    <div class="stat-label">คะแนนเฉลี่ย</div>
                    <div class="stat-value" style="font-size: 1.4rem; color: #d97706;">{}%</div>
                </div>
                <div class="stat-card" style="background: white !important;">
                    <div class="stat-label">ข้อผิดค้างทบทวน</div>
                    <div class="stat-value" style="font-size: 1.4rem; color: #dc2626;">{} ข้อ</div>
                </div>
            </div>
        </div>
        '''.format(com_stats['total_bank_questions'], com_stats['total_exams'], com_stats['avg_score'], com_stats['mistake_count']), unsafe_allow_html=True)

def render_backup_restore_section():
    cur_user = st.session_state.get('current_user', 'เฟิส')
    
    st.markdown('''
    <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 14px; padding: 20px 24px; margin-top: 24px; margin-bottom: 24px;">
        <h4 style="margin: 0 0 8px 0; color: #0f172a;">💾 สำรองและกู้คืนข้อมูล (Backup & Restore Data)</h4>
        <p style="margin: 0 0 16px 0; color: #64748b; font-size: 0.88rem;">
            สำหรับผู้ใช้งานบน Streamlit Cloud ข้อมูลใน SQLite จะถูกรีเซ็ตหาก Server Sleep หรือถูก Reboot แนะนำให้ดาวน์โหลดไฟล์สำรองข้อมูล JSON เก็บไว้ในเครื่อง และสามารถกด Import กลับมาได้ทุกเมื่อ
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    col_export, col_import = st.columns(2)
    
    with col_export:
        st.markdown("<h5 style='color: #1e3a8a; margin-bottom: 8px;'>📥 ส่งออกข้อมูล (Export Backup)</h5>", unsafe_allow_html=True)
        backup_data = db.export_user_data(username=cur_user)
        json_str = json.dumps(backup_data, ensure_ascii=False, indent=2)
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        st.download_button(
            label=f"💾 ดาวน์โหลดไฟล์สำรอง JSON ({cur_user})",
            data=json_str,
            file_name=f"oag_exam_backup_{cur_user}_{now_str}.json",
            mime="application/json",
            use_container_width=True,
            type="primary"
        )
        st.caption(f"📦 รวม: ประวัติสอบ {backup_data['summary']['total_sessions']} ครั้ง | สถิติสะสม {backup_data['summary']['total_stats_records']} ข้อ | บุ๊กมาร์ก {backup_data['summary']['total_bookmarks']} ข้อ")
        
    with col_import:
        st.markdown("<h5 style='color: #047857; margin-bottom: 8px;'>📤 นำเข้าข้อมูล (Import Backup)</h5>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("เลือกไฟล์ JSON ที่เคยสำรองไว้:", type=["json"], key="backup_file_uploader")
        
        if uploaded_file is not None:
            if st.button("🚀 ยืนยันการกู้คืนข้อมูล (Restore Now)", type="secondary", use_container_width=True):
                try:
                    import_content = json.load(uploaded_file)
                    success, msg = db.import_user_data(import_content, username=cur_user)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {str(e)}")
                    
    with st.expander("🚨 ล้างข้อมูลสถิติ (Danger Zone)"):
        st.warning(f"⚠️ การล้างสถิติจะลบประวัติการสอบ ข้อผิดใน Mistake Bank และบุ๊กมาร์กทั้งหมดของผู้ใช้ '{cur_user}'")
        if st.button(f"🚨 ล้างสถิติและประวัติทั้งหมดของ '{cur_user}' (Reset)", type="secondary", use_container_width=True):
            db.reset_all_statistics(username=cur_user)
            st.success("ล้างสถิติและประวัติเรียบร้อยแล้ว")
            st.rerun()
