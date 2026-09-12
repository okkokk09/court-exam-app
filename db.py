# -*- coding: utf-8 -*-
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'exam_data.db')
QUESTIONS_JSON_PATH = os.path.join(os.path.dirname(__file__), 'data', 'questions.json')
COMPUTER_JSON_PATH = os.path.join(os.path.dirname(__file__), 'data', 'computer_questions.json')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Questions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id TEXT PRIMARY KEY,
        subject TEXT DEFAULT 'law',
        category TEXT,
        topic TEXT,
        question TEXT,
        options_json TEXT,
        answer_index INTEGER,
        explanation TEXT,
        law_ref TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Check if subject column exists, if not add it
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN subject TEXT DEFAULT 'law'")
        conn.commit()
    except Exception:
        pass
    
    # 2. Exam sessions history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exam_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        subject TEXT DEFAULT 'law',
        mode TEXT,
        category TEXT,
        total_questions INTEGER,
        score INTEGER,
        percentage REAL,
        time_spent_seconds INTEGER,
        answers_json TEXT
    )
    ''')
    
    try:
        cursor.execute("ALTER TABLE exam_sessions ADD COLUMN subject TEXT DEFAULT 'law'")
        conn.commit()
    except Exception:
        pass
    
    # 3. Question statistics
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS question_stats (
        question_id TEXT PRIMARY KEY,
        times_answered INTEGER DEFAULT 0,
        times_correct INTEGER DEFAULT 0,
        times_wrong INTEGER DEFAULT 0,
        wrong_options_json TEXT DEFAULT '{}',
        last_answered_at TIMESTAMP,
        last_result INTEGER,
        mastery_level INTEGER DEFAULT 0,
        FOREIGN KEY (question_id) REFERENCES questions (id)
    )
    ''')
    
    # 4. Bookmarks table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_bookmarks (
        question_id TEXT PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        note TEXT,
        FOREIGN KEY (question_id) REFERENCES questions (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    # Seed and sync questions from JSON
    seed_questions_if_empty()

def seed_questions_if_empty():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Sync Law Questions
    if os.path.exists(QUESTIONS_JSON_PATH):
        with open(QUESTIONS_JSON_PATH, 'r', encoding='utf-8') as f:
            items = json.load(f)
            
        for item in items:
            cursor.execute('''
            INSERT OR REPLACE INTO questions (id, subject, category, topic, question, options_json, answer_index, explanation, law_ref)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['id'],
                'law',
                item.get('category', 'ทั่วไป'),
                item.get('topic', ''),
                item['question'],
                json.dumps(item['options'], ensure_ascii=False),
                item['answer_index'],
                item.get('explanation', ''),
                item.get('law_ref', '')
            ))
        conn.commit()
        
    # Sync Computer Questions
    if os.path.exists(COMPUTER_JSON_PATH):
        with open(COMPUTER_JSON_PATH, 'r', encoding='utf-8') as f:
            items = json.load(f)
            
        for item in items:
            cursor.execute('''
            INSERT OR REPLACE INTO questions (id, subject, category, topic, question, options_json, answer_index, explanation, law_ref)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['id'],
                'computer',
                item.get('category', 'คอมพิวเตอร์ทั่วไป'),
                item.get('topic', ''),
                item['question'],
                json.dumps(item['options'], ensure_ascii=False),
                item['answer_index'],
                item.get('explanation', ''),
                item.get('law_ref', '')
            ))
        conn.commit()
        
    conn.close()

def get_all_questions(category=None, subject=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    conditions = []
    params = []
    
    if subject:
        conditions.append("(subject = ? OR (subject IS NULL AND ? = 'law'))")
        params.extend([subject, subject])
    if category and category != 'ทั้งหมด':
        conditions.append("category = ?")
        params.append(category)
        
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    cursor.execute(f'SELECT * FROM questions {where_clause} ORDER BY id', tuple(params))
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        result.append({
            'id': r['id'],
            'subject': r['subject'] or 'law',
            'category': r['category'],
            'topic': r['topic'],
            'question': r['question'],
            'options': json.loads(r['options_json']),
            'answer_index': r['answer_index'],
            'explanation': r['explanation'],
            'law_ref': r['law_ref']
        })
    return result

def get_random_questions(count=50, category=None, subject=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    conditions = []
    params = []
    
    if subject:
        conditions.append("(subject = ? OR (subject IS NULL AND ? = 'law'))")
        params.extend([subject, subject])
    if category and category != 'ทั้งหมด':
        conditions.append("category = ?")
        params.append(category)
        
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    params.append(count)
    
    cursor.execute(f'SELECT * FROM questions {where_clause} ORDER BY RANDOM() LIMIT ?', tuple(params))
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        result.append({
            'id': r['id'],
            'subject': r['subject'] or 'law',
            'category': r['category'],
            'topic': r['topic'],
            'question': r['question'],
            'options': json.loads(r['options_json']),
            'answer_index': r['answer_index'],
            'explanation': r['explanation'],
            'law_ref': r['law_ref']
        })
    return result

def get_mistake_questions(limit=50, filter_type='all_mistakes', subject=None):
    '''
    filter_type options:
    - 'all_mistakes': Any question with times_wrong > 0
    - 'frequent_mistakes': Questions sorted by highest times_wrong
    - 'recent_mistakes': Questions where last_result == 0
    - 'unmastered': Questions with times_wrong > times_correct
    '''
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''
    SELECT q.*, s.times_answered, s.times_correct, s.times_wrong, s.wrong_options_json, s.last_result, s.mastery_level
    FROM questions q
    JOIN question_stats s ON q.id = s.question_id
    WHERE s.times_wrong > 0
    '''
    params = []
    if subject:
        query += " AND (q.subject = ? OR (q.subject IS NULL AND ? = 'law'))"
        params.extend([subject, subject])
    
    if filter_type == 'frequent_mistakes':
        query += ' ORDER BY s.times_wrong DESC, s.times_answered DESC LIMIT ?'
    elif filter_type == 'recent_mistakes':
        query += ' AND s.last_result = 0 ORDER BY s.last_answered_at DESC LIMIT ?'
    elif filter_type == 'unmastered':
        query += ' AND (s.times_wrong >= s.times_correct OR s.mastery_level < 2) ORDER BY s.times_wrong DESC LIMIT ?'
    else:
        query += ' ORDER BY s.times_wrong DESC, q.id ASC LIMIT ?'
        
    params.append(limit)
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        result.append({
            'id': r['id'],
            'subject': r['subject'] or 'law',
            'category': r['category'],
            'topic': r['topic'],
            'question': r['question'],
            'options': json.loads(r['options_json']),
            'answer_index': r['answer_index'],
            'explanation': r['explanation'],
            'law_ref': r['law_ref'],
            'times_answered': r['times_answered'],
            'times_correct': r['times_correct'],
            'times_wrong': r['times_wrong'],
            'last_result': r['last_result'],
            'mastery_level': r['mastery_level']
        })
    return result

def get_all_categories(subject=None):
    conn = get_connection()
    cursor = conn.cursor()
    if subject:
        cursor.execute('''
        SELECT category, COUNT(*) as count 
        FROM questions 
        WHERE subject = ? OR (subject IS NULL AND ? = 'law')
        GROUP BY category 
        ORDER BY count DESC
        ''', (subject, subject))
    else:
        cursor.execute('SELECT category, COUNT(*) as count FROM questions GROUP BY category ORDER BY count DESC')
    rows = cursor.fetchall()
    conn.close()
    return [(r['category'], r['count']) for r in rows]

def record_answer(question_id, selected_index, is_correct):
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Get existing stats
    cursor.execute('SELECT * FROM question_stats WHERE question_id = ?', (question_id,))
    row = cursor.fetchone()
    
    if row:
        times_answered = row['times_answered'] + 1
        times_correct = row['times_correct'] + (1 if is_correct else 0)
        times_wrong = row['times_wrong'] + (0 if is_correct else 1)
        
        wrong_opts = json.loads(row['wrong_options_json'] or '{}')
        if not is_correct and selected_index is not None:
            k = str(selected_index)
            wrong_opts[k] = wrong_opts.get(k, 0) + 1
            
        # Update mastery level
        # 0: new, 1: practiced, 2: progressing, 3: mastered
        if times_correct >= 3 and times_wrong == 0:
            mastery = 3
        elif is_correct and times_correct > times_wrong:
            mastery = 2
        elif is_correct:
            mastery = 1
        else:
            mastery = 0
            
        cursor.execute('''
        UPDATE question_stats
        SET times_answered = ?, times_correct = ?, times_wrong = ?,
            wrong_options_json = ?, last_answered_at = ?, last_result = ?, mastery_level = ?
        WHERE question_id = ?
        ''', (times_answered, times_correct, times_wrong, json.dumps(wrong_opts), now, 1 if is_correct else 0, mastery, question_id))
    else:
        wrong_opts = {}
        if not is_correct and selected_index is not None:
            wrong_opts[str(selected_index)] = 1
        mastery = 1 if is_correct else 0
        
        cursor.execute('''
        INSERT INTO question_stats (question_id, times_answered, times_correct, times_wrong, wrong_options_json, last_answered_at, last_result, mastery_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (question_id, 1, 1 if is_correct else 0, 0 if is_correct else 1, json.dumps(wrong_opts), now, 1 if is_correct else 0, mastery))
        
    conn.commit()
    conn.close()

def save_exam_session(mode, category, total_q, score, time_spent_seconds, answers_detail, subject='law'):
    conn = get_connection()
    cursor = conn.cursor()
    
    percentage = (score / total_q * 100.0) if total_q > 0 else 0.0
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
    INSERT INTO exam_sessions (created_at, subject, mode, category, total_questions, score, percentage, time_spent_seconds, answers_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (now, subject, mode, category, total_q, score, round(percentage, 2), time_spent_seconds, json.dumps(answers_detail, ensure_ascii=False)))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Also record individual question stats
    for qid, detail in answers_detail.items():
        record_answer(qid, detail.get('selected'), detail.get('is_correct', False))
        
    return session_id

def get_exam_history(limit=20, subject=None):
    conn = get_connection()
    cursor = conn.cursor()
    if subject:
        cursor.execute('''
        SELECT * FROM exam_sessions 
        WHERE subject = ? OR (subject IS NULL AND ? = 'law')
        ORDER BY created_at DESC LIMIT ?
        ''', (subject, subject, limit))
    else:
        cursor.execute('SELECT * FROM exam_sessions ORDER BY created_at DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_dashboard_stats(subject=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Total questions in bank
    if subject:
        cursor.execute('SELECT COUNT(*) as count FROM questions WHERE subject = ? OR (subject IS NULL AND ? = "law")', (subject, subject))
    else:
        cursor.execute('SELECT COUNT(*) as count FROM questions')
    total_bank_questions = cursor.fetchone()['count']
    
    # 2. Total exams taken (strictly filtered by subject)
    if subject:
        cursor.execute('''
        SELECT COUNT(*) as count, AVG(percentage) as avg_score, MAX(score) as max_score 
        FROM exam_sessions 
        WHERE mode = "simulation" AND (subject = ? OR (subject IS NULL AND ? = "law"))
        ''', (subject, subject))
    else:
        cursor.execute('SELECT COUNT(*) as count, AVG(percentage) as avg_score, MAX(score) as max_score FROM exam_sessions WHERE mode = "simulation"')
    exam_stat = cursor.fetchone()
    total_exams = exam_stat['count'] or 0
    avg_score = round(exam_stat['avg_score'] or 0.0, 1)
    
    # 3. Questions practiced & Mistakes
    if subject:
        cursor.execute('''
        SELECT 
            COUNT(s.question_id) as practiced_count,
            SUM(CASE WHEN s.times_wrong > 0 THEN 1 ELSE 0 END) as mistake_count,
            SUM(CASE WHEN s.mastery_level >= 2 THEN 1 ELSE 0 END) as mastered_count,
            SUM(s.times_answered) as total_answers,
            SUM(s.times_correct) as total_correct
        FROM question_stats s
        JOIN questions q ON s.question_id = q.id
        WHERE q.subject = ? OR (q.subject IS NULL AND ? = 'law')
        ''', (subject, subject))
    else:
        cursor.execute('''
        SELECT 
            COUNT(*) as practiced_count,
            SUM(CASE WHEN times_wrong > 0 THEN 1 ELSE 0 END) as mistake_count,
            SUM(CASE WHEN mastery_level >= 2 THEN 1 ELSE 0 END) as mastered_count,
            SUM(times_answered) as total_answers,
            SUM(times_correct) as total_correct
        FROM question_stats
        ''')
    stat_row = cursor.fetchone()
    practiced_count = stat_row['practiced_count'] or 0
    mistake_count = stat_row['mistake_count'] or 0
    mastered_count = stat_row['mastered_count'] or 0
    total_answers = stat_row['total_answers'] or 0
    total_correct = stat_row['total_correct'] or 0
    overall_accuracy = round((total_correct / total_answers * 100.0), 1) if total_answers > 0 else 0.0
    
    # 4. Performance by category
    if subject:
        cursor.execute('''
        SELECT 
            q.category,
            COUNT(DISTINCT q.id) as total_in_cat,
            COUNT(s.question_id) as practiced_in_cat,
            COALESCE(SUM(s.times_answered), 0) as total_ans,
            COALESCE(SUM(s.times_correct), 0) as total_cor,
            COALESCE(SUM(s.times_wrong), 0) as total_wrg
        FROM questions q
        LEFT JOIN question_stats s ON q.id = s.question_id
        WHERE q.subject = ? OR (q.subject IS NULL AND ? = 'law')
        GROUP BY q.category
        ORDER BY total_in_cat DESC
        ''', (subject, subject))
    else:
        cursor.execute('''
        SELECT 
            q.category,
            COUNT(DISTINCT q.id) as total_in_cat,
            COUNT(s.question_id) as practiced_in_cat,
            COALESCE(SUM(s.times_answered), 0) as total_ans,
            COALESCE(SUM(s.times_correct), 0) as total_cor,
            COALESCE(SUM(s.times_wrong), 0) as total_wrg
        FROM questions q
        LEFT JOIN question_stats s ON q.id = s.question_id
        GROUP BY q.category
        ORDER BY total_in_cat DESC
        ''')
    category_stats = []
    for r in cursor.fetchall():
        total_ans = r['total_ans']
        total_cor = r['total_cor']
        acc = round((total_cor / total_ans * 100.0), 1) if total_ans > 0 else 0.0
        category_stats.append({
            'category': r['category'],
            'total_in_cat': r['total_in_cat'],
            'practiced_in_cat': r['practiced_in_cat'],
            'accuracy': acc,
            'total_wrong': r['total_wrg']
        })
        
    # 5. Top 10 most missed questions
    if subject:
        cursor.execute('''
        SELECT q.id, q.category, q.topic, q.question, q.law_ref, s.times_wrong, s.times_answered
        FROM questions q
        JOIN question_stats s ON q.id = s.question_id
        WHERE s.times_wrong > 0 AND (q.subject = ? OR (q.subject IS NULL AND ? = 'law'))
        ORDER BY s.times_wrong DESC, s.times_answered DESC
        LIMIT 10
        ''', (subject, subject))
    else:
        cursor.execute('''
        SELECT q.id, q.category, q.topic, q.question, q.law_ref, s.times_wrong, s.times_answered
        FROM questions q
        JOIN question_stats s ON q.id = s.question_id
        WHERE s.times_wrong > 0
        ORDER BY s.times_wrong DESC, s.times_answered DESC
        LIMIT 10
        ''')
    top_mistakes = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    
    return {
        'total_bank_questions': total_bank_questions,
        'total_exams': total_exams,
        'avg_score': avg_score,
        'practiced_count': practiced_count,
        'mistake_count': mistake_count,
        'mastered_count': mastered_count,
        'overall_accuracy': overall_accuracy,
        'category_stats': category_stats,
        'top_mistakes': top_mistakes
    }

def toggle_bookmark(question_id, note=''):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_bookmarks WHERE question_id = ?', (question_id,))
    if cursor.fetchone():
        cursor.execute('DELETE FROM user_bookmarks WHERE question_id = ?', (question_id,))
        is_bookmarked = False
    else:
        cursor.execute('INSERT INTO user_bookmarks (question_id, note) VALUES (?, ?)', (question_id, note))
        is_bookmarked = True
    conn.commit()
    conn.close()
    return is_bookmarked

def get_all_bookmarks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT question_id FROM user_bookmarks')
    rows = cursor.fetchall()
    conn.close()
    return set([r['question_id'] for r in rows])

def add_custom_question(category, topic, question, options, answer_index, explanation, law_ref, subject='law'):
    conn = get_connection()
    cursor = conn.cursor()
    
    prefix = 'COM' if subject == 'computer' else 'Q'
    cursor.execute('SELECT COUNT(*) as count FROM questions WHERE subject = ?', (subject,))
    count = cursor.fetchone()['count'] + 1
    new_id = f"{prefix}{count:03d}"
    
    cursor.execute('''
    INSERT INTO questions (id, subject, category, topic, question, options_json, answer_index, explanation, law_ref)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (new_id, subject, category, topic, question, json.dumps(options, ensure_ascii=False), answer_index, explanation, law_ref))
    
    conn.commit()
    conn.close()
    return new_id
    
    conn.commit()
    conn.close()
    return new_id

def reset_all_statistics():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM exam_sessions')
    cursor.execute('DELETE FROM question_stats')
    cursor.execute('DELETE FROM user_bookmarks')
    conn.commit()
    conn.close()

# Initialize upon import
init_db()
