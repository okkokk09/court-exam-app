# -*- coding: utf-8 -*-
import time
import random
import db

def init_session_state(st_session_state):
    '''Initialize core state variables in Streamlit session_state'''
    defaults = {
        'current_page': 'exam', # 'exam', 'review', 'practice', 'stats', 'manage'
        'exam_active': False,
        'exam_submitted': False,
        'exam_mode': 'simulation', # 'simulation', 'review_test', 'practice'
        'exam_questions': [],
        'user_answers': {}, # {q_idx: selected_choice_idx (0..3)}
        'bookmarked_indices': set(),
        'current_q_idx': 0,
        'start_time': 0,
        'duration_seconds': 3600, # 60 minutes default
        'time_spent': 0,
        'exam_result': None,
        # Practice & Review specific states
        'practice_category': 'ทั้งหมด',
        'practice_q_idx': 0,
        'practice_selected': None,
        'practice_show_answer': False,
        'review_filter': 'frequent_mistakes',
        'review_q_idx': 0,
        'review_selected': None,
        'review_show_answer': False,
        'selected_theme': 'court_navy',
        'selected_subject': 'law', # 'law' or 'computer'
        'shuffle_options': True, # Shuffle choices to prevent position memorization
        'mistakes': [], # List of questions missed in the latest exam session (Mistake Bank)
    }
    
    for key, val in defaults.items():
        if key not in st_session_state:
            st_session_state[key] = val

def shuffle_question_options(question_dict):
    '''
    Randomizes / shuffles the 4 options of a question dictionary while accurately 
    updating the answer_index to point to the new shuffled position of the correct answer.
    '''
    if not question_dict or 'options' not in question_dict or not question_dict['options']:
        return question_dict
        
    q = dict(question_dict)
    options = list(q['options'])
    correct_idx = q.get('answer_index', 0)
    
    if correct_idx >= len(options):
        correct_idx = 0
        
    correct_text = options[correct_idx]
    
    # Shuffle options randomly
    random.shuffle(options)
    
    # Update answer_index to point to new position
    q['options'] = options
    q['answer_index'] = options.index(correct_text)
    return q

def shuffle_questions_list(questions_list):
    '''Shuffles options for every question in a list of questions'''
    return [shuffle_question_options(q) for q in questions_list]

def start_full_simulation_exam(st_session_state, duration_minutes=180):
    '''
    Starts Full Exam Simulation: Exactly 100 questions (30 Law + 70 Computer),
    Strictly ordered: Law questions first (Q1-Q30) followed by Computer questions (Q31-Q100).
    180 minutes (3 hours) timer, 200 points scale.
    '''
    law_qs = db.get_random_questions(count=30, subject='law')
    com_qs = db.get_random_questions(count=70, subject='computer')
    
    # Shuffle choices within questions if option is enabled
    if st_session_state.get('shuffle_options', True):
        law_qs = shuffle_questions_list(law_qs)
        com_qs = shuffle_questions_list(com_qs)
        
    # Combine strictly: Law first (index 0..29 / ข้อ 1-30), Computer second (index 30..99 / ข้อ 31-100)
    questions = law_qs + com_qs
        
    st_session_state.exam_active = True
    st_session_state.exam_submitted = False
    st_session_state.exam_mode = 'full_simulation'
    st_session_state.exam_questions = questions
    st_session_state.user_answers = {}
    st_session_state.bookmarked_indices = set()
    st_session_state.current_q_idx = 0
    st_session_state.start_time = time.time()
    st_session_state.duration_seconds = duration_minutes * 60 # 180 mins = 10,800 secs
    st_session_state.time_spent = 0
    st_session_state.exam_result = None
    st_session_state.confirm_submit = False
    st_session_state.confirm_abandon = False

def start_simulation_exam(st_session_state, count=50, duration_minutes=60, category=None, subject=None):
    if not subject:
        subject = st_session_state.get('selected_subject', 'law')
    questions = db.get_random_questions(count=count, category=category, subject=subject)
    if len(questions) < count:
        # If category has fewer, take all available
        pass
        
    # Shuffle choices if option is enabled
    if st_session_state.get('shuffle_options', True):
        questions = shuffle_questions_list(questions)
        
    st_session_state.exam_active = True
    st_session_state.exam_submitted = False
    st_session_state.exam_mode = 'simulation'
    st_session_state.exam_questions = questions
    st_session_state.user_answers = {}
    st_session_state.bookmarked_indices = set()
    st_session_state.current_q_idx = 0
    st_session_state.start_time = time.time()
    st_session_state.duration_seconds = duration_minutes * 60
    st_session_state.time_spent = 0
    st_session_state.exam_result = None

def start_review_exam(st_session_state, limit=50, filter_type='frequent_mistakes', subject=None):
    if not subject:
        subject = st_session_state.get('selected_subject', 'law')
    questions = db.get_mistake_questions(limit=limit, filter_type=filter_type, subject=subject)
    if not questions:
        return False
        
    # Shuffle choices if option is enabled
    if st_session_state.get('shuffle_options', True):
        questions = shuffle_questions_list(questions)
        
    st_session_state.exam_active = True
    st_session_state.exam_submitted = False
    st_session_state.exam_mode = 'review_test'
    st_session_state.exam_questions = questions
    st_session_state.user_answers = {}
    st_session_state.bookmarked_indices = set()
    st_session_state.current_q_idx = 0
    st_session_state.start_time = time.time()
    st_session_state.duration_seconds = len(questions) * 72 # ~1.2 mins per question
    st_session_state.time_spent = 0
    st_session_state.exam_result = None
    return True

def start_mistakes_retest(st_session_state):
    '''Starts a retest session containing only the questions missed in the latest exam round'''
    mistakes = st_session_state.get('mistakes', [])
    if not mistakes:
        return False
        
    questions = list(mistakes)
    if st_session_state.get('shuffle_options', True):
        questions = shuffle_questions_list(questions)
        
    st_session_state.exam_active = True
    st_session_state.exam_submitted = False
    st_session_state.exam_mode = 'mistakes_retest'
    st_session_state.exam_questions = questions
    st_session_state.user_answers = {}
    st_session_state.bookmarked_indices = set()
    st_session_state.current_q_idx = 0
    st_session_state.start_time = time.time()
    st_session_state.duration_seconds = max(300, len(questions) * 90) # ~1.5 mins per question, min 5 mins
    st_session_state.time_spent = 0
    st_session_state.exam_result = None
    return True

def abandon_exam(st_session_state):
    '''Cancels the current active exam immediately without recording any stats or saving results'''
    st_session_state.exam_active = False
    st_session_state.exam_submitted = False
    st_session_state.exam_questions = []
    st_session_state.user_answers = {}
    st_session_state.bookmarked_indices = set()
    st_session_state.current_q_idx = 0
    st_session_state.start_time = 0
    st_session_state.time_spent = 0
    st_session_state.exam_result = None
    st_session_state.confirm_submit = False
    st_session_state.confirm_abandon = False

def get_remaining_seconds(st_session_state):
    if not st_session_state.exam_active or st_session_state.exam_submitted:
        return 0
    elapsed = int(time.time() - st_session_state.start_time)
    remaining = max(0, st_session_state.duration_seconds - elapsed)
    return remaining

def format_time_hhmmss(seconds):
    seconds = max(0, int(seconds))
    hours = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"

format_time_mmss = format_time_hhmmss

def calculate_and_save_exam_results(st_session_state):
    questions = st_session_state.exam_questions
    user_answers = st_session_state.user_answers
    exam_mode = st_session_state.get('exam_mode', 'simulation')
    is_full_sim = (exam_mode == 'full_simulation')
    
    total_q = len(questions)
    correct_count = 0
    wrong_count = 0
    unanswered_count = 0
    
    details = {}
    category_breakdown = {}
    mistake_questions = []
    
    # Subject breakdown
    subject_stats = {
        'law': {'total': 0, 'correct': 0, 'wrong': 0, 'unanswered': 0, 'points': 0, 'max_points': 0},
        'computer': {'total': 0, 'correct': 0, 'wrong': 0, 'unanswered': 0, 'points': 0, 'max_points': 0}
    }
    
    points_per_q = 2 if is_full_sim else 1
    
    for idx, q in enumerate(questions):
        qid = q['id']
        subj = q.get('subject', 'law')
        if subj not in subject_stats:
            subject_stats[subj] = {'total': 0, 'correct': 0, 'wrong': 0, 'unanswered': 0, 'points': 0, 'max_points': 0}
            
        cat = q.get('category', 'ทั่วไป')
        correct_ans = q['answer_index']
        user_ans = user_answers.get(idx, None)
        
        if cat not in category_breakdown:
            category_breakdown[cat] = {'total': 0, 'correct': 0, 'wrong': 0}
        category_breakdown[cat]['total'] += 1
        subject_stats[subj]['total'] += 1
        subject_stats[subj]['max_points'] += points_per_q
        
        is_correct = (user_ans == correct_ans) if user_ans is not None else False
        
        # Record into SQLite question_stats
        db.record_answer(qid, user_ans, is_correct)
        
        if user_ans is None:
            unanswered_count += 1
            subject_stats[subj]['unanswered'] += 1
            status = 'unanswered'
            mistake_questions.append(q)
        elif is_correct:
            correct_count += 1
            category_breakdown[cat]['correct'] += 1
            subject_stats[subj]['correct'] += 1
            subject_stats[subj]['points'] += points_per_q
            status = 'correct'
        else:
            wrong_count += 1
            category_breakdown[cat]['wrong'] += 1
            subject_stats[subj]['wrong'] += 1
            status = 'wrong'
            mistake_questions.append(q)
            
        details[qid] = {
            'q_idx': idx,
            'subject': subj,
            'question_text': q['question'],
            'options': q['options'],
            'correct_index': correct_ans,
            'selected': user_ans,
            'is_correct': is_correct,
            'status': status,
            'category': cat,
            'explanation': q.get('explanation', ''),
            'law_ref': q.get('law_ref', '')
        }
        
    time_spent = int(time.time() - st_session_state.start_time)
    
    total_points = total_q * points_per_q
    earned_points = correct_count * points_per_q
    score_percentage = (correct_count / total_q * 100.0) if total_q > 0 else 0.0
    passed = score_percentage >= 60.0 # Standard pass mark 60%
    
    # Tier validation
    if is_full_sim:
        if earned_points >= 170:
            tier = 'top10'
            tier_title = '🌟 ระดับหัวแถว ลุ้นติด Top 10 ศาลยุติธรรม!'
            tier_badge = 'TOP 10 TIER (85%+)'
            tier_color = '#d97706'
            tier_desc = 'คะแนนของคุณอยู่ในเกณฑ์ยอดเยี่ยมระดับกลุ่มผู้มีคะแนนสูงสุด มีโอกาสสอบติดลำดับต้นๆ สูงมาก!'
        elif earned_points >= 120:
            tier = 'passed'
            tier_title = '✅ สอบผ่านเกณฑ์มาตรฐานศาลยุติธรรม (60%+)'
            tier_badge = 'PASSED (60%+)'
            tier_color = '#059669'
            tier_desc = 'ยินดีด้วย! คะแนนของคุณผ่านเกณฑ์มาตรฐานการสอบของสำนักงานศาลยุติธรรม'
        else:
            tier = 'failed'
            tier_title = '❌ ยังไม่ผ่านเกณฑ์มาตรฐาน (ต่ำกว่า 120 คะแนน)'
            tier_badge = 'FAILED (<60%)'
            tier_color = '#dc2626'
            tier_desc = 'ยังไม่ผ่านเกณฑ์มาตรฐาน 60% แนะนำให้ฝึกทำซ้ำข้อที่ผิดใน Mistake Bank เพื่อปิดจุดอ่อน'
    else:
        if score_percentage >= 85.0:
            tier = 'top10'
            tier_title = '🌟 ยอดเยี่ยมมาก (85%+)'
            tier_badge = 'EXCELLENT'
            tier_color = '#d97706'
            tier_desc = 'คะแนนอยู่ในเกณฑ์ดีเยี่ยม!'
        elif passed:
            tier = 'passed'
            tier_title = '✅ สอบผ่านเกณฑ์ (60%+)'
            tier_badge = 'PASSED'
            tier_color = '#059669'
            tier_desc = 'ผ่านเกณฑ์มาตรฐานการสอบ'
        else:
            tier = 'failed'
            tier_title = '💪 ยังไม่ผ่านเกณฑ์ 60%'
            tier_badge = 'NEEDS IMPROVEMENT'
            tier_color = '#dc2626'
            tier_desc = 'พยายามใหม่อีกครั้ง ฝึกซ้ำข้อที่ผิดเพื่อพัฒนาคะแนน'
            
    result = {
        'exam_mode': exam_mode,
        'is_full_simulation': is_full_sim,
        'total_questions': total_q,
        'points_per_question': points_per_q,
        'total_points': total_points,
        'earned_points': earned_points,
        'score': correct_count,
        'wrong_count': wrong_count,
        'unanswered_count': unanswered_count,
        'percentage': round(score_percentage, 1),
        'passed': passed,
        'tier': tier,
        'tier_title': tier_title,
        'tier_badge': tier_badge,
        'tier_color': tier_color,
        'tier_desc': tier_desc,
        'time_spent_seconds': time_spent,
        'time_spent_str': format_time_hhmmss(time_spent),
        'subject_stats': subject_stats,
        'category_breakdown': category_breakdown,
        'details': details
    }
    
    # Save into SQLite database with subject
    subj = 'combined' if is_full_sim else st_session_state.get('selected_subject', 'law')
    mode_label = 'สอบจริงเต็มรูปแบบ 200 คะแนน' if is_full_sim else ('รวมข้อสอบ' if exam_mode == 'simulation' else ('วนทำซ้ำข้อผิด' if exam_mode == 'mistakes_retest' else 'ทบทวนข้อผิด'))
    
    session_id = db.save_exam_session(
        mode=exam_mode,
        category=mode_label,
        total_q=total_q,
        score=correct_count,
        time_spent_seconds=time_spent,
        answers_detail=details,
        subject=subj
    )
    
    result['session_id'] = session_id
    st_session_state.exam_result = result
    st_session_state.exam_submitted = True
    st_session_state.exam_active = False
    
    # Update Mistake Bank in session state
    st_session_state.mistakes = mistake_questions
    
    return result
