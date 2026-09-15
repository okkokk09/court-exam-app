# -*- coding: utf-8 -*-
import unittest
import os
import json
import db
import quiz_engine

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), 'test_exam_data_runner.db')

class TestQuizApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orig_db_path = db.DB_PATH
        db.DB_PATH = TEST_DB_PATH
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
        db.init_db()

    @classmethod
    def tearDownClass(cls):
        db.DB_PATH = cls.orig_db_path
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except Exception:
                pass

    def setUp(self):
        pass
        
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
        mistakes = db.get_mistake_questions(limit=500)
        mistake_ids = [m['id'] for m in mistakes]
        self.assertIn(qid, mistake_ids, 'Question answered wrongly should appear in mistake bank')
        
        # 2. Record correct answers to increase mastery
        db.record_answer(qid, correct_ans, is_correct=True)
        db.record_answer(qid, correct_ans, is_correct=True)
        db.record_answer(qid, correct_ans, is_correct=True)
        
        stats = db.get_dashboard_stats()
        self.assertGreater(stats['practiced_count'], 0)
        
        # 3. Test clearing mistake on correct in review mode
        db.record_answer(qid, correct_ans, is_correct=True, clear_mistake_on_correct=True)
        mistakes_after = db.get_mistake_questions()
        mistake_ids_after = [m['id'] for m in mistakes_after]
        self.assertNotIn(qid, mistake_ids_after, 'Question cleared in review mode should no longer be in mistake bank')
        
        # 4. Test manual clear_question_mistake
        q2 = db.get_all_questions()[1]
        db.record_answer(q2['id'], (q2['answer_index'] + 1) % 4, is_correct=False)
        self.assertIn(q2['id'], [m['id'] for m in db.get_mistake_questions(limit=500)])
        db.clear_question_mistake(q2['id'])
        self.assertNotIn(q2['id'], [m['id'] for m in db.get_mistake_questions(limit=500)])
        
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

    def test_shuffle_question_options(self):
        sample_q = {
            'id': 'TEST_01',
            'question': 'Sample Question?',
            'options': ['Choice A', 'Choice B', 'Choice C', 'Choice D'],
            'answer_index': 1 # Choice B
        }
        
        # Test 50 iterations to ensure correct text is always tracked
        for _ in range(50):
            shuffled = quiz_engine.shuffle_question_options(sample_q)
            new_idx = shuffled['answer_index']
            self.assertEqual(shuffled['options'][new_idx], 'Choice B', 'Shuffled answer_index must always point to correct choice text')
            self.assertEqual(len(shuffled['options']), 4)
            self.assertEqual(set(shuffled['options']), set(sample_q['options']))

    def test_abandon_exam(self):
        class DummySessionState(dict):
            __getattr__ = dict.get
            __setattr__ = dict.__setitem__
            
        dummy_state = DummySessionState()
        quiz_engine.init_session_state(dummy_state)
        quiz_engine.start_simulation_exam(dummy_state, count=50, duration_minutes=60)
        self.assertTrue(dummy_state.exam_active)
        
        # User abandons exam
        quiz_engine.abandon_exam(dummy_state)
        self.assertFalse(dummy_state.exam_active)
        self.assertFalse(dummy_state.exam_submitted)
        self.assertEqual(len(dummy_state.exam_questions), 0)
        self.assertEqual(len(dummy_state.user_answers), 0)
        self.assertIsNone(dummy_state.exam_result)

    def test_mistakes_retest_and_session_state(self):
        class DummySessionState(dict):
            __getattr__ = dict.get
            __setattr__ = dict.__setitem__
            
        dummy_state = DummySessionState()
        quiz_engine.init_session_state(dummy_state)
        quiz_engine.start_simulation_exam(dummy_state, count=20, duration_minutes=30)
        
        # Answer 15 correctly and 5 wrongly
        for i in range(15):
            correct_idx = dummy_state.exam_questions[i]['answer_index']
            dummy_state.user_answers[i] = correct_idx
        for i in range(15, 20):
            correct_idx = dummy_state.exam_questions[i]['answer_index']
            dummy_state.user_answers[i] = (correct_idx + 1) % 4
            
        result = quiz_engine.calculate_and_save_exam_results(dummy_state)
        self.assertEqual(result['wrong_count'], 5)
        self.assertEqual(len(dummy_state.mistakes), 5, 'st.session_state.mistakes should store exactly the 5 missed questions')
        
        # Start re-test with mistakes only
        retest_started = quiz_engine.start_mistakes_retest(dummy_state)
        self.assertTrue(retest_started)
        self.assertTrue(dummy_state.exam_active)
        self.assertEqual(dummy_state.exam_mode, 'mistakes_retest')
        self.assertEqual(len(dummy_state.exam_questions), 5, 'Retest questions should contain only the 5 missed questions')
        self.assertEqual(len(dummy_state.user_answers), 0)

    def test_full_simulation_exam(self):
        class DummySessionState(dict):
            __getattr__ = dict.get
            __setattr__ = dict.__setitem__
            
        # 1. Test database full simulation sampling
        sim_qs = db.get_full_simulation_questions(law_count=30, computer_count=70)
        self.assertEqual(len(sim_qs), 100, "Full simulation must contain exactly 100 questions")
        
        law_qs = [q for q in sim_qs if q.get('subject') == 'law']
        com_qs = [q for q in sim_qs if q.get('subject') == 'computer']
        self.assertEqual(len(law_qs), 30, "Must contain exactly 30 Law questions")
        self.assertEqual(len(com_qs), 70, "Must contain exactly 70 Computer questions")
        
        # Check uniqueness
        sim_ids = [q['id'] for q in sim_qs]
        self.assertEqual(len(sim_ids), len(set(sim_ids)), "All 100 questions must be unique")
        
        # 2. Test starting full simulation exam
        dummy_state = DummySessionState()
        quiz_engine.init_session_state(dummy_state)
        quiz_engine.start_full_simulation_exam(dummy_state, duration_minutes=180)
        
        self.assertTrue(dummy_state.exam_active)
        self.assertEqual(dummy_state.exam_mode, 'full_simulation')
        self.assertEqual(len(dummy_state.exam_questions), 100)
        self.assertEqual(dummy_state.duration_seconds, 180 * 60) # 10800s
        
        # Verify ordering: Law questions first (0..29), Computer questions second (30..99)
        for q in dummy_state.exam_questions[:30]:
            self.assertEqual(q['subject'], 'law', "First 30 questions must be Law")
        for q in dummy_state.exam_questions[30:]:
            self.assertEqual(q['subject'], 'computer', "Remaining 70 questions must be Computer")
        
        # 3. Test 200-point scoring: Answer 86 correctly (172 points -> Top 10 tier)
        for i in range(86):
            correct_idx = dummy_state.exam_questions[i]['answer_index']
            dummy_state.user_answers[i] = correct_idx
        for i in range(86, 95): # 9 wrong
            correct_idx = dummy_state.exam_questions[i]['answer_index']
            dummy_state.user_answers[i] = (correct_idx + 1) % 4
        # 5 unanswered (95..99)
        
        res = quiz_engine.calculate_and_save_exam_results(dummy_state)
        self.assertTrue(res['is_full_simulation'])
        self.assertEqual(res['total_questions'], 100)
        self.assertEqual(res['points_per_question'], 2)
        self.assertEqual(res['total_points'], 200)
        self.assertEqual(res['score'], 86)
        self.assertEqual(res['earned_points'], 172)
        self.assertEqual(res['wrong_count'], 9)
        self.assertEqual(res['unanswered_count'], 5)
        self.assertEqual(res['percentage'], 86.0)
        self.assertTrue(res['passed'])
        self.assertEqual(res['tier'], 'top10')
        self.assertIn('Top 10', res['tier_title'])
        
        # 4. Verify Subject Breakdown stats
        subj_stats = res['subject_stats']
        # 5. Verify get_full_simulation_stats
        full_stats = db.get_full_simulation_stats()
        self.assertGreater(full_stats['total_exams'], 0)
        self.assertGreater(full_stats['max_points'], 0)
        self.assertIsNotNone(full_stats['latest_session'])

    def test_multi_user_isolation(self):
        class DummySessionState(dict):
            __getattr__ = dict.get
            __setattr__ = dict.__setitem__

        # 1. User 1 answers a question wrongly
        q1 = db.get_all_questions()[0]
        qid1 = q1['id']
        wrong_ans = (q1['answer_index'] + 1) % 4
        
        db.record_answer(qid1, wrong_ans, is_correct=False, username='User 1')
        
        # User 1 should have this in mistake bank, User 2 should NOT
        user1_mistakes = [m['id'] for m in db.get_mistake_questions(username='User 1')]
        user2_mistakes = [m['id'] for m in db.get_mistake_questions(username='User 2')]
        self.assertIn(qid1, user1_mistakes)
        self.assertNotIn(qid1, user2_mistakes)
        
        # 2. Bookmarks isolation
        db.toggle_bookmark(qid1, username='User 1')
        user1_bms = db.get_all_bookmarks(username='User 1')
        user2_bms = db.get_all_bookmarks(username='User 2')
        self.assertIn(qid1, user1_bms)
        self.assertNotIn(qid1, user2_bms)
        
        # 3. Exam sessions isolation
        u1_count_before = db.get_dashboard_stats(username='User 1')['total_exams']
        
        state_u2 = DummySessionState()
        quiz_engine.init_session_state(state_u2)
        state_u2.current_user = 'User 2'
        quiz_engine.start_simulation_exam(state_u2, count=10, duration_minutes=15)
        for i in range(10):
            state_u2.user_answers[i] = state_u2.exam_questions[i]['answer_index']
            
        res_u2 = quiz_engine.calculate_and_save_exam_results(state_u2)
        self.assertEqual(res_u2['score'], 10)
        
        # Verify stats isolation
        stats_u1 = db.get_dashboard_stats(username='User 1')
        stats_u2 = db.get_dashboard_stats(username='User 2')
        self.assertEqual(stats_u1['total_exams'], u1_count_before) # User 1 count remains unchanged
        self.assertEqual(stats_u2['total_exams'], 1) # User 2 took 1 exam
        
        # 4. Selective Reset Isolation (Reset User 1 only)
        db.reset_all_statistics(username='User 1')
        self.assertEqual(len(db.get_all_bookmarks(username='User 1')), 0)
        self.assertEqual(db.get_dashboard_stats(username='User 1')['total_exams'], 0)
        
        # User 2 exam history must remain intact
        stats_u2_after = db.get_dashboard_stats(username='User 2')
        self.assertEqual(stats_u2_after['total_exams'], 1)

    def test_time_formatting(self):
        # Test 3 hours countdown
        self.assertEqual(quiz_engine.format_time_hhmmss(10800), "03:00:00")
        self.assertEqual(quiz_engine.format_time_hhmmss(3665), "01:01:05")
        # Under 1 hour
        self.assertEqual(quiz_engine.format_time_hhmmss(3599), "59:59")
        self.assertEqual(quiz_engine.format_time_hhmmss(125), "02:05")
        self.assertEqual(quiz_engine.format_time_hhmmss(0), "00:00")

if __name__ == '__main__':
    unittest.main()



