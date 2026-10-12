import json
import re
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    submissions = db.relationship('Submission', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'


class Level(db.Model):
    __tablename__ = 'levels'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # 'A1', 'A2', 'B1', 'B2', 'C1', 'IELTS'
    name = db.Column(db.String(100), nullable=False)              # 'Trình độ A1 - Căn bản'
    description = db.Column(db.Text, nullable=True)
    badge_color = db.Column(db.String(30), default='blue')        # 'blue', 'green', 'amber', 'purple', 'rose'
    icon_name = db.Column(db.String(50), default='book-open')
    order_num = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tests = db.relationship('Test', backref='level', lazy=True, cascade='all, delete-orphan')

    @property
    def active_tests_count(self):
        return len([t for t in self.tests if t.is_active])


class Test(db.Model):
    __tablename__ = 'tests'

    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, db.ForeignKey('levels.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    ppt_filename = db.Column(db.String(255), nullable=True)      # Original filename
    ppt_filepath = db.Column(db.String(500), nullable=True)      # Relative or abs path to ppt file
    slides_folder = db.Column(db.String(500), nullable=True)     # Relative folder under static/ containing slide images
    
    # Audio Listening support
    audio_filename = db.Column(db.String(255), nullable=True)    # Original audio filename (.mp3, .wav)
    audio_filepath = db.Column(db.String(500), nullable=True)    # Relative path under static/ to audio file
    
    total_slides = db.Column(db.Integer, default=0)
    time_limit_minutes = db.Column(db.Integer, default=15)       # 0 = unlimited
    total_questions = db.Column(db.Integer, default=10)
    pass_percentage = db.Column(db.Integer, default=50)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship('Question', backref='test', lazy=True, cascade='all, delete-orphan', order_by='Question.question_number')
    submissions = db.relationship('Submission', backref='test', lazy=True, cascade='all, delete-orphan')


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False)
    question_number = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=True)            # Prompt or question detail
    question_type = db.Column(db.String(30), default='single_choice') # 'single_choice', 'text_input'
    options_json = db.Column(db.Text, default='["A", "B", "C", "D"]') # Available choices
    correct_answer = db.Column(db.String(255), nullable=False)   # E.g. "A" or "elephant" or "centre / center"
    slide_number = db.Column(db.Integer, default=1)              # Associated PPT slide number
    audio_file = db.Column(db.String(500), nullable=True)        # Optional question-specific audio clip
    points = db.Column(db.Float, default=1.0)
    explanation = db.Column(db.Text, nullable=True)

    @property
    def options(self):
        try:
            return json.loads(self.options_json) if self.options_json else ["A", "B", "C", "D"]
        except Exception:
            return ["A", "B", "C", "D"]

    def check_user_answer(self, user_ans):
        """
        Kiểm tra câu trả lời của học viên:
        - Hỗ trợ trắc nghiệm A/B/C/D
        - Hỗ trợ điền từ vựng (chính xác không phân biệt hoa/thường)
        - Hỗ trợ viết 1 câu (chuẩn hóa khoảng trắng, dấu câu cuối câu)
        - Hỗ trợ nhiều đáp án hợp lệ cách nhau bởi '/' hoặc '|' (ví dụ: 'center / centre')
        """
        if not user_ans or not user_ans.strip():
            return False, 0.0

        user_clean = user_ans.strip()

        # 1. Trắc nghiệm A, B, C, D đơn giản
        if self.question_type == 'single_choice' and len(self.correct_answer.strip()) <= 2:
            if user_clean.upper() == self.correct_answer.strip().upper():
                return True, self.points
            return False, 0.0

        # 2. Điền từ vựng hoặc viết 1 câu
        def normalize(s):
            if not s:
                return ''
            t = s.strip().lower()
            t = re.sub(r'\s+', ' ', t)
            t = re.sub(r'[\.\?!;]+$', '', t).strip()
            return t

        user_norm = normalize(user_clean)
        # Các đáp án khả dĩ phân cách bằng / hoặc |
        candidates = [c.strip() for c in re.split(r'[/|]', self.correct_answer) if c.strip()]
        for cand in candidates:
            if user_norm == normalize(cand):
                return True, self.points

        return False, 0.0


class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    student_name = db.Column(db.String(120), nullable=False, default='Thí sinh')
    student_email = db.Column(db.String(120), nullable=True)
    student_phone = db.Column(db.String(50), nullable=True)

    total_questions = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    wrong_count = db.Column(db.Integer, default=0)
    unanswered_count = db.Column(db.Integer, default=0)
    score = db.Column(db.Float, default=0.0)
    percentage = db.Column(db.Float, default=0.0)
    is_passed = db.Column(db.Boolean, default=False)
    time_taken_seconds = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    answers = db.relationship('SubmissionAnswer', backref='submission', lazy=True, cascade='all, delete-orphan', order_by='SubmissionAnswer.question_number')

    @property
    def formatted_time(self):
        minutes = self.time_taken_seconds // 60
        seconds = self.time_taken_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"


class SubmissionAnswer(db.Model):
    __tablename__ = 'submission_answers'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=True)
    question_number = db.Column(db.Integer, nullable=False)
    user_answer = db.Column(db.String(500), nullable=True)
    correct_answer = db.Column(db.String(500), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    slide_number = db.Column(db.Integer, default=1)
    points_awarded = db.Column(db.Float, default=0.0)
