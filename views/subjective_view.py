# -*- coding: utf-8 -*-
import sqlite3
import html
import re
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# 1. SQL LAB ENGINE & DATABASE SETUP (In-Memory SQLite)
# ==============================================================================

def create_oag_sample_db():
    '''Creates an in-memory SQLite database populated with realistic OAG case data'''
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Attorneys Table
    cursor.execute('''
    CREATE TABLE attorneys (
        attorney_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        position TEXT NOT NULL,
        department TEXT NOT NULL,
        active_status TEXT DEFAULT 'ACTIVE'
    );
    ''')
    
    attorneys_data = [
        (1, 'นายธนกร สัจจะพิทักษ์', 'อัยการจังหวัด', 'สำนักงานอัยการจังหวัดนนทบุรี', 'ACTIVE'),
        (2, 'นางสาวกานดา เที่ยงธรรม', 'รองอัยการจังหวัด', 'สำนักงานอัยการจังหวัดนนทบุรี', 'ACTIVE'),
        (3, 'นายพิเชษฐ์ ยุติธรรมรักษา', 'อัยการประจำกอง', 'สำนักงานคดีพิเศษ', 'ACTIVE'),
        (4, 'นางวรรณา รักษ์กฎหมาย', 'อัยการผู้เชี่ยวชาญ', 'สำนักงานคดีเศรษฐกิจและทรัพยากร', 'ACTIVE'),
        (5, 'นายสมศักดิ์ สุจริตธรรม', 'อัยการจังหวัดประจำสำนักงาน', 'สำนักงานคดีปราบปรามการทุจริต', 'INACTIVE')
    ]
    cursor.executemany('INSERT INTO attorneys VALUES (?, ?, ?, ?, ?)', attorneys_data)
    
    # 2. Courts Table
    cursor.execute('''
    CREATE TABLE courts (
        court_id INTEGER PRIMARY KEY,
        court_name TEXT NOT NULL,
        court_type TEXT NOT NULL
    );
    ''')
    
    courts_data = [
        (101, 'ศาลจังหวัดนนทบุรี', 'ศาลชั้นต้น'),
        (102, 'ศาลอาญาคดีทุจริตและประพฤติมิชอบภาค 1', 'ศาลชั้นต้นชำนัญพิเศษ'),
        (103, 'ศาลอาญา', 'ศาลชั้นต้น'),
        (104, 'ศาลทรัพย์สินทางปัญญาและการค้าระหว่างประเทศกลาง', 'ศาลชำนัญพิเศษ')
    ]
    cursor.executemany('INSERT INTO courts VALUES (?, ?, ?)', courts_data)
    
    # 3. Cases Table
    cursor.execute('''
    CREATE TABLE cases (
        case_id INTEGER PRIMARY KEY,
        case_number TEXT NOT NULL,
        title TEXT NOT NULL,
        charge TEXT NOT NULL,
        court_id INTEGER,
        attorney_id INTEGER,
        status TEXT NOT NULL,
        filing_date TEXT NOT NULL,
        lawsuit_amount REAL DEFAULT 0.0,
        FOREIGN KEY (court_id) REFERENCES courts(court_id),
        FOREIGN KEY (attorney_id) REFERENCES attorneys(attorney_id)
    );
    ''')
    
    cases_data = [
        (1001, 'อ.124/2567', 'คดีลักทรัพย์นายจ้างในเวลากลางคืน', 'ลักทรัพย์', 101, 1, 'กำลังดำเนินคดี', '2024-02-15', 350000.0),
        (1002, 'ทจ.45/2567', 'คดีเรียกรับสินบนจัดซื้อเครื่องตรวจจับ', 'ทุจริตต่อหน้าที่', 102, 3, 'กำลังดำเนินคดี', '2024-03-01', 12500000.0),
        (1003, 'อ.550/2567', 'คดีฉ้อโกงประชาชนผ่านระบบคอมพิวเตอร์', 'ฉ้อโกงประชาชน', 101, 2, 'สั่งฟ้องแล้ว', '2024-01-20', 4800000.0),
        (1004, 'ศก.12/2567', 'คดีลักลอบนำเข้าสินค้าเลี่ยงภาษีศุลกากร', 'ศุลกากร', 104, 4, 'กำลังดำเนินคดี', '2024-04-10', 8900000.0),
        (1005, 'อ.780/2567', 'คดีทำร้ายร่างกายสาหัสและพกพาอาวุธ', 'ทำร้ายร่างกาย', 103, 1, 'รอคำสั่งฟ้อง', '2024-05-02', 150000.0),
        (1006, 'ทจ.88/2567', 'คดีเอื้อประโยชน์ฮั้วประมูลระบบสายเคเบิล', 'ทุจริตต่อหน้าที่', 102, 3, 'กำลังดำเนินคดี', '2024-05-18', 45000000.0),
        (1007, 'อ.902/2567', 'คดีฟอกเงินขบวนการแก๊งคอลเซ็นเตอร์', 'ฉ้อโกงประชาชน', 103, 2, 'กำลังดำเนินคดี', '2024-06-01', 32000000.0),
        (1008, 'อ.915/2567', 'คดีหมิ่นประมาททางออนไลน์', 'พ.ร.บ.คอมพิวเตอร์', 101, 2, 'สั่งไม่ฟ้อง', '2024-06-15', 50000.0)
    ]
    cursor.executemany('INSERT INTO cases VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', cases_data)
    
    # 4. Evidence Items Table
    cursor.execute('''
    CREATE TABLE evidence_items (
        evidence_id INTEGER PRIMARY KEY,
        case_id INTEGER,
        item_name TEXT NOT NULL,
        item_type TEXT NOT NULL,
        storage_location TEXT,
        is_digital INTEGER DEFAULT 0,
        FOREIGN KEY (case_id) REFERENCES cases(case_id)
    );
    ''')
    
    evidence_data = [
        (201, 1001, 'ฮาร์ดดิสก์กล้องวงจรปิด CCTV', 'ดิจิทัล', 'ห้องเก็บหลักฐานดิจิทัล ชั้น 3', 1),
        (202, 1002, 'สมุดบัญชีเงินฝากธนาคารส่วยสินบน', 'เอกสาร', 'ตู้นิรภัย สอศ.', 0),
        (203, 1003, 'ไฟล์ Log การโอนเงินและแชตไลน์', 'ดิจิทัล', 'Cloud Storage สำนวนคดี', 1),
        (204, 1004, 'สินค้าสำแดงเท็จจำนวน 20 ลัง', 'วัตถุพยาน', 'คลังสินค้าทัณฑ์บน', 0),
        (205, 1006, 'ไฟล์เอกสารร่าง TOR ที่แก้ไข', 'ดิจิทัล', None, 1),
        (206, 1007, 'โทรศัพท์มือถือ iPhone 15 Pro Max', 'ดิจิทัล', None, 1)
    ]
    cursor.executemany('INSERT INTO evidence_items VALUES (?, ?, ?, ?, ?, ?)', evidence_data)
    
    conn.commit()
    return conn

# Alias for backward compatibility and tests
create_sample_oag_db = create_oag_sample_db

def run_custom_query(conn, query):
    '''Executes a SQL query on SQLite connection and returns (DataFrame, error_message)'''
    try:
        df = pd.read_sql_query(query, conn)
        return df, None
    except Exception as e:
        return None, str(e)

SQL_CHALLENGES = [
    {
        'id': 'sql_1',
        'title': 'โจทย์ที่ 1: ค้นหาสำนวนคดีที่สถานะกำลังดำเนินคดี (INNER JOIN)',
        'description': 'เขียนคำสั่ง SQL เพื่อดึงข้อมูล `case_number` (เลขคดี), `title` (ชื่อคดี), `charge` (ข้อหา), และ `name` (ชื่อพนักงานอัยการเจ้าของสำนวน) จากตาราง `cases` และ `attorneys` โดยเลือกเฉพาะคดีที่มีสถานะ `status = \'กำลังดำเนินคดี\'` และเรียงลำดับตาม `filing_date` จากใหม่ไปเก่า (DESC)',
        'solution_sql': '''SELECT c.case_number, c.title, c.charge, a.name AS attorney_name
FROM cases c
INNER JOIN attorneys a ON c.attorney_id = a.attorney_id
WHERE c.status = 'กำลังดำเนินคดี'
ORDER BY c.filing_date DESC;''',
        'hint': 'ใช้ `INNER JOIN attorneys ON cases.attorney_id = attorneys.attorney_id` ร่วมกับเงื่อนไข `WHERE status = \'กำลังดำเนินคดี\'` และ `ORDER BY filing_date DESC`'
    },
    {
        'id': 'sql_2',
        'title': 'โจทย์ที่ 2: สรุปสถิติมูลค่าคดีรวมแยกตามข้อหา (GROUP BY + HAVING)',
        'description': 'เขียนคำสั่ง SQL เพื่อสรุปจำนวนคดีทั้งหมด (`total_cases`) และยอดรวมมูลค่าฟ้องร้อง (`total_amount`) แยกตามแต่ละข้อหา (`charge`) โดยแสดงเฉพาะข้อหาที่มียอดรวมมูลค่าฟ้องร้องตั้งแต่ 1,000,000 บาทขึ้นไป และเรียงจากยอดเงินมากไปหาน้อย',
        'solution_sql': '''SELECT charge, COUNT(case_id) AS total_cases, SUM(lawsuit_amount) AS total_amount
FROM cases
GROUP BY charge
HAVING SUM(lawsuit_amount) >= 1000000
ORDER BY total_amount DESC;''',
        'hint': 'ใช้ `GROUP BY charge` ร่วมกับ `HAVING SUM(lawsuit_amount) >= 1000000` และคำนวณ `COUNT(case_id)` และ `SUM(lawsuit_amount)`'
    },
    {
        'id': 'sql_3',
        'title': 'โจทย์ที่ 3: ตรวจสอบพยานหลักฐานดิจิทัลที่ยังไม่ระบุสถานที่จัดเก็บ (LEFT JOIN / NULL check)',
        'description': 'เขียนคำสั่ง SQL เพื่อค้นหาพยานหลักฐานดิจิทัล (`is_digital = 1`) ที่ยังไม่ได้ระบุสถานที่จัดเก็บ (`storage_location IS NULL`) โดยแสดง `case_number`, `title`, `item_name`, และ `item_type`',
        'solution_sql': '''SELECT c.case_number, c.title, e.item_name, e.item_type
FROM evidence_items e
INNER JOIN cases c ON e.case_id = c.case_id
WHERE e.is_digital = 1 AND e.storage_location IS NULL;''',
        'hint': 'ตรวจสอบคอลัมน์ `is_digital = 1` และ `storage_location IS NULL` พร้อม JOIN กับตาราง `cases` เพื่อดึงเลขคดี'
    },
    {
        'id': 'sql_4',
        'title': 'โจทย์ที่ 4: ค้นหาพนักงานอัยการที่รับผิดชอบสำนวนคดีมากที่สุด (SUBQUERY / AGGREGATION)',
        'description': 'เขียนคำสั่ง SQL เพื่อค้นหาชื่อพนักงานอัยการ (`name`), ตำแหน่ง (`position`), และจำนวนคดีความที่รับผิดชอบทั้งหมด (`assigned_cases`) โดยแสดงเฉพาะอัยการที่มีคดีในความรับผิดชอบอย่างน้อย 2 คดีขึ้นไป',
        'solution_sql': '''SELECT a.name, a.position, COUNT(c.case_id) AS assigned_cases
FROM attorneys a
INNER JOIN cases c ON a.attorney_id = c.attorney_id
GROUP BY a.attorney_id, a.name, a.position
HAVING COUNT(c.case_id) >= 2
ORDER BY assigned_cases DESC;''',
        'hint': 'ใช้ `JOIN cases` นับจำนวน `COUNT(c.case_id)` แล้วกรองด้วย `HAVING COUNT(c.case_id) >= 2`'
    }
]

# ==============================================================================
# 2. ER-DIAGRAM & SYSTEM DESIGN CHALLENGES
# ==============================================================================

ERD_CHALLENGES = [
    {
        'id': 'erd_1',
        'title': 'ระบบที่ 1: ระบบรับ-ส่งและติดตามสำนวนคดีอัยการอิเล็กทรอนิกส์ (OAG e-Prosecution)',
        'scenario': '''
**บริบทโจทย์:** สำนักงานอัยการสูงสุดต้องการพัฒนาระบบรับสำนวนคดีจากพนักงานสอบสวน (ตำรวจ) ส่งต่อให้อัยการเจ้าของสำนวนพิจารณาสั่งคดี
**ข้อกำหนดความสัมพันธ์ (Business Rules):**
1. พนักงานอัยการ 1 คน (`ATTORNEY`) สามารถรับผิดชอบสำนวนคดี (`CASE`) ได้หลายคดี (1:N)
2. คดี 1 คดี (`CASE`) ต้องมีพนักงานอัยการผู้รับผิดชอบสำนวนเพียง 1 คน (1:1)
3. คดี 1 คดี สามารถมีผู้ต้องหา (`DEFENDANT`) ได้หลายคน และบุคคล 1 คน อาจเป็นผู้ต้องหาในหลายคดีได้ (M:N) -> ต้องมีตารางเชื่อม `CASE_DEFENDANT`
4. คดี 1 คดี สามารถมีเอกสารสำนวน (`DOCUMENT`) แนบได้หลายไฟล์ (1:N)
5. คดี 1 คดี ถูกยื่นฟ้องต่อศาล (`COURT`) ได้ 1 ศาล แต่ละศาลสามารถรับฟ้องได้หลายคดี (1:N)
''',
        'default_code': '''erDiagram
    ATTORNEY ||--o{ CASE : "assigned_to"
    CASE ||--o{ CASE_DEFENDANT : "involves"
    DEFENDANT ||--o{ CASE_DEFENDANT : "charged_in"
    CASE ||--o{ DOCUMENT : "contains"
    COURT ||--o{ CASE : "jurisdiction_over"
''',
        'model_solution_mermaid': '''erDiagram
    ATTORNEY {
        int attorney_id PK
        string full_name
        string position
        string department
    }
    COURT {
        int court_id PK
        string court_name
        string court_level
    }
    CASE {
        int case_id PK
        string case_number UK
        string title
        string status
        date filing_date
        int attorney_id FK
        int court_id FK
    }
    DEFENDANT {
        int defendant_id PK
        string id_card UK
        string full_name
        date birth_date
    }
    CASE_DEFENDANT {
        int case_id PK,FK
        int defendant_id PK,FK
        string specific_charge
        string bail_status
    }
    DOCUMENT {
        int doc_id PK
        int case_id FK
        string file_name
        string doc_type
        datetime uploaded_at
    }

    ATTORNEY ||--o{ CASE : "supervises (1:N)"
    COURT ||--o{ CASE : "handles (1:N)"
    CASE ||--o{ CASE_DEFENDANT : "has (1:N)"
    DEFENDANT ||--o{ CASE_DEFENDANT : "appears_in (1:N)"
    CASE ||--o{ DOCUMENT : "includes (1:N)"
''',
        'data_dictionary': [
            {'table': 'CASE', 'field': 'case_id', 'type': 'INT', 'key': 'PK', 'null': 'NO', 'desc': 'รหัสคดีหลัก (Auto Increment)'},
            {'table': 'CASE', 'field': 'case_number', 'type': 'VARCHAR(50)', 'key': 'UK', 'null': 'NO', 'desc': 'เลขคดีดำ/คดีแดง เช่น อ.123/2567'},
            {'table': 'CASE', 'field': 'attorney_id', 'type': 'INT', 'key': 'FK', 'null': 'NO', 'desc': 'รหัสอัยการเจ้าของสำนวน'},
            {'table': 'CASE', 'field': 'court_id', 'type': 'INT', 'key': 'FK', 'null': 'NO', 'desc': 'รหัสศาลที่มีเขตอำนาจ'},
            {'table': 'CASE_DEFENDANT', 'field': 'case_id, defendant_id', 'type': 'INT, INT', 'key': 'Composite PK', 'null': 'NO', 'desc': 'ตารางแก้ M:N ระหว่างคดีกับผู้ต้องหา'}
        ]
    },
    {
        'id': 'erd_2',
        'title': 'ระบบที่ 2: ระบบจัดการและตรวจพิสูจน์พยานหลักฐานดิจิทัล (Digital Chain of Custody)',
        'scenario': '''
**บริบทโจทย์:** พัฒนาระบบบันทึกห่วงโซ่การครอบครองพยานหลักฐานดิจิทัล (Chain of Custody) เพื่อป้องกันการแก้ไขทำลายหลักฐาน
**ข้อกำหนดความสัมพันธ์:**
1. คดี (`CASE`) มีพยานหลักฐาน (`EVIDENCE`) ได้หลายชิ้น (1:N)
2. พยานหลักฐาน 1 ชิ้น มีบันทึกประวัติการส่งมอบ-ตรวจพิสูจน์ (`CHAIN_LOG`) ได้หลายครั้งตามลำดับเวลา (1:N)
3. เจ้าหน้าที่ตรวจพิสูจน์ (`OFFICER`) 1 คน สามารถทำบันทึกผลการตรวจพิสูจน์ (`EXAM_REPORT`) ได้หลายรายงาน (1:N)
''',
        'default_code': '''erDiagram
    CASE ||--o{ EVIDENCE : "possesses"
    EVIDENCE ||--o{ CHAIN_LOG : "tracked_by"
    OFFICER ||--o{ CHAIN_LOG : "custodian"
    EVIDENCE ||--o{ EXAM_REPORT : "examined_in"
    OFFICER ||--o{ EXAM_REPORT : "authored_by"
''',
        'model_solution_mermaid': '''erDiagram
    CASE {
        int case_id PK
        string case_number
        string title
    }
    EVIDENCE {
        int evidence_id PK
        int case_id FK
        string item_name
        string hash_sha256
        string storage_vault
    }
    OFFICER {
        int officer_id PK
        string full_name
        string rank_title
        string unit_name
    }
    CHAIN_LOG {
        int log_id PK
        int evidence_id FK
        int released_by FK
        int received_by FK
        datetime transfer_time
        string transfer_purpose
    }
    EXAM_REPORT {
        int report_id PK
        int evidence_id FK
        int examiner_id FK
        text findings_summary
        datetime report_date
    }

    CASE ||--o{ EVIDENCE : "registers"
    EVIDENCE ||--o{ CHAIN_LOG : "transfer_history"
    EVIDENCE ||--o{ EXAM_REPORT : "generates"
    OFFICER ||--o{ CHAIN_LOG : "handles"
    OFFICER ||--o{ EXAM_REPORT : "authors"
''',
        'data_dictionary': [
            {'table': 'EVIDENCE', 'field': 'hash_sha256', 'type': 'CHAR(64)', 'key': '-', 'null': 'NO', 'desc': 'ค่า Hash สำหรับยืนยันความถูกต้องของข้อมูล (Integrity)'},
            {'table': 'CHAIN_LOG', 'field': 'released_by / received_by', 'type': 'INT', 'key': 'FK', 'null': 'NO', 'desc': 'ผู้ส่งมอบและผู้รับมอบพยานหลักฐาน'}
        ]
    }
]

# ==============================================================================
# 3. CODE & SECURITY FIX CHALLENGES (OWASP & Bug Fixing)
# ==============================================================================

SECURITY_CHALLENGES = [
    {
        'id': 'sec_1',
        'title': 'โจทย์ที่ 1: ช่องโหว่ SQL Injection ในระบบค้นหาสำนวนคดี (Python)',
        'vulnerability_type': 'OWASP Top 10 - A03:2021-Injection (SQLi)',
        'description': 'โค้ดฟังก์ชันค้นหาคดีด้านล่างมีช่องโหว่ SQL Injection เนื่องจากนำ `case_no` ที่รับจากผู้ใช้ไปต่อสตริง (String Concatenation) โดยตรง ทำให้ผู้ไม่หวังดีป้อนค่า เช่น `\' OR \'1\'=\'1` เพื่อดึงข้อมูลคดีทั้งหมดได้ จงเขียนโค้ดแก้ไขให้ปลอดภัยด้วย Parameterized Query',
        'vulnerable_code': '''def search_case_by_number(conn, case_no):
    cursor = conn.cursor()
    # ❌ มีช่องโหว่ SQL Injection ร้ายแรง:
    query = f"SELECT * FROM cases WHERE case_number = '{case_no}'"
    cursor.execute(query)
    return cursor.fetchall()
''',
        'starter_code': '''def search_case_by_number(conn, case_no):
    cursor = conn.cursor()
    # ✍️ พิมพ์โค้ดที่ปลอดภัย (Parameterized Query) ที่นี่:
    query = "SELECT * FROM cases WHERE case_number = ?"
    cursor.execute(query, (case_no,))
    return cursor.fetchall()
''',
        'secure_solution': '''def search_case_by_number(conn, case_no):
    cursor = conn.cursor()
    # ✅ ปลอดภัยด้วย Parameterized Query (Prepared Statement):
    query = "SELECT * FROM cases WHERE case_number = ?"
    cursor.execute(query, (case_no,))
    return cursor.fetchall()
''',
        'security_principle': '''
### 🛡️ หลักการความมั่นคงปลอดภัย (Defense Principle):
1. **ห้ามนำตัวแปรจาก User Input มาต่อสตริง SQL โดยตรงเด็ดขาด**
2. ใช้ **Parameterized Queries (Prepared Statements)** เสมอ ตัว Driver ของฐานข้อมูลจะส่ง Data แยกต่างหากจาก Query Structure ทำให้ตัวแปรถูกมองเป็น String Data เท่านั้น ไม่สามารถสั่งรัน SQL Command เพิ่มเติมได้
3. สำหรับ SQLite ใช้ placeholder `?` ส่วน PostgreSQL ใช้ `%s` หรือ `$1`
'''
    },
    {
        'id': 'sec_2',
        'title': 'โจทย์ที่ 2: ช่องโหว่ Stored Cross-Site Scripting (XSS) ในหน้าเว็บร้องขอความเป็นธรรม',
        'vulnerability_type': 'OWASP Top 10 - A03:2021-Injection (XSS)',
        'description': 'ฟังก์ชันแสดงผลความคิดเห็นของประชาชนด้านล่าง นำข้อความจากฐานข้อมูลมาแทรกใน HTML โดยตรงโดยไม่มีการ Escape ทำให้ผู้ไม่ประสงค์ดีสามารถฝัง JavaScript เช่น `<script>stealCookie()</script>` จงแก้ไขฟังก์ชันให้ทำการ Sanitize / Escape ข้อมูลอย่างถูกต้อง',
        'vulnerable_code': '''def render_citizen_comment(author_name, comment_text):
    # ❌ นำ comment_text ที่มีสคริปต์มาแสดงใน HTML โดยตรง
    html_card = f"""
    <div class="comment-box">
        <h4>{author_name}</h4>
        <p>{comment_text}</p>
    </div>
    """
    return html_card
''',
        'starter_code': '''import html

def render_citizen_comment(author_name, comment_text):
    # ✍️ ทำการ Sanitize / Escape ข้อมูลก่อนแสดงผลใน HTML:
    safe_name = html.escape(author_name)
    safe_text = html.escape(comment_text)
    html_card = f"""
    <div class="comment-box">
        <h4>{safe_name}</h4>
        <p>{safe_text}</p>
    </div>
    """
    return html_card
''',
        'secure_solution': '''import html

def render_citizen_comment(author_name, comment_text):
    # ✅ ปลอดภัยด้วยการ Escape HTML Characters พิเศษ (&, <, >, ", '):
    safe_name = html.escape(author_name, quote=True)
    safe_text = html.escape(comment_text, quote=True)
    html_card = f"""
    <div class="comment-box">
        <h4>{safe_name}</h4>
        <p>{safe_text}</p>
    </div>
    """
    return html_card
''',
        'security_principle': '''
### 🛡️ หลักการความมั่นคงปลอดภัย (Defense Principle):
1. **Context-aware Output Encoding:** ข้อมูลใดๆ ที่มาจาก User Input หรือฐานข้อมูล เมื่อจะนำไปแสดงใน HTML ต้องแปลงอักขระพิเศษ (`<`, `>`, `&`, `"`, `'`) เป็น HTML Entities เสมอ (เช่น `<` เป็น `&lt;`)
2. ใน Python ใช้โมดูลมาตรฐาน `import html` แล้วเรียก `html.escape(text, quote=True)`
3. ในระดับ Web Framework เช่น Django, Jinja2, React จะมี Auto-escaping ให้ แต่ต้องระวังไม่ใช้ฟังก์ชันเสี่ยง เช่น `safe` filter หรือ `dangerouslySetInnerHTML`
'''
    },
    {
        'id': 'sec_3',
        'title': 'โจทย์ที่ 3: ช่องโหว่ Broken Authentication จากการใช้ MD5 แฮชรหัสผ่าน',
        'vulnerability_type': 'OWASP Top 10 - A02:2021-Cryptographic Failures',
        'description': 'ฟังก์ชันจัดเก็บรหัสผ่านด้านล่างใช้ MD5 แบบไม่มี Salt ซึ่งเปราะบางต่อการโจมตีด้วย Rainbow Table และ Brute Force อย่างมาก จงเขียนโค้ดแก้ไขให้ใช้ PBKDF2 พร้อม Salt แบบสุ่มที่ปลอดภัย',
        'vulnerable_code': '''import hashlib

def hash_officer_password(password):
    # ❌ MD5 อ่อนแอมากและไม่มี Salt ป้องกัน Rainbow Table
    return hashlib.md5(password.encode('utf-8')).hexdigest()
''',
        'starter_code': '''import hashlib
import os

def hash_officer_password(password, salt=None):
    # ✍️ เขียนโค้ดแฮชรหัสผ่านที่ปลอดภัยด้วย PBKDF2-HMAC-SHA256 พร้อม Salt:
    if salt is None:
        salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ":" + key.hex()
''',
        'secure_solution': '''import hashlib
import os

def hash_officer_password(password, salt=None):
    # ✅ ปลอดภัยด้วย Key Derivation Function (PBKDF2) + Salt สุ่ม 16 bytes:
    if salt is None:
        salt = os.urandom(16) # สุ่ม Salt ขนาด 16 ไบต์ป้องกัน Rainbow Table
    # ทำรอบการแฮช 100,000 รอบ ชะลอการทำ Brute-force
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ":" + key.hex()
''',
        'security_principle': '''
### 🛡️ หลักการความมั่นคงปลอดภัย (Defense Principle):
1. **ห้ามใช้ MD5, SHA-1 หรือ Fast Hashing ในการจัดเก็บรหัสผ่าน** เนื่องจากสามารถประมวลผลได้หลายพันล้านครั้งต่อวินาทีด้วย GPU
2. ต้องใช้ **Slow / Adaptive Hashing Algorithm** เช่น Argon2, bcrypt, scrypt หรือ PBKDF2-HMAC-SHA256
3. ต้องมี **Cryptographic Salt สุ่ม** ไม่ซ้ำกันในแต่ละผู้ใช้งาน เพื่อป้องกันการใช้ Rainbow Table โจมตี
'''
    }
]

# ==============================================================================
# 4. MAIN VIEW RENDERER
# ==============================================================================

def render_subjective_view():
    st.markdown('''
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #1e40af 100%); padding: 24px 28px; border-radius: 16px; color: white; margin-bottom: 24px; border: 1px solid #d4af37; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);">
        <h2 style="margin: 0 0 8px 0; color: #fef08a;">✍️ สนามฝึกข้อเขียนอัตนัย (คะแนนเต็ม 100 คะแนน)</h2>
        <p style="margin: 0; color: #e2e8f0; font-size: 1rem;">
            หลักสูตรปฏิบัติการสำหรับตำแหน่งนักวิชาการคอมพิวเตอร์ปฏิบัติการ สำนักงานอัยการสูงสุด: ฝึกเขียนคำสั่ง SQL รันจริง, ออกแบบ ER-Diagram แสดงผลสด และแก้ไขโค้ดปิดช่องโหว่ความมั่นคงปลอดภัย
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    tab_sql, tab_erd, tab_sec = st.tabs([
        "💻 1. SQL Lab (รันคิวรีจริง)",
        "📊 2. ER-Diagram & System Design",
        "🛡️ 3. Code & Security Fix"
    ])
    
    # --------------------------------------------------------------------------
    # TAB 1: SQL LAB
    # --------------------------------------------------------------------------
    with tab_sql:
        st.markdown("### 💻 SQL Lab: ห้องปฏิบัติการทดสอบคำสั่ง SQL กับฐานข้อมูลคดีความเสมือนจริง")
        st.info("💡 คำสั่ง SQL ของคุณจะถูกประมวลผลกับฐานข้อมูล SQLite ในหน่วยความจำที่มีโครงสร้างและข้อมูลจำลองของสำนักงานอัยการสูงสุดจริง")
        
        # Schema Expander
        with st.expander("🔍 ดูโครงสร้างตารางและข้อมูลตัวอย่างในฐานข้อมูล (Database Schema)", expanded=False):
            sc_c1, sc_c2 = st.columns(2)
            with sc_c1:
                st.markdown("**ตาราง `cases` (สำนวนคดี):**")
                st.caption("คอลัมน์: `case_id`, `case_number`, `title`, `charge`, `court_id`, `attorney_id`, `status`, `filing_date`, `lawsuit_amount`")
                st.markdown("**ตาราง `attorneys` (พนักงานอัยการ):**")
                st.caption("คอลัมน์: `attorney_id`, `name`, `position`, `department`, `active_status`")
            with sc_c2:
                st.markdown("**ตาราง `courts` (ศาล):**")
                st.caption("คอลัมน์: `court_id`, `court_name`, `court_type`")
                st.markdown("**ตาราง `evidence_items` (พยานหลักฐาน):**")
                st.caption("คอลัมน์: `evidence_id`, `case_id`, `item_name`, `item_type`, `storage_location`, `is_digital`")
        
        # Challenge Selector
        selected_sql_idx = st.selectbox(
            "🎯 เลือกโจทย์ข้อสอบ SQL ที่ต้องการฝึก:",
            options=range(len(SQL_CHALLENGES)),
            format_func=lambda i: SQL_CHALLENGES[i]['title'],
            key="sql_challenge_selector"
        )
        challenge = SQL_CHALLENGES[selected_sql_idx]
        
        st.markdown(f"**รายละเอียดโจทย์:** {challenge['description']}")
        
        # User input area
        user_sql = st.text_area(
            "✍️ พิมพ์คำสั่ง SQL ของคุณที่นี่:",
            value=st.session_state.get(f"sql_input_{challenge['id']}", "SELECT * FROM cases LIMIT 5;"),
            height=140,
            key=f"sql_text_{challenge['id']}"
        )
        
        btn_run_c1, btn_run_c2 = st.columns([1.5, 2.5])
        with btn_run_c1:
            run_clicked = st.button("▶️ รันทดสอบคำสั่ง SQL", type="primary", use_container_width=True)
            
        with btn_run_c2:
            show_sol = st.checkbox("💡 ดูเฉลยแนวทางคำตอบและคำอธิบาย SQL", key=f"sql_sol_toggle_{challenge['id']}")
            
        if run_clicked:
            conn = create_oag_sample_db()
            try:
                # Run user query
                user_df = pd.read_sql_query(user_sql, conn)
                # Run solution query
                sol_df = pd.read_sql_query(challenge['solution_sql'], conn)
                
                st.markdown("#### 📊 ผลลัพธ์จากการรันคำสั่งของคุณ:")
                st.dataframe(user_df, use_container_width=True)
                
                # Compare shapes and data
                is_match = False
                if len(user_df) == len(sol_df) and len(user_df.columns) == len(sol_df.columns):
                    try:
                        # Check values ignoring column names case
                        norm_user = user_df.values.tolist()
                        norm_sol = sol_df.values.tolist()
                        is_match = (norm_user == norm_sol)
                    except Exception:
                        pass
                        
                if is_match:
                    st.success("🎉 ถูกต้องสมบูรณ์! ผลลัพธ์ตรงตามเกณฑ์ที่โจทย์กำหนดทุกประการ")
                else:
                    st.warning("⚠️ คำสั่ง SQL ทำงานได้ แต่ผลลัพธ์ (จำนวนแถวหรือคอลัมน์) ยังไม่ตรงกับเฉลยต้นแบบ ลองตรวจสอบเงื่อนไข WHERE หรือ JOIN อีกครั้ง")
                    with st.expander("👀 ดูตารางผลลัพธ์ที่ถูกต้องตามเฉลย:", expanded=False):
                        st.dataframe(sol_df, use_container_width=True)
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาดทางไวยากรณ์ SQL (SQL Syntax Error): {str(e)}")
            finally:
                conn.close()
                
        if show_sol:
            st.markdown("---")
            st.markdown("#### 💡 เฉลยแนวทางคำตอบ (Model Solution):")
            st.code(challenge['solution_sql'], language='sql')
            st.markdown(f"**คำอธิบายเทคนิค:** {challenge['hint']}")

    # --------------------------------------------------------------------------
    # TAB 2: ER-DIAGRAM & SYSTEM DESIGN
    # --------------------------------------------------------------------------
    with tab_erd:
        st.markdown("### 📊 ER-Diagram & System Design: ออกแบบฐานข้อมูลระบบงานอัยการ")
        st.info("💡 ฝึกเขียนแผนภาพความสัมพันธ์ของข้อมูล (Entity-Relationship Diagram) ด้วยไวยากรณ์ Mermaid.js พร้อมแสดงผลพรีวิวแบบเรียลไทม์")
        
        selected_erd_idx = st.selectbox(
            "🎯 เลือกโจทย์ออกแบบระบบที่ต้องการฝึก:",
            options=range(len(ERD_CHALLENGES)),
            format_func=lambda i: ERD_CHALLENGES[i]['title'],
            key="erd_challenge_selector"
        )
        erd_item = ERD_CHALLENGES[selected_erd_idx]
        
        st.markdown(erd_item['scenario'])
        
        erd_code = st.text_area(
            "✍️ โค้ด Mermaid ER-Diagram ของคุณ (แก้ไขแล้วผลจะพรีวิวด้านล่างทันที):",
            value=st.session_state.get(f"erd_code_{erd_item['id']}", erd_item['default_code']),
            height=200,
            key=f"erd_text_{erd_item['id']}"
        )
        
        st.markdown("#### 🖼️ ผลการแสดงผลแผนภาพ (Live Mermaid Preview):")
        
        # Render Mermaid via HTML component
        mermaid_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
          <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
          </script>
        </head>
        <body style="background: transparent; margin: 0; padding: 10px; font-family: sans-serif;">
          <pre class="mermaid" style="background: white; padding: 16px; border-radius: 8px; border: 1px solid #cbd5e1;">
{erd_code}
          </pre>
        </body>
        </html>
        '''
        components.html(mermaid_html, height=380, scrolling=True)
        
        with st.expander("💡 ดูเฉลยต้นแบบแผนภาพ & Data Dictionary:", expanded=False):
            st.markdown("#### แผนภาพเฉลยต้นแบบ (Model ERD):")
            st.code(erd_item['model_solution_mermaid'], language='mermaid')
            
            st.markdown("#### ตารางพจนานุกรมข้อมูล (Data Dictionary):")
            df_dict = pd.DataFrame(erd_item['data_dictionary'])
            st.table(df_dict)

    # --------------------------------------------------------------------------
    # TAB 3: CODE & SECURITY FIX
    # --------------------------------------------------------------------------
    with tab_sec:
        st.markdown("### 🛡️ Code & Security Fix: แล็บแก้ไขบั๊กและอุดช่องโหว่ความมั่นคงปลอดภัย (OWASP)")
        st.info("💡 ข้อสอบอัตนัยมักให้โค้ดที่มีข้อผิดพลาดหรือมีช่องโหว่ความปลอดภัยมา แล้วให้ผู้สอบเขียนโค้ดที่ถูกต้องและปลอดภัย (Secure Coding)")
        
        selected_sec_idx = st.selectbox(
            "🎯 เลือกโจทย์ความปลอดภัยที่ต้องการฝึก:",
            options=range(len(SECURITY_CHALLENGES)),
            format_func=lambda i: SECURITY_CHALLENGES[i]['title'],
            key="sec_challenge_selector"
        )
        sec_item = SECURITY_CHALLENGES[selected_sec_idx]
        
        st.markdown(f"**ประเภทช่องโหว่:** `{sec_item['vulnerability_type']}`")
        st.markdown(sec_item['description'])
        
        col_code1, col_code2 = st.columns(2)
        with col_code1:
            st.markdown("❌ **โค้ดเดิมที่มีช่องโหว่ (Vulnerable Code):**")
            st.code(sec_item['vulnerable_code'], language='python')
            
        with col_code2:
            st.markdown("✍️ **เขียนโค้ดที่ได้รับการแก้ไขให้ปลอดภัย (Your Fix):**")
            user_fix_code = st.text_area(
                "พิมพ์โค้ดแก้ไข:",
                value=st.session_state.get(f"user_fix_{sec_item['id']}", sec_item['starter_code']),
                height=180,
                key=f"sec_input_{sec_item['id']}",
                label_visibility="collapsed"
            )
            
        sec_c1, sec_c2 = st.columns([1.5, 2.5])
        with sec_c1:
            check_sec = st.button("🔍 ตรวจสอบคำตอบของคุณ", type="primary", key=f"btn_check_sec_{sec_item['id']}", use_container_width=True)
        with sec_c2:
            show_sec_sol = st.checkbox("💡 ดูเฉลยโค้ดที่ปลอดภัยและหลักการ OWASP", key=f"sec_sol_toggle_{sec_item['id']}")
            
        if check_sec:
            code_text = user_fix_code.lower()
            passed_checks = False
            
            if sec_item['id'] == 'sec_1':
                # Check for parameterized query
                if ('?' in user_fix_code or '%s' in user_fix_code) and ('case_no' in user_fix_code) and ('f"' not in user_fix_code and "f'" not in user_fix_code):
                    passed_checks = True
            elif sec_item['id'] == 'sec_2':
                # Check for html.escape
                if 'html.escape' in user_fix_code:
                    passed_checks = True
            elif sec_item['id'] == 'sec_3':
                # Check for pbkdf2 or salt
                if ('pbkdf2' in code_text or 'salt' in code_text) and 'md5' not in code_text:
                    passed_checks = True
                    
            if passed_checks:
                st.success("✅ ยอดเยี่ยมมาก! โค้ดของคุณใช้แนวทางความปลอดภัยที่ถูกต้อง (Secure Coding) ตามมาตรฐาน OWASP")
            else:
                st.warning("⚠️ โค้ดยังมีจุดที่อาจยังไม่ปลอดภัย ตรวจสอบการแทนที่ด้วย Parameter หรือการใช้ฟังก์ชัน Escape อีกครั้ง")
                
        if show_sec_sol:
            st.markdown("---")
            st.markdown("#### ✅ โค้ดเฉลยต้นแบบที่ปลอดภัย (Secure Code):")
            st.code(sec_item['secure_solution'], language='python')
            st.markdown(sec_item['security_principle'])
