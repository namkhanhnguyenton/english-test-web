import os
import re
import uuid
import random
import logging
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, abort
)
from werkzeug.utils import secure_filename
from models import db, User, Level, Test, Question, Submission, SubmissionAnswer
from ppt_converter import convert_ppt_to_slides

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vietnam-english-test-secret-key-2026-xyz'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.root_path, 'english_test.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 120 * 1024 * 1024  # 120 MB max upload for PPT + MP3
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'tests')

db.init_app(app)

ALLOWED_PPT_EXTENSIONS = {'ppt', 'pptx', 'pps', 'ppsx'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'aac'}

def allowed_ppt_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_PPT_EXTENSIONS

def allowed_audio_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id') or session.get('role') not in ('admin', 'teacher'):
            flash('Vui lòng đăng nhập với tài khoản Quản trị viên hoặc Giáo viên.', 'warning')
            return redirect(url_for('admin_login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

# Đồng nhất admin_required để cho phép cả Admin lẫn Giáo viên quản lý đề thi và bài làm
admin_required = staff_required

def admin_only_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('admin_login', next=request.path))
        if session.get('role') != 'admin':
            flash('Chức năng này chỉ dành riêng cho Quản trị viên tối cao (Admin).', 'danger')
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def parse_answers_string(bulk_text, total_slides=1):
    """
    Phân tích chuỗi đáp án linh hoạt:
    - Hỗ trợ trắc nghiệm (A, B, C, D)
    - Hỗ trợ điền từ vựng (ví dụ: 'apple', 'difficult')
    - Hỗ trợ viết 1 câu (ví dụ: 'She goes to school every day.')
    - Hỗ trợ nhiều đáp án tương đương (ví dụ: 'center / centre')
    - Hỗ trợ nhiều dòng hoặc định dạng 1. A, 2. B, 1A 2B...
    """
    questions = []
    lines = [line.strip() for line in bulk_text.strip().splitlines() if line.strip()]

    line_pattern = re.compile(r'^(\d+)[\.\s:\-]+(.*)$')
    has_numbered_lines = any(line_pattern.match(l) for l in lines)

    if len(lines) > 1 and has_numbered_lines:
        for idx, line in enumerate(lines, start=1):
            m = line_pattern.match(line)
            if m:
                num = int(m.group(1))
                ans = m.group(2).strip()
            else:
                num = idx
                ans = line.strip()
            
            # Tự động nhận diện loại câu hỏi
            is_single_mcq = len(ans) <= 2 and ans.isalpha()
            q_type = 'single_choice' if is_single_mcq else 'text_input'
            questions.append({
                'num': num,
                'ans': ans.upper() if is_single_mcq else ans,
                'type': q_type,
                'slide': min(num + 1, total_slides) if total_slides > 1 else 1,
                'exp': ''
            })
    elif len(lines) > 1:
        # Mỗi dòng là 1 đáp án
        for idx, line in enumerate(lines, start=1):
            ans = line.strip()
            is_single_mcq = len(ans) <= 2 and ans.isalpha()
            q_type = 'single_choice' if is_single_mcq else 'text_input'
            questions.append({
                'num': idx,
                'ans': ans.upper() if is_single_mcq else ans,
                'type': q_type,
                'slide': min(idx + 1, total_slides) if total_slides > 1 else 1,
                'exp': ''
            })
    else:
        # Chuỗi trên 1 dòng duy nhất: '1A 2B 3C' hoặc '1: apple, 2: banana'
        bulk = lines[0] if lines else ''
        # Thử tách theo '1:', '2.'
        parts = re.split(r'(\d+)[\.\s:\-]+', bulk)
        if len(parts) > 1 and parts[1].isdigit():
            i = 1
            while i < len(parts):
                num = int(parts[i])
                ans = parts[i+1].strip().rstrip(',; ') if i+1 < len(parts) else ''
                is_single_mcq = len(ans) <= 2 and ans.isalpha()
                q_type = 'single_choice' if is_single_mcq else 'text_input'
                questions.append({
                    'num': num,
                    'ans': ans.upper() if is_single_mcq else ans,
                    'type': q_type,
                    'slide': min(num + 1, total_slides) if total_slides > 1 else 1,
                    'exp': ''
                })
                i += 2
        else:
            # Fallback tách chữ cái đơn lẻ
            tokens = re.findall(r'(\d+)?([A-Za-z]+)', bulk)
            for idx, (n_str, tok) in enumerate(tokens, start=1):
                num = int(n_str) if n_str else idx
                is_single_mcq = len(tok) <= 2 and tok.isalpha()
                q_type = 'single_choice' if is_single_mcq else 'text_input'
                questions.append({
                    'num': num,
                    'ans': tok.upper() if is_single_mcq else tok,
                    'type': q_type,
                    'slide': min(num + 1, total_slides) if total_slides > 1 else 1,
                    'exp': ''
                })

    return questions


@app.context_processor
def inject_globals():
    levels = Level.query.filter_by(is_active=True).order_by(Level.order_num).all()
    current_user = None
    if session.get('user_id'):
        current_user = User.query.get(session.get('user_id'))
    return {
        'all_levels': levels,
        'current_user': current_user,
        'is_admin': session.get('role') == 'admin',
        'is_teacher': session.get('role') == 'teacher',
        'is_staff': session.get('role') in ('admin', 'teacher'),
        'candidate_name': session.get('student_name'),
        'candidate_phone': session.get('student_phone'),
        'candidate_email': session.get('student_email')
    }


# ==========================================
# PUBLIC & USER ROUTES
# ==========================================

@app.route('/')
def home():
    """Trang chủ: Chọn trình độ test tiếng Anh."""
    levels = Level.query.filter_by(is_active=True).order_by(Level.order_num).all()
    total_tests = Test.query.filter_by(is_active=True).count()
    total_submissions = Submission.query.count()
    
    return render_template(
        'home.html',
        levels=levels,
        total_tests=total_tests,
        total_submissions=total_submissions
    )


@app.route('/level/<int:level_id>/random-test')
def random_test_by_level(level_id):
    """
    Khi user chọn trình độ: Tự động chọn 1 đề ngẫu nhiên thuộc trình độ đó.
    """
    level = Level.query.get_or_404(level_id)
    active_tests = Test.query.filter_by(level_id=level.id, is_active=True).all()

    if not active_tests:
        flash(f'Trình độ "{level.name}" hiện chưa có đề thi nào được kích hoạt. Vui lòng chọn trình độ khác hoặc liên hệ Admin.', 'info')
        return redirect(url_for('home'))

    # Chọn ngẫu nhiên 1 đề thi
    selected_test = random.choice(active_tests)
    return redirect(url_for('take_test', test_id=selected_test.id))


@app.route('/test/<int:test_id>')
def take_test(test_id):
    """
    Trang làm bài thi: Hiển thị slide PPT + audio nghe MP3 (nếu có) + phiếu trả lời.
    """
    test = Test.query.get_or_404(test_id)
    if not test.is_active and session.get('role') != 'admin':
        flash('Đề thi này hiện đang tạm ẩn.', 'warning')
        return redirect(url_for('home'))

    # Lấy danh sách ảnh slide
    slides = []
    if test.slides_folder:
        folder_path = os.path.join(app.root_path, 'static', test.slides_folder)
        if os.path.exists(folder_path):
            files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            def get_num(s):
                nums = re.findall(r'\d+', s)
                return int(nums[0]) if nums else 0
            files.sort(key=get_num)
            slides = [f"{test.slides_folder}/{f}".replace('\\', '/') for f in files]

    questions = test.questions
    return render_template('test_taking.html', test=test, slides=slides, questions=questions)


@app.route('/api/candidate-info', methods=['POST'])
def save_candidate_info():
    """Lưu thông tin thí sinh (Tên, SĐT, Email) vào session trước khi làm bài."""
    name = request.form.get('student_name', '').strip()
    phone = request.form.get('student_phone', '').strip()
    email = request.form.get('student_email', '').strip()

    if name:
        session['student_name'] = name
    if phone:
        session['student_phone'] = phone
    if email:
        session['student_email'] = email

    next_url = request.form.get('next_url')
    if next_url:
        return redirect(next_url)
    return jsonify({
        'status': 'success',
        'student_name': session.get('student_name'),
        'student_phone': session.get('student_phone'),
        'student_email': session.get('student_email')
    })


@app.route('/test/<int:test_id>/submit', methods=['POST'])
def submit_test(test_id):
    """
    Xử lý nộp bài thi của user: chấm điểm và lưu kết quả.
    Lưu đầy đủ Tên, SĐT, Email của thí sinh.
    """
    test = Test.query.get_or_404(test_id)
    
    student_name = request.form.get('student_name', '').strip() or session.get('student_name') or 'Học viên ẩn danh'
    student_phone = request.form.get('student_phone', '').strip() or session.get('student_phone') or None
    student_email = request.form.get('student_email', '').strip() or session.get('student_email') or None
    time_taken_seconds = int(request.form.get('time_taken_seconds', 0))

    # Lưu lại vào session để học viên không phải nhập lại lần sau
    session['student_name'] = student_name
    if student_phone:
        session['student_phone'] = student_phone
    if student_email:
        session['student_email'] = student_email

    questions = test.questions
    correct_count = 0
    wrong_count = 0
    unanswered_count = 0
    total_score = 0.0

    submission = Submission(
        test_id=test.id,
        user_id=session.get('user_id'),
        student_name=student_name,
        student_phone=student_phone,
        student_email=student_email,
        total_questions=len(questions),
        time_taken_seconds=time_taken_seconds
    )
    db.session.add(submission)
    db.session.flush()

    for q in questions:
        user_ans = request.form.get(f'question_{q.id}', '').strip()
        is_correct, points = q.check_user_answer(user_ans)

        if not user_ans:
            unanswered_count += 1
        elif is_correct:
            correct_count += 1
            total_score += points
        else:
            wrong_count += 1

        ans_record = SubmissionAnswer(
            submission_id=submission.id,
            question_id=q.id,
            question_number=q.question_number,
            user_answer=user_ans if user_ans else '(Chưa chọn/điền)',
            correct_answer=q.correct_answer,
            is_correct=is_correct,
            slide_number=q.slide_number,
            points_awarded=points
        )
        db.session.add(ans_record)

    submission.correct_count = correct_count
    submission.wrong_count = wrong_count
    submission.unanswered_count = unanswered_count
    submission.score = round(total_score, 2)
    percentage = (correct_count / len(questions) * 100) if len(questions) > 0 else 0
    submission.percentage = round(percentage, 1)
    submission.is_passed = percentage >= test.pass_percentage

    db.session.commit()

    flash('Nộp bài thành công! Hãy xem kết quả chi tiết bên dưới.', 'success')
    return redirect(url_for('test_result', submission_id=submission.id))


@app.route('/test/result/<int:submission_id>')
def test_result(submission_id):
    """
    Trang hiển thị kết quả làm bài của user: số lượng câu đúng, điểm số, đánh giá.
    """
    submission = Submission.query.get_or_404(submission_id)
    test = submission.test
    answers = submission.answers

    q_map = {q.id: q for q in test.questions}

    return render_template(
        'test_result.html',
        submission=submission,
        test=test,
        answers=answers,
        q_map=q_map
    )


# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@app.route('/web/admin')
def web_admin_alias():
    """Hỗ trợ đường dẫn bí mật web/admin để vào thẳng quản trị."""
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('role') in ('admin', 'teacher'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.can_manage():
            session['user_id'] = user.id
            session['username'] = user.username
            session['full_name'] = user.full_name
            session['role'] = user.role
            role_text = "Quản trị viên (Admin)" if user.is_admin() else "Giáo viên"
            flash(f'Chào mừng {role_text}: {user.full_name}!', 'success')
            next_url = request.args.get('next') or url_for('admin_dashboard')
            return redirect(next_url)
        else:
            flash('Tên đăng nhập hoặc mật khẩu không chính xác (hoặc tài khoản không có quyền truy cập).', 'danger')

    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Đã đăng xuất thành công.', 'info')
    return redirect(url_for('home'))


# ==========================================
# ADMIN & TEACHER DASHBOARD & ROUTES
# ==========================================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Trang thống kê tổng quan dành cho Quản trị viên và Giáo viên."""
    total_levels = Level.query.count()
    total_tests = Test.query.count()
    total_questions = Question.query.count()
    total_submissions = Submission.query.count()
    total_teachers = User.query.filter_by(role='teacher').count()
    
    avg_score = 0
    if total_submissions > 0:
        submissions = Submission.query.all()
        avg_score = round(sum(s.percentage for s in submissions) / total_submissions, 1)

    recent_submissions = Submission.query.order_by(Submission.submitted_at.desc()).limit(10).all()
    tests = Test.query.order_by(Test.created_at.desc()).limit(6).all()

    return render_template(
        'admin/dashboard.html',
        total_levels=total_levels,
        total_tests=total_tests,
        total_questions=total_questions,
        total_submissions=total_submissions,
        total_teachers=total_teachers,
        avg_score=avg_score,
        recent_submissions=recent_submissions,
        tests=tests
    )


# ==========================================
# TEACHER MANAGEMENT (ADMIN EXCLUSIVE)
# ==========================================

@app.route('/admin/teachers', methods=['GET', 'POST'])
@admin_only_required
def admin_teachers():
    """Quản lý danh sách giáo viên: Xem và cấp tài khoản giáo viên mới (Chỉ Admin)."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not full_name or not password:
            flash('Vui lòng điền đầy đủ Tên đăng nhập, Họ tên và Mật khẩu.', 'danger')
        elif len(password) < 4:
            flash('Mật khẩu giáo viên phải có ít nhất 4 ký tự.', 'danger')
        elif User.query.filter_by(username=username).first():
            flash(f'Tên đăng nhập "{username}" đã tồn tại. Vui lòng chọn tên khác.', 'warning')
        else:
            teacher = User(
                username=username,
                full_name=full_name,
                email=email if email else None,
                role='teacher'
            )
            teacher.set_password(password)
            db.session.add(teacher)
            db.session.commit()
            flash(f'Đã cấp tài khoản Giáo viên mới thành công cho: {full_name} (@{username})!', 'success')
            return redirect(url_for('admin_teachers'))

    teachers = User.query.filter_by(role='teacher').order_by(User.created_at.desc()).all()
    return render_template('admin/teachers.html', teachers=teachers)


@app.route('/admin/teachers/<int:teacher_id>/change-password', methods=['POST'])
@admin_only_required
def admin_change_teacher_password(teacher_id):
    """Admin thay đổi mật khẩu cho giáo viên."""
    teacher = User.query.get_or_404(teacher_id)
    if teacher.role != 'teacher':
        flash('Chỉ có thể đổi mật khẩu cho tài khoản Giáo viên tại đây.', 'warning')
        return redirect(url_for('admin_teachers'))

    new_password = request.form.get('new_password', '').strip()
    if not new_password or len(new_password) < 4:
        flash('Mật khẩu mới phải có ít nhất 4 ký tự.', 'danger')
    else:
        teacher.set_password(new_password)
        db.session.commit()
        flash(f'Đã đổi mật khẩu thành công cho Giáo viên: {teacher.full_name} (@{teacher.username})!', 'success')

    return redirect(url_for('admin_teachers'))


@app.route('/admin/teachers/<int:teacher_id>/delete', methods=['POST'])
@admin_only_required
def admin_delete_teacher(teacher_id):
    """Admin xóa tài khoản giáo viên."""
    teacher = User.query.get_or_404(teacher_id)
    if teacher.id == session.get('user_id'):
        flash('Không thể tự xóa tài khoản của chính mình!', 'danger')
        return redirect(url_for('admin_teachers'))

    if teacher.role != 'teacher':
        flash('Không thể xóa tài khoản Quản trị viên tối cao.', 'danger')
        return redirect(url_for('admin_teachers'))

    teacher_name = teacher.full_name
    db.session.delete(teacher)
    db.session.commit()
    flash(f'Đã xóa tài khoản giáo viên: {teacher_name} thành công.', 'info')
    return redirect(url_for('admin_teachers'))


@app.route('/admin/change-password', methods=['GET', 'POST'])
@staff_required
def admin_change_password():
    """Đổi mật khẩu tài khoản hiện tại (Cả Admin và Giáo viên đều có thể tự đổi)."""
    user = User.query.get(session.get('user_id'))
    if not user:
        return redirect(url_for('admin_logout'))

    if request.method == 'POST':
        old_password = request.form.get('old_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not user.check_password(old_password):
            flash('Mật khẩu hiện tại không chính xác. Vui lòng kiểm tra lại.', 'danger')
        elif not new_password or len(new_password) < 4:
            flash('Mật khẩu mới phải có ít nhất 4 ký tự.', 'danger')
        elif new_password != confirm_password:
            flash('Xác nhận mật khẩu mới không trùng khớp.', 'danger')
        else:
            user.set_password(new_password)
            db.session.commit()
            flash('Đổi mật khẩu thành công! Vui lòng ghi nhớ mật khẩu mới của bạn.', 'success')
            return redirect(url_for('admin_dashboard'))

    return render_template('admin/change_password.html', user=user)


@app.route('/admin/levels', methods=['GET', 'POST'])
@admin_required
def admin_levels():
    """Quản lý danh sách trình độ tiếng Anh."""
    if request.method == 'POST':
        code = request.form.get('code', '').strip().upper()
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        badge_color = request.form.get('badge_color', 'blue')
        icon_name = request.form.get('icon_name', 'book-open')
        order_num = int(request.form.get('order_num', 1))

        if not code or not name:
            flash('Mã trình độ và tên trình độ không được để trống.', 'danger')
        elif Level.query.filter_by(code=code).first():
            flash(f'Mã trình độ "{code}" đã tồn tại.', 'warning')
        else:
            level = Level(
                code=code,
                name=name,
                description=description,
                badge_color=badge_color,
                icon_name=icon_name,
                order_num=order_num
            )
            db.session.add(level)
            db.session.commit()
            flash(f'Đã tạo mới trình độ "{name}" thành công!', 'success')
            return redirect(url_for('admin_levels'))

    levels = Level.query.order_by(Level.order_num).all()
    return render_template('admin/levels.html', levels=levels)


@app.route('/admin/levels/<int:level_id>/delete', methods=['POST'])
@admin_required
def admin_delete_level(level_id):
    level = Level.query.get_or_404(level_id)
    db.session.delete(level)
    db.session.commit()
    flash(f'Đã xóa trình độ "{level.name}"!', 'info')
    return redirect(url_for('admin_levels'))


@app.route('/admin/tests')
@admin_required
def admin_tests():
    """Danh sách tất cả đề thi và quản lý."""
    level_filter = request.args.get('level_id', type=int)
    query = Test.query
    if level_filter:
        query = query.filter_by(level_id=level_filter)
    tests = query.order_by(Test.created_at.desc()).all()
    levels = Level.query.order_by(Level.order_num).all()
    return render_template('admin/tests.html', tests=tests, levels=levels, current_level_id=level_filter)


@app.route('/admin/tests/new', methods=['GET', 'POST'])
@admin_required
def admin_new_test():
    """
    Thêm đề thi mới bằng file PPT/PPTX + File âm thanh MP3 (tùy chọn) + Bảng đáp án.
    Hỗ trợ cả trắc nghiệm A/B/C/D, từ vựng và câu văn.
    """
    levels = Level.query.filter_by(is_active=True).order_by(Level.order_num).all()

    if request.method == 'POST':
        level_id = request.form.get('level_id', type=int)
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        time_limit = int(request.form.get('time_limit_minutes', 15))
        pass_percentage = int(request.form.get('pass_percentage', 50))
        ppt_file = request.files.get('ppt_file')
        audio_file = request.files.get('audio_file')

        if not level_id or not title:
            flash('Vui lòng chọn trình độ và nhập tiêu đề đề thi.', 'danger')
            return render_template('admin/test_new.html', levels=levels)

        if not ppt_file or ppt_file.filename == '':
            flash('Vui lòng tải lên file đề thi PowerPoint (.pptx hoặc .ppt).', 'danger')
            return render_template('admin/test_new.html', levels=levels)

        if not allowed_ppt_file(ppt_file.filename):
            flash('Định dạng file không hợp lệ! Vui lòng chỉ tải lên file PowerPoint (.pptx, .ppt).', 'danger')
            return render_template('admin/test_new.html', levels=levels)

        # 1. Lưu file PPT vào thư mục riêng
        test_uuid = f"test_{uuid.uuid4().hex[:8]}"
        test_folder = os.path.join(app.config['UPLOAD_FOLDER'], test_uuid)
        slides_folder = os.path.join(test_folder, 'slides')
        os.makedirs(test_folder, exist_ok=True)
        os.makedirs(slides_folder, exist_ok=True)

        original_filename = secure_filename(ppt_file.filename)
        saved_ppt_path = os.path.join(test_folder, original_filename)
        ppt_file.save(saved_ppt_path)

        # 2. Chuyển đổi PPT sang ảnh slide
        try:
            slide_images, total_slides = convert_ppt_to_slides(saved_ppt_path, slides_folder)
        except Exception as e:
            logger.error(f"Error converting PPT: {e}")
            slide_images = []
            total_slides = 0

        rel_ppt_path = f"uploads/tests/{test_uuid}/{original_filename}"
        rel_slides_folder = f"uploads/tests/{test_uuid}/slides"

        # 3. Lưu file MP3 / Âm thanh nghe nếu có
        saved_audio_name = None
        rel_audio_path = None
        if audio_file and audio_file.filename != '' and allowed_audio_file(audio_file.filename):
            audio_subfolder = os.path.join(test_folder, 'audio')
            os.makedirs(audio_subfolder, exist_ok=True)
            saved_audio_name = secure_filename(audio_file.filename)
            audio_full_path = os.path.join(audio_subfolder, saved_audio_name)
            audio_file.save(audio_full_path)
            rel_audio_path = f"uploads/tests/{test_uuid}/audio/{saved_audio_name}"

        # 4. Phân tích bảng đáp án
        bulk_answers = request.form.get('bulk_answers', '').strip()
        question_count = int(request.form.get('question_count', 0))

        questions_list = []

        if bulk_answers:
            questions_list = parse_answers_string(bulk_answers, total_slides)
        elif question_count > 0:
            for i in range(1, question_count + 1):
                ans = request.form.get(f'q_ans_{i}', '').strip()
                q_type = request.form.get(f'q_type_{i}', 'single_choice').strip()
                slide = int(request.form.get(f'q_slide_{i}', 1))
                exp = request.form.get(f'q_exp_{i}', '').strip()
                if ans:
                    if q_type == 'single_choice' and len(ans) <= 2:
                        ans = ans.upper()
                    questions_list.append({
                        'num': i,
                        'ans': ans,
                        'type': q_type,
                        'slide': slide,
                        'exp': exp
                    })

        if not questions_list:
            flash('Chưa nhập bảng đáp án! Hệ thống tạm tạo 5 câu mẫu để bạn bổ sung.', 'warning')
            for i in range(1, 6):
                questions_list.append({'num': i, 'ans': 'A', 'type': 'single_choice', 'slide': min(i, max(1, total_slides)), 'exp': ''})

        # 5. Lưu Test vào CSDL
        new_test = Test(
            level_id=level_id,
            title=title,
            description=description,
            ppt_filename=original_filename,
            ppt_filepath=rel_ppt_path,
            slides_folder=rel_slides_folder,
            audio_filename=saved_audio_name,
            audio_filepath=rel_audio_path,
            total_slides=total_slides,
            time_limit_minutes=time_limit,
            total_questions=len(questions_list),
            pass_percentage=pass_percentage,
            is_active=True
        )
        db.session.add(new_test)
        db.session.commit()

        # 6. Lưu Questions
        for item in questions_list:
            q = Question(
                test_id=new_test.id,
                question_number=item['num'],
                question_text=f"Câu hỏi số {item['num']}",
                question_type=item.get('type', 'single_choice'),
                options_json='["A", "B", "C", "D"]',
                correct_answer=item['ans'],
                slide_number=item.get('slide', 1),
                points=1.0,
                explanation=item.get('exp', '')
            )
            db.session.add(q)

        db.session.commit()
        has_audio_msg = " kèm file nghe MP3" if rel_audio_path else ""
        flash(f'Tạo đề thi "{title}" thành công với {total_slides} slides, {len(questions_list)} câu hỏi{has_audio_msg}!', 'success')
        return redirect(url_for('admin_tests'))

    return render_template('admin/test_new.html', levels=levels)


@app.route('/admin/tests/<int:test_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_test(test_id):
    """Chỉnh sửa đề thi: Cập nhật PPT, MP3 âm thanh, bảng đáp án (từ vựng/câu văn/trắc nghiệm)."""
    test = Test.query.get_or_404(test_id)
    levels = Level.query.filter_by(is_active=True).order_by(Level.order_num).all()

    if request.method == 'POST':
        test.level_id = request.form.get('level_id', type=int)
        test.title = request.form.get('title', '').strip()
        test.description = request.form.get('description', '').strip()
        test.time_limit_minutes = int(request.form.get('time_limit_minutes', 15))
        test.pass_percentage = int(request.form.get('pass_percentage', 50))
        test.is_active = 'is_active' in request.form

        test_folder = os.path.dirname(os.path.join(app.root_path, 'static', test.ppt_filepath)) if test.ppt_filepath else os.path.join(app.config['UPLOAD_FOLDER'], f"test_{test.id}")
        os.makedirs(test_folder, exist_ok=True)

        # 1. Tải lên thay thế file PPT mới
        new_ppt = request.files.get('ppt_file')
        if new_ppt and new_ppt.filename != '' and allowed_ppt_file(new_ppt.filename):
            slides_folder = os.path.join(test_folder, 'slides')
            os.makedirs(slides_folder, exist_ok=True)

            original_filename = secure_filename(new_ppt.filename)
            saved_ppt_path = os.path.join(test_folder, original_filename)
            new_ppt.save(saved_ppt_path)

            slide_images, total_slides = convert_ppt_to_slides(saved_ppt_path, slides_folder)
            test.ppt_filename = original_filename
            test.ppt_filepath = os.path.relpath(saved_ppt_path, os.path.join(app.root_path, 'static')).replace('\\', '/')
            test.slides_folder = os.path.relpath(slides_folder, os.path.join(app.root_path, 'static')).replace('\\', '/')
            test.total_slides = total_slides

        # 2. Tải lên / Xóa file Âm thanh nghe (MP3)
        remove_audio = request.form.get('remove_audio') == '1'
        new_audio = request.files.get('audio_file')

        if remove_audio:
            test.audio_filename = None
            test.audio_filepath = None
        elif new_audio and new_audio.filename != '' and allowed_audio_file(new_audio.filename):
            audio_subfolder = os.path.join(test_folder, 'audio')
            os.makedirs(audio_subfolder, exist_ok=True)
            saved_audio_name = secure_filename(new_audio.filename)
            audio_full_path = os.path.join(audio_subfolder, saved_audio_name)
            new_audio.save(audio_full_path)
            test.audio_filename = saved_audio_name
            test.audio_filepath = f"uploads/tests/{os.path.basename(test_folder)}/audio/{saved_audio_name}"

        # 3. Cập nhật các câu hỏi
        for q in test.questions:
            ans = request.form.get(f'q_ans_{q.id}', '').strip()
            q_type = request.form.get(f'q_type_{q.id}', 'single_choice').strip()
            slide = request.form.get(f'q_slide_{q.id}', type=int)
            exp = request.form.get(f'q_exp_{q.id}', '').strip()
            
            if ans:
                if q_type == 'single_choice' and len(ans) <= 2:
                    ans = ans.upper()
                q.correct_answer = ans
            q.question_type = q_type
            if slide:
                q.slide_number = slide
            q.explanation = exp

        test.total_questions = len(test.questions)
        db.session.commit()
        flash('Đã lưu các thay đổi của đề thi thành công!', 'success')
        return redirect(url_for('admin_tests'))

    return render_template('admin/test_edit.html', test=test, levels=levels)


@app.route('/admin/tests/<int:test_id>/delete', methods=['POST'])
@admin_required
def admin_delete_test(test_id):
    """Xóa đề thi và tất cả dữ liệu liên quan."""
    test = Test.query.get_or_404(test_id)
    title = test.title
    db.session.delete(test)
    db.session.commit()
    flash(f'Đã xóa đề thi "{title}"!', 'info')
    return redirect(url_for('admin_tests'))


@app.route('/admin/submissions')
@admin_required
def admin_submissions():
    """Xem danh sách và chi tiết tất cả bài làm của user."""
    level_id = request.args.get('level_id', type=int)
    test_id = request.args.get('test_id', type=int)
    search_q = request.args.get('q', '').strip()

    query = Submission.query.join(Test)

    if level_id:
        query = query.filter(Test.level_id == level_id)
    if test_id:
        query = query.filter(Submission.test_id == test_id)
    if search_q:
        query = query.filter(
            db.or_(
                Submission.student_name.ilike(f'%{search_q}%'),
                Submission.student_phone.ilike(f'%{search_q}%'),
                Submission.student_email.ilike(f'%{search_q}%')
            )
        )

    submissions = query.order_by(Submission.submitted_at.desc()).all()
    levels = Level.query.order_by(Level.order_num).all()
    tests = Test.query.order_by(Test.title).all()

    return render_template(
        'admin/submissions.html',
        submissions=submissions,
        levels=levels,
        tests=tests,
        selected_level=level_id,
        selected_test=test_id,
        search_q=search_q
    )


@app.route('/admin/submissions/<int:submission_id>')
@admin_required
def admin_submission_detail(submission_id):
    """
    Xem chi tiết bài làm cụ thể của 1 user:
    Xem đáp án user đã chọn vs đáp án đúng của từng câu, kèm ảnh slide PPT tham chiếu.
    """
    submission = Submission.query.get_or_404(submission_id)
    test = submission.test
    answers = submission.answers

    slides = []
    if test.slides_folder:
        folder_path = os.path.join(app.root_path, 'static', test.slides_folder)
        if os.path.exists(folder_path):
            files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            files.sort(key=lambda s: int(re.findall(r'\d+', s)[0]) if re.findall(r'\d+', s) else 0)
            slides = [f"{test.slides_folder}/{f}".replace('\\', '/') for f in files]

    return render_template(
        'admin/submission_detail.html',
        submission=submission,
        test=test,
        answers=answers,
        slides=slides
    )


@app.route('/admin/submissions/<int:submission_id>/delete', methods=['POST'])
@admin_required
def admin_delete_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    db.session.delete(submission)
    db.session.commit()
    flash('Đã xóa bài làm của thí sinh!', 'info')
    return redirect(url_for('admin_submissions'))


if __name__ == '__main__':
    from seed_data import seed_database
    seed_database(app)
    app.run(host='0.0.0.0', port=5000, debug=True)
