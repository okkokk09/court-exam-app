# -*- coding: utf-8 -*-

DEFAULT_CATEGORY = 'oag'

# รายการ 9 หมวดวิชาหลักตามหลักสูตรสอบ นักวิชาการคอมพิวเตอร์ปฏิบัติการ สำนักงานอัยการสูงสุด (ภาค ข.)
OAG_9_CATEGORIES = [
    {
        'id': 'cat1_oag_org',
        'number': 1,
        'name': 'หมวดที่ 1: พ.ร.บ.องค์กรอัยการและพนักงานอัยการ พ.ศ. 2553',
        'short': 'พ.ร.บ.องค์กรอัยการฯ 2553',
        'icon': '⚖️',
        'subject': 'law',
        'description': 'โครงสร้าง อำนาจหน้าที่พนักงานอัยการ (ม.14) ความเป็นอิสระในการสั่งคดี (ม.21) การสั่งไม่ฟ้อง และการรักษาราชการแทน',
        'law_ref': 'พ.ร.บ.องค์กรอัยการและพนักงานอัยการ พ.ศ. 2553',
        'keywords': ['องค์กรอัยการ', 'พนักงานอัยการ', 'มาตรา 14', 'มาตรา 21', 'สั่งคดี', 'สอศ.', 'อัยการสูงสุด', 'สั่งไม่ฟ้อง']
    },
    {
        'id': 'cat2_oag_service',
        'number': 2,
        'name': 'หมวดที่ 2: พ.ร.บ.ระเบียบข้าราชการฝ่ายอัยการ พ.ศ. 2553',
        'short': 'พ.ร.บ.ระเบียบข้าราชการฝ่ายอัยการฯ',
        'icon': '👥',
        'subject': 'law',
        'description': 'คณะกรรมการอัยการ (ก.อ.) การบริหารงานบุคคล ชั้นและตำแหน่งข้าราชการอัยการ วินัยและการรักษาวินัย 5 สถาน',
        'law_ref': 'พ.ร.บ.ระเบียบข้าราชการฝ่ายอัยการ พ.ศ. 2553',
        'keywords': ['ก.อ.', 'ข้าราชการฝ่ายอัยการ', 'ข้าราชการธุรการ', 'วินัย', 'ตำแหน่ง', 'ปลดออก', 'ไล่ออก', 'ภาคทัณฑ์']
    },
    {
        'id': 'cat3_cybersecurity',
        'number': 3,
        'name': 'หมวดที่ 3: พ.ร.บ.การรักษาความมั่นคงปลอดภัยไซเบอร์ พ.ศ. 2562',
        'short': 'พ.ร.บ.ไซเบอร์ฯ 2562',
        'icon': '🛡️',
        'subject': 'computer',
        'description': '3 ระดับภัยคุกคามไซเบอร์ (ไม่ร้ายแรง, ร้ายแรง, วิกฤติ) โครงสร้างพื้นฐานสำคัญทางสารสนเทศ (CII 8 ด้าน) และอำนาจ สกมช.',
        'law_ref': 'พ.ร.บ.การรักษาความมั่นคงปลอดภัยไซเบอร์ พ.ศ. 2562',
        'keywords': ['ไซเบอร์', 'CII', 'ภัยคุกคาม', 'สกมช.', 'สมช.', 'วิกฤติ', 'ร้ายแรง', 'โครงสร้างพื้นฐานสำคัญ']
    },
    {
        'id': 'cat4_pdpa',
        'number': 4,
        'name': 'หมวดที่ 4: พ.ร.บ.คุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562 (PDPA) & นโยบาย อสส.',
        'short': 'พ.ร.บ.คุ้มครองข้อมูลส่วนบุคคล (PDPA)',
        'icon': '🔒',
        'subject': 'computer',
        'description': '6 ฐานการประมวลผลข้อมูล สิทธิเจ้าของข้อมูล ข้อมูลอ่อนไหว (Sensitive Data) และการแจ้ง Data Breach ภายใน 72 ชม.',
        'law_ref': 'พ.ร.บ.คุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562',
        'keywords': ['PDPA', 'ข้อมูลส่วนบุคคล', 'Consent', 'ละเมิดข้อมูล', '72 ชม.', 'Sensitive', 'ผู้ควบคุมข้อมูล', 'DPO']
    },
    {
        'id': 'cat5_saraban',
        'number': 5,
        'name': 'หมวดที่ 5: ระเบียบสำนักนายกรัฐมนตรี ว่าด้วยงานสารบรรณ พ.ศ. 2526',
        'short': 'ระเบียบงานสารบรรณฯ',
        'icon': '📝',
        'subject': 'law',
        'description': 'หนังสือราชการ 6 ชนิด เงื่อนไขการใช้หนังสือประทับตรา 8 กรณี คำขึ้นต้น-ลงท้าย และอายุการเก็บรักษา 10 ปี',
        'law_ref': 'ระเบียบสำนักนายกรัฐมนตรี ว่าด้วยงานสารบรรณ พ.ศ. 2526',
        'keywords': ['สารบรรณ', 'หนังสือภายนอก', 'หนังสือภายใน', 'ประทับตรา', '10 ปี', 'ทำลายหนังสือ', 'ตราครุฑ', 'รายงานการประชุม']
    },
    {
        'id': 'cat6_procurement',
        'number': 6,
        'name': 'หมวดที่ 6: ระเบียบกระทรวงการคลังว่าด้วยการจัดซื้อจัดจ้างฯ พ.ศ. 2560',
        'short': 'ระเบียบจัดซื้อจัดจ้างฯ 2560',
        'icon': '💼',
        'subject': 'law',
        'description': '3 วิธีจัดซื้อจัดจ้าง (เชิญชวนทั่วไป, คัดเลือก, เฉพาะเจาะจง ไม่เกิน 500,000 บาท) และข้อห้ามคณะกรรมการตรวจรับพัสดุ',
        'law_ref': 'พ.ร.บ.การจัดซื้อจัดจ้างและการบริหารพัสดุภาครัฐ พ.ศ. 2560',
        'keywords': ['จัดซื้อจัดจ้าง', 'พัสดุ', 'เฉพาะเจาะจง', '500,000', 'e-bidding', 'e-market', 'ตรวจรับพัสดุ', 'คัดเลือก']
    },
    {
        'id': 'cat7_oag_policy',
        'number': 7,
        'name': 'หมวดที่ 7: นโยบาย ยุทธศาสตร์ และภารกิจสำนักงานอัยการสูงสุด',
        'short': 'นโยบาย & ยุทธศาสตร์ อสส.',
        'icon': '🏛️',
        'subject': 'law',
        'description': 'วิสัยทัศน์ อสส. 4 พันธกิจหลัก Smart OAG นวัตกรรม e-Prosecution และการคุ้มครองสิทธิประชาชน (สคช.)',
        'law_ref': 'แผนปฏิบัติราชการและนโยบายสำนักงานอัยการสูงสุด',
        'keywords': ['วิสัยทัศน์', 'ยุทธศาสตร์', 'Smart OAG', 'สคช.', 'พันธกิจ', 'คุ้มครองสิทธิ', 'e-Prosecution', 'อัยการสูงสุด']
    },
    {
        'id': 'cat8_programming',
        'number': 8,
        'name': 'หมวดที่ 8: การเขียนโปรแกรมและการพัฒนาโปรแกรมประยุกต์',
        'short': 'การเขียนโปรแกรม (Programming)',
        'icon': '💻',
        'subject': 'computer',
        'description': 'หลักการเขียนโค้ด (Python, SQL, Web) ขั้นตอนวิธี (Algorithm) โครงสร้างข้อมูล (Data Structure) OOP และ Secure Coding',
        'law_ref': 'หลักการวิศวกรรมซอฟต์แวร์และการเขียนโปรแกรม',
        'keywords': ['Python', 'SQL', 'Algorithm', 'Data Structure', 'Logic', 'Web', 'API', 'Loop', 'OOP', 'Function']
    },
    {
        'id': 'cat9_systems_security',
        'number': 9,
        'name': 'หมวดที่ 9: ระบบคอมพิวเตอร์ เครือข่าย ฐานข้อมูล และความมั่นคงปลอดภัย',
        'short': 'ระบบคอมพิวเตอร์ เครือข่าย & Security',
        'icon': '🌐',
        'subject': 'computer',
        'description': 'Hardware, OS, Computer Network, RDBMS, Cyber Security และ พ.ร.บ.ว่าด้วยการกระทำความผิดเกี่ยวกับคอมพิวเตอร์ 2550',
        'law_ref': 'พ.ร.บ.ว่าด้วยการกระทำความผิดเกี่ยวกับคอมพิวเตอร์ พ.ศ. 2550',
        'keywords': ['Hardware', 'OS', 'Network', 'TCP/IP', 'Database', 'พ.ร.บ.คอมฯ', 'Security', 'Malware', 'Firewall']
    }
]

EXAM_CATEGORIES = {
    'oag': {
        'id': 'oag',
        'icon': '⚖️',
        'name': 'สอบสำนักงานอัยการสูงสุด',
        'short_name': 'สำนักงานอัยการสูงสุด',
        'position': 'นักวิชาการคอมพิวเตอร์ปฏิบัติการ สำนักงานอัยการสูงสุด',
        'badge': 'OAG COMPUTER OFFICER EXAM 200 PTS',
        'law_label': 'พ.ร.บ.องค์กรอัยการและระเบียบที่เกี่ยวข้อง (6 ฉบับ + นโยบาย)',
        'law_short': 'กฎหมายและระเบียบอัยการ',
        'law_desc': 'กฎหมายองค์กรอัยการ ระเบียบข้าราชการฝ่ายอัยการ ไซเบอร์ PDPA สารบรรณ จัดซื้อจัดจ้าง และนโยบาย อสส.',
        'computer_label': 'คอมพิวเตอร์และเทคโนโลยีสารสนเทศ',
        'computer_short': 'คอมพิวเตอร์และสารสนเทศ',
        'computer_desc': 'การเขียนโปรแกรม ฐานข้อมูล ระบบเครือข่าย ความมั่นคงปลอดภัย และการวิเคราะห์ออกแบบระบบ',
        'default_law_ref': 'พ.ร.บ.องค์กรอัยการและพนักงานอัยการ พ.ศ. 2553',
        'full_exam_enabled': True,
        'categories_9': OAG_9_CATEGORIES,
        'law_categories': [c['name'] for c in OAG_9_CATEGORIES if c['subject'] == 'law'],
        'computer_categories': [c['name'] for c in OAG_9_CATEGORIES if c['subject'] == 'computer']
    }
}

def get_category_keys():
    return list(EXAM_CATEGORIES.keys())

def get_active(st_session_state=None):
    if st_session_state is not None:
        cat_key = st_session_state.get('exam_category', DEFAULT_CATEGORY)
        if cat_key in EXAM_CATEGORIES:
            return EXAM_CATEGORIES[cat_key]
    return EXAM_CATEGORIES[DEFAULT_CATEGORY]

def get_oag_9_categories():
    return OAG_9_CATEGORIES

def get_category_by_id(cat_id):
    for cat in OAG_9_CATEGORIES:
        if cat['id'] == cat_id or cat.get('number') == cat_id or str(cat.get('number')) == str(cat_id):
            return cat
    return None

def map_question_to_oag_category(q):
    '''
    Maps any question dictionary to one of the 9 OAG categories based on
    its category, law_ref, topic, and question content.
    '''
    q_cat = q.get('category', '')
    law_ref = q.get('law_ref', '')
    topic = q.get('topic', '')
    text = (q.get('question', '') + " " + q.get('explanation', '') + " " + law_ref + " " + topic + " " + q_cat).lower()
    subject = q.get('subject', 'law')
    
    # 1. Check for specific law / regulation matches
    if 'สารบรรณ' in text:
        return OAG_9_CATEGORIES[4] # Cat 5
    if 'จัดซื้อจัดจ้าง' in text or 'พัสดุ' in text:
        return OAG_9_CATEGORIES[5] # Cat 6
    if 'cyber' in text or 'ไซเบอร์' in text or 'สกมช' in text or 'cii' in text:
        return OAG_9_CATEGORIES[2] # Cat 3
    if 'pdpa' in text or 'ข้อมูลส่วนบุคคล' in text:
        return OAG_9_CATEGORIES[3] # Cat 4
    if 'ข้าราชการฝ่ายอัยการ' in text or 'ก.อ.' in text:
        return OAG_9_CATEGORIES[1] # Cat 2
    if 'วิสัยทัศน์' in text or 'ยุทธศาสตร์' in text or 'พันธกิจ' in text or 'นโยบาย' in text:
        return OAG_9_CATEGORIES[6] # Cat 7
    if 'องค์กรอัยการ' in text or 'พนักงานอัยการ' in text or 'อัยการสูงสุด' in text:
        return OAG_9_CATEGORIES[0] # Cat 1
        
    # 2. Check for computer categories
    if subject == 'computer':
        prog_keywords = [
            'python', 'code', 'programming', 'loop', 'algorithm', 'function', 'class',
            'array', 'string', 'variable', 'syntax', 'c++', 'java', 'sql', 'query',
            'เขียนคำสั่ง', 'เขียนโปรแกรม', 'โปรแกรม', 'การพัฒนา', 'ขั้นตอนวิธี', 'โครงสร้างข้อมูล',
            'ตรรกะ', 'อัลกอริทึม', 'object-oriented', 'oop', 'api', 'framework', 'database', 'ฐานข้อมูล'
        ]
        if any(kw in text for kw in prog_keywords):
            return OAG_9_CATEGORIES[7] # Cat 8: Programming
        return OAG_9_CATEGORIES[8] # Cat 9: Systems, Network & Security
        
    # Default fallback by subject
    return OAG_9_CATEGORIES[0] if subject == 'law' else OAG_9_CATEGORIES[8]
