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

def get_remaining_seconds(st_session_state):
    if not st_session_state.exam_active or st_session_state.exam_submitted:
        return 0
    elapsed = int(time.time() - st_session_state.start_time)
    remaining = max(0, st_session_state.duration_seconds - elapsed)
    return remaining

def format_time_mmss(seconds):
    mins = max(0, seconds) // 60
    secs = max(0, seconds) % 60
    return f"{mins:02d}:{secs:02d}"

def calculate_and_save_exam_results(st_session_state):
    questions = st_session_state.exam_questions
    user_answers = st_session_state.user_answers
    
    total_q = len(questions)
    correct_count = 0
    wrong_count = 0
    unanswered_count = 0
    
    details = {}
    category_breakdown = {}
    
    for idx, q in enumerate(questions):
        qid = q['id']
        cat = q.get('category', 'ทั่วไป')
        correct_ans = q['answer_index']
        user_ans = user_answers.get(idx, None)
        
        if cat not in category_breakdown:
            category_breakdown[cat] = {'total': 0, 'correct': 0, 'wrong': 0}
        category_breakdown[cat]['total'] += 1
        
        is_correct = (user_ans == correct_ans) if user_ans is not None else False
        
        if user_ans is None:
            unanswered_count += 1
            status = 'unanswered'
        elif is_correct:
            correct_count += 1
            category_breakdown[cat]['correct'] += 1
            status = 'correct'
        else:
            wrong_count += 1
            category_breakdown[cat]['wrong'] += 1
            status = 'wrong'
            
        details[qid] = {
            'q_idx': idx,
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
    score_percentage = (correct_count / total_q * 100.0) if total_q > 0 else 0.0
    passed = score_percentage >= 60.0
    
    result = {
        'total_questions': total_q,
        'score': correct_count,
        'wrong_count': wrong_count,
        'unanswered_count': unanswered_count,
        'percentage': round(score_percentage, 1),
        'passed': passed,
        'time_spent_seconds': time_spent,
        'time_spent_str': format_time_mmss(time_spent),
        'category_breakdown': category_breakdown,
        'details': details
    }
    
    # Save into SQLite database with subject
    subj = st_session_state.get('selected_subject', 'law')
    session_id = db.save_exam_session(
        mode=st_session_state.exam_mode,
        category='รวมข้อสอบ' if st_session_state.exam_mode == 'simulation' else 'ทบทวนข้อผิด',
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
    
    return result
