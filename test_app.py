# -*- coding: utf-8 -*-
import unittest
import os
import json
import db
import quiz_engine

class TestQuizApp(unittest.TestCase):
    def setUp(self):
        db.init_db()
        
    def test_database_questions(self):
        questions = db.get_all_questions()
        self.assertGreaterEqual(len(questions), 100, 'Database should contain at least 100 questions (Law + Computer)')
        
        # Verify question structure
        for q in questions[:10]:
            self.assertTrue(q['id'].startswith('Q') or q['id'].startswith('COM'))
            self.assertEqual(len(q['options']), 4)
            self.assertIn(q['answer_index'], [0, 1, 2, 3])
            self.assertTrue(len(q['explanation']) > 0)
            self.assertTrue(len(q['law_ref']) > 0)
            
    def test_subjects_filtering(self):
        law_qs = db.get_all_questions(subject='law')
        com_qs = db.get_all_questions(subject='computer')
        self.assertGreaterEqual(len(law_qs), 50, 'Should have at least 50 Law questions')
        self.assertGreaterEqual(len(com_qs), 50, 'Should have at least 50 Computer questions')
        
        # Check random sampling for subjects
        random_com = db.get_random_questions(count=30, subject='computer')
        self.assertEqual(len(random_com), 30)
        for q in random_com:
            self.assertEqual(q['subject'], 'computer')
            
    def test_random_selection(self):
        sample_50 = db.get_random_questions(count=50)
        self.assertEqual(len(sample_50), 50)
        
        # Check uniqueness
        ids = [q['id'] for q in sample_50]
        self.assertEqual(len(ids), len(set(ids)), 'All 50 selected questions should be unique')
        
    def test_record_answer_and_mistake_tracking(self):
        # Pick first question
        q = db.get_all_questions()[0]
        qid = q['id']
        correct_ans = q['answer_index']
        wrong_ans = (correct_ans + 1) % 4
        
        # 1. Record a wrong answer
        db.record_answer(qid, wrong_ans, is_correct=False)
        
        # Check mistake bank
        mistakes = db.get_mistake_questions()
        mistake_ids = [m['id'] for m in mistakes]
        self.assertIn(qid, mistake_ids, 'Question answered wrongly should appear in mistake bank')
        
        # 2. Record correct answers to increase mastery
        db.record_answer(qid, correct_ans, is_correct=True)
        db.record_answer(qid, correct_ans, is_correct=True)
        db.record_answer(qid, correct_ans, is_correct=True)
        
        stats = db.get_dashboard_stats()
        self.assertGreater(stats['practiced_count'], 0)
        
    def test_exam_session_calculation(self):
        class DummySessionState(dict):
            __getattr__ = dict.get
            __setattr__ = dict.__setitem__
            
        dummy_state = DummySessionState()
        quiz_engine.init_session_state(dummy_state)
        
        quiz_engine.start_simulation_exam(dummy_state, count=50, duration_minutes=60)
        self.assertTrue(dummy_state.exam_active)
        self.assertEqual(len(dummy_state.exam_questions), 50)
        
        # Answer first 30 correctly, next 10 wrongly, leave 10 unanswered
        for i in range(30):
            correct_idx = dummy_state.exam_questions[i]['answer_index']
            dummy_state.user_answers[i] = correct_idx
        for i in range(30, 40):
            correct_idx = dummy_state.exam_questions[i]['answer_index']
            dummy_state.user_answers[i] = (correct_idx + 1) % 4
            
        result = quiz_engine.calculate_and_save_exam_results(dummy_state)
        self.assertEqual(result['total_questions'], 50)
        self.assertEqual(result['score'], 30)
        self.assertEqual(result['wrong_count'], 10)
        self.assertEqual(result['unanswered_count'], 10)
        self.assertEqual(result['percentage'], 60.0)
        self.assertTrue(result['passed'])

if __name__ == '__main__':
    unittest.main()
