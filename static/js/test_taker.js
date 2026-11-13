// Interactive Test Taker Logic (Slides, Audio, Answers, Timer)

let currentSlide = 1;
let totalSlides = typeof TOTAL_SLIDES !== 'undefined' ? TOTAL_SLIDES : 1;
let totalQuestions = typeof TOTAL_QUESTIONS !== 'undefined' ? TOTAL_QUESTIONS : 0;
let timeLimitMinutes = typeof TIME_LIMIT_MINUTES !== 'undefined' ? TIME_LIMIT_MINUTES : 15;

let timeRemainingSeconds = timeLimitMinutes * 60;
let timeElapsedSeconds = 0;
let timerInterval = null;
let isSubmitting = false;

document.addEventListener('DOMContentLoaded', () => {
    initSlideViewer();
    initKeyboardNav();
    initTimer();
    initAudioPlayer();
    updateAnsweredCount();
    initAntiCheat();
});

/* ==========================================================
   SLIDE VIEWER CONTROLS
========================================================== */

function initSlideViewer() {
    goToSlide(1);
}

function goToSlide(index) {
    if (index < 1 || index > totalSlides) return;

    // Hide previous
    const oldImg = document.getElementById(`slide-img-${currentSlide}`);
    if (oldImg) {
        oldImg.classList.add('hidden', 'opacity-0');
        oldImg.classList.remove('block', 'opacity-100');
    }

    const oldThumb = document.getElementById(`thumb-btn-${currentSlide}`);
    if (oldThumb) {
        oldThumb.classList.remove('border-indigo-600', 'ring-2', 'ring-indigo-400/40');
        oldThumb.classList.add('border-slate-300', 'opacity-70');
    }

    // Show new
    currentSlide = index;
    const newImg = document.getElementById(`slide-img-${currentSlide}`);
    if (newImg) {
        newImg.classList.remove('hidden', 'opacity-0');
        newImg.classList.add('block', 'opacity-100');
    }

    const newThumb = document.getElementById(`thumb-btn-${currentSlide}`);
    if (newThumb) {
        newThumb.classList.remove('border-slate-300', 'opacity-70');
        newThumb.classList.add('border-indigo-600', 'ring-2', 'ring-indigo-400/40');
        newThumb.scrollIntoView({ behavior: 'smooth', inline: 'nearest', block: 'nearest' });
    }

    // Update counter
    const counter = document.getElementById('slide-counter');
    if (counter) {
        counter.innerText = `Slide ${currentSlide} / ${totalSlides}`;
    }

    // Update buttons state
    const prevBtn = document.getElementById('btn-prev-slide');
    const nextBtn = document.getElementById('btn-next-slide');
    if (prevBtn) prevBtn.disabled = currentSlide <= 1;
    if (nextBtn) nextBtn.disabled = currentSlide >= totalSlides;
}

function prevSlide() {
    if (currentSlide > 1) {
        goToSlide(currentSlide - 1);
    }
}

function nextSlide() {
    if (currentSlide < totalSlides) {
        goToSlide(currentSlide + 1);
    }
}

function initKeyboardNav() {
    document.addEventListener('keydown', (e) => {
        // Do not trigger if typing in inputs or textarea
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        if (e.key === 'ArrowLeft') {
            prevSlide();
        } else if (e.key === 'ArrowRight' || e.key === 'Space') {
            e.preventDefault();
            nextSlide();
        }
    });
}

function toggleFullScreen() {
    const stage = document.getElementById('slide-stage');
    if (!document.fullscreenElement) {
        if (stage.requestFullscreen) {
            stage.requestFullscreen();
        } else if (stage.webkitRequestFullscreen) {
            stage.webkitRequestFullscreen();
        }
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
}


/* ==========================================================
   AUDIO PLAYER LOGIC (LISTENING COMPONENT)
========================================================== */

let audioEl = null;
let currentSpeedIndex = 1;
const speeds = [0.75, 1.0, 1.25, 1.5];

function initAudioPlayer() {
    audioEl = document.getElementById('exam-audio');
    if (!audioEl) return;

    audioEl.addEventListener('loadedmetadata', () => {
        const dur = document.getElementById('audio-duration');
        if (dur) dur.innerText = formatTime(audioEl.duration);
    });

    audioEl.addEventListener('timeupdate', () => {
        const cur = document.getElementById('audio-current-time');
        const prog = document.getElementById('audio-progress');
        if (cur) cur.innerText = formatTime(audioEl.currentTime);
        if (prog && audioEl.duration) {
            prog.value = (audioEl.currentTime / audioEl.duration) * 100;
        }
    });

    audioEl.addEventListener('ended', () => {
        const icon = document.getElementById('audio-play-icon');
        const badge = document.getElementById('audio-status-badge');
        if (icon) {
            icon.setAttribute('data-lucide', 'play');
            lucide.createIcons();
        }
        if (badge) {
            badge.innerText = 'Đã kết thúc';
            badge.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400 border border-slate-700';
        }
    });
}

function formatTime(seconds) {
    if (isNaN(seconds) || seconds <= 0) return "00:00";
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

function toggleAudioPlay() {
    if (!audioEl) return;
    const icon = document.getElementById('audio-play-icon');
    const badge = document.getElementById('audio-status-badge');

    if (audioEl.paused) {
        audioEl.play();
        if (icon) icon.setAttribute('data-lucide', 'pause');
        if (badge) {
            badge.innerText = 'Đang phát...';
            badge.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 animate-pulse';
        }
    } else {
        audioEl.pause();
        if (icon) icon.setAttribute('data-lucide', 'play');
        if (badge) {
            badge.innerText = 'Tạm dừng';
            badge.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400 border border-slate-700';
        }
    }
    if (window.lucide) lucide.createIcons();
}

function audioSeekRelative(seconds) {
    if (!audioEl) return;
    audioEl.currentTime = Math.max(0, Math.min(audioEl.duration || 0, audioEl.currentTime + seconds));
}

function toggleAudioSpeed() {
    if (!audioEl) return;
    currentSpeedIndex = (currentSpeedIndex + 1) % speeds.length;
    const newSpeed = speeds[currentSpeedIndex];
    audioEl.playbackRate = newSpeed;
    const btn = document.getElementById('btn-audio-speed');
    if (btn) btn.innerText = `${newSpeed}x`;
}

function onAudioProgressChange(val) {
    if (!audioEl || !audioEl.duration) return;
    audioEl.currentTime = (val / 100) * audioEl.duration;
}

function onAudioVolumeChange(val) {
    if (!audioEl) return;
    audioEl.volume = parseFloat(val);
    const volIcon = document.getElementById('audio-vol-icon');
    if (volIcon) {
        volIcon.setAttribute('data-lucide', val > 0 ? 'volume-2' : 'volume-x');
        if (window.lucide) lucide.createIcons();
    }
}

function toggleAudioMute() {
    if (!audioEl) return;
    audioEl.muted = !audioEl.muted;
    const volIcon = document.getElementById('audio-vol-icon');
    if (volIcon) {
        volIcon.setAttribute('data-lucide', audioEl.muted ? 'volume-x' : 'volume-2');
        if (window.lucide) lucide.createIcons();
    }
}


/* ==========================================================
   TIMER & PROGRESS
========================================================== */

function initTimer() {
    const timerDisplay = document.getElementById('timer-display');
    const inputTimeTaken = document.getElementById('input-time-taken');

    // If unlimited time
    if (timeLimitMinutes <= 0) {
        timerDisplay.innerText = "Không giới hạn";
        timerInterval = setInterval(() => {
            timeElapsedSeconds++;
            if (inputTimeTaken) inputTimeTaken.value = timeElapsedSeconds;
        }, 1000);
        return;
    }

    function updateTimer() {
        const mins = Math.floor(timeRemainingSeconds / 60);
        const secs = timeRemainingSeconds % 60;
        timerDisplay.innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

        if (timeRemainingSeconds <= 180) { // Under 3 mins
            timerDisplay.classList.add('text-rose-400');
        }

        if (timeRemainingSeconds <= 0) {
            clearInterval(timerInterval);
            alert("Đã hết thời gian làm bài thi! Hệ thống sẽ tự động nộp bài của bạn.");
            document.getElementById('exam-form').submit();
            return;
        }

        timeRemainingSeconds--;
        timeElapsedSeconds++;
        if (inputTimeTaken) inputTimeTaken.value = timeElapsedSeconds;
    }

    updateTimer();
    timerInterval = setInterval(updateTimer, 1000);
}


/* ==========================================================
   ANSWER SELECTION & TRACKING (MCQ & TEXT INPUT)
========================================================== */

function onAnswerSelected(questionId) {
    const jumpBtn = document.getElementById(`jump-btn-${questionId}`);
    if (jumpBtn) {
        jumpBtn.classList.add('answered');
    }
    updateAnsweredCount();
}

function onAnswerSelect(questionId) {
    const sel = document.getElementById(`select-q-${questionId}`);
    const jumpBtn = document.getElementById(`jump-btn-${questionId}`);
    if (sel && jumpBtn) {
        if (sel.value.trim().length > 0) {
            jumpBtn.classList.add('answered');
        } else {
            jumpBtn.classList.remove('answered');
        }
    }
    updateAnsweredCount();
}

function onAnswerInput(questionId) {
    const input = document.getElementById(`input-q-${questionId}`);
    const jumpBtn = document.getElementById(`jump-btn-${questionId}`);
    if (input && jumpBtn) {
        if (input.value.trim().length > 0) {
            jumpBtn.classList.add('answered');
        } else {
            jumpBtn.classList.remove('answered');
        }
    }
    updateAnsweredCount();
}

function updateAnsweredCount() {
    const form = document.getElementById('exam-form');
    if (!form) return 0;

    // 1. Radio inputs checked
    const checkedRadios = form.querySelectorAll('input[type="radio"]:checked');
    let answeredQuestions = new Set();
    checkedRadios.forEach(r => answeredQuestions.add(r.name));

    // 2. Text inputs non-empty
    const textInputs = form.querySelectorAll('input[type="text"][name^="question_"]');
    textInputs.forEach(input => {
        if (input.value.trim().length > 0) {
            answeredQuestions.add(input.name);
        }
    });

    // 3. Dropdown selects chosen
    const selectInputs = form.querySelectorAll('select[name^="question_"]');
    selectInputs.forEach(sel => {
        if (sel.value.trim().length > 0) {
            answeredQuestions.add(sel.name);
        }
    });

    const count = answeredQuestions.size;
    const counterSpan = document.getElementById('answered-counter');
    if (counterSpan) {
        counterSpan.innerText = `${count} / ${totalQuestions} câu`;
    }

    return count;
}

function confirmSubmit() {
    const answered = updateAnsweredCount();
    const unanswered = totalQuestions - answered;
    const msg = document.getElementById('submit-modal-msg');

    if (unanswered > 0) {
        msg.innerHTML = `Bạn đã trả lời <strong class="text-indigo-600 font-bold">${answered}/${totalQuestions}</strong> câu.<br><span class="text-rose-600 font-semibold">Còn ${unanswered} câu chưa trả lời.</span> Bạn có chắc chắn muốn nộp bài?`;
    } else {
        msg.innerHTML = `Tuyệt vời! Bạn đã hoàn thành toàn bộ <strong class="text-emerald-600 font-bold">${totalQuestions}/${totalQuestions}</strong> câu hỏi.<br>Bạn có muốn nộp bài ngay để xem kết quả?`;
    }

    document.getElementById('submit-modal').classList.remove('hidden');
}

function closeModal() {
    const modal = document.getElementById('submit-modal');
    if (modal) modal.classList.add('hidden');
}

function finalizeSubmit() {
    const nameInput = document.getElementById('input-student-name');
    const phoneInput = document.getElementById('input-student-phone');
    const nameVal = nameInput ? nameInput.value.trim() : '';
    const phoneVal = phoneInput ? phoneInput.value.trim() : '';

    if (!nameVal || !phoneVal) {
        closeModal();
        alert("Vui lòng nhập Họ tên và Số điện thoại trước khi nộp bài để hệ thống ghi nhận kết quả!");
        if (typeof openCandidateModal === 'function') {
            openCandidateModal();
        }
        return;
    }

    isSubmitting = true;
    closeModal();
    if (timerInterval) clearInterval(timerInterval);
    const form = document.getElementById('exam-form');
    if (form) {
        form.submit();
    }
}

/* ==========================================================
   ANTI-CHEAT & TAB SWITCH PREVENTION MODULE
========================================================== */

let tabSwitchCount = 0;
const MAX_ALLOWED_SWITCHES = 3;
let lastSwitchTime = 0;
let antiCheatActive = false;
let toastTimeout = null;

function initAntiCheat() {
    // Kích hoạt sau 2 giây khi vào trang để tránh các sự kiện khởi tạo ban đầu
    setTimeout(() => {
        antiCheatActive = true;
    }, 2000);

    // 1. Lắng nghe sự kiện chuyển tab (visibilitychange - chuẩn 100% trên mọi trình duyệt)
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            handleTabSwitch('visibilitychange');
        }
    });

    // 2. Lắng nghe sự kiện mất tiêu điểm cửa sổ (window blur: Alt+Tab, mở ứng dụng khác)
    window.addEventListener('blur', () => {
        // Trì hoãn nhẹ 250ms để lọc bỏ các sự kiện ảo khi nhấp chọn menu dropdown <select> hoặc popup
        setTimeout(() => {
            if (document.hidden || !document.hasFocus()) {
                handleTabSwitch('blur');
            }
        }, 250);
    });

    // 3. Khóa chuột phải trong phòng thi
    document.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        showAntiCheatToast("Thao tác chuột phải bị khóa trong phòng thi!");
        return false;
    });

    // 4. Khóa sao chép câu hỏi (copy, cut)
    document.addEventListener('copy', (e) => {
        const tag = (e.target.tagName || '').toUpperCase();
        if (tag !== 'INPUT' && tag !== 'TEXTAREA') {
            e.preventDefault();
            showAntiCheatToast("Không được phép sao chép câu hỏi khi làm bài!");
            return false;
        }
    });

    document.addEventListener('cut', (e) => {
        const tag = (e.target.tagName || '').toUpperCase();
        if (tag !== 'INPUT' && tag !== 'TEXTAREA') {
            e.preventDefault();
            return false;
        }
    });

    // 5. Khóa các phím tắt gian lận: F12, Ctrl+U, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+P
    document.addEventListener('keydown', (e) => {
        if (e.key === 'F12') {
            e.preventDefault();
            showAntiCheatToast("Phím F12 bị vô hiệu hóa trong phòng thi!");
            return false;
        }
        if (e.ctrlKey && e.shiftKey && ['I', 'i', 'J', 'j', 'C', 'c'].includes(e.key)) {
            e.preventDefault();
            showAntiCheatToast("Công cụ kiểm tra phần tử bị vô hiệu hóa!");
            return false;
        }
        if (e.ctrlKey && (e.key === 'u' || e.key === 'U')) {
            e.preventDefault();
            showAntiCheatToast("Xem mã nguồn bị vô hiệu hóa!");
            return false;
        }
        if (e.ctrlKey && (e.key === 'p' || e.key === 'P')) {
            e.preventDefault();
            return false;
        }
    });

    // 6. Cảnh báo trước khi vô tình đóng tab hoặc tải lại trang
    window.addEventListener('beforeunload', (e) => {
        if (!isSubmitting) {
            e.preventDefault();
            e.returnValue = 'Bạn đang trong quá trình làm bài thi. Rời trang sẽ mất kết quả!';
            return e.returnValue;
        }
    });
}

function handleTabSwitch(source) {
    if (!antiCheatActive || isSubmitting) return;

    // Bỏ qua nếu các modal thông tin thí sinh hoặc modal nộp bài đang mở
    const candModal = document.getElementById('modal-candidate-info');
    if (candModal && !candModal.classList.contains('hidden')) return;

    const subModal = document.getElementById('submit-modal');
    if (subModal && !subModal.classList.contains('hidden')) return;

    // Bỏ qua nếu người dùng chỉ đang thao tác trên các ô chọn lựa (dropdown <select>, input, button)
    const activeEl = document.activeElement;
    if (activeEl && (activeEl.tagName === 'SELECT' || activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA')) {
        if (!document.hidden) {
            return;
        }
    }

    const now = Date.now();
    // Chống đếm đúp trong 2.5 giây
    if (now - lastSwitchTime < 2500) return;
    lastSwitchTime = now;

    tabSwitchCount++;

    // Cập nhật giá trị vào hidden inputs của form
    const inputs = document.querySelectorAll('input[name="tab_switch_count"]');
    inputs.forEach(inp => inp.value = tabSwitchCount);

    // Cập nhật badge trên thanh tiêu đề
    const countEl = document.getElementById('tab-warning-count');
    const badgeEl = document.getElementById('proctor-badge');
    const iconEl = document.getElementById('proctor-icon');
    if (countEl) {
        countEl.innerText = `${tabSwitchCount}/${MAX_ALLOWED_SWITCHES}`;
    }
    if (badgeEl) {
        if (tabSwitchCount >= MAX_ALLOWED_SWITCHES) {
            badgeEl.className = "flex items-center space-x-1.5 px-3 py-1.5 bg-rose-600 text-white border border-rose-700 rounded-xl text-xs font-bold transition-all shadow-md animate-pulse";
            if (iconEl) iconEl.setAttribute('class', 'w-4 h-4 text-white');
        } else {
            badgeEl.className = "flex items-center space-x-1.5 px-3 py-1.5 bg-amber-100 text-amber-900 border border-amber-300 rounded-xl text-xs font-bold transition-all shadow-xs";
            if (iconEl) iconEl.setAttribute('class', 'w-4 h-4 text-amber-600');
        }
    }

    // Phát âm thanh cảnh báo còi vi phạm
    playWarningSound();

    if (tabSwitchCount >= MAX_ALLOWED_SWITCHES) {
        // Vi phạm 3 lần: Khóa bài thi và nộp ngay lập tức!
        const fatalModal = document.getElementById('tab-fatal-modal');
        const warnModal = document.getElementById('tab-warning-modal');
        if (warnModal) warnModal.classList.add('hidden');
        if (fatalModal) fatalModal.classList.remove('hidden');

        isSubmitting = true;
        setTimeout(() => {
            if (timerInterval) clearInterval(timerInterval);
            const form = document.getElementById('exam-form');
            if (form) form.submit();
        }, 3000);
    } else {
        // Hiển thị popup cảnh báo
        const warnModal = document.getElementById('tab-warning-modal');
        const ratioEl = document.getElementById('tab-warning-modal-ratio');
        const progressEl = document.getElementById('tab-warning-progress');
        if (ratioEl) ratioEl.innerText = `${tabSwitchCount} / ${MAX_ALLOWED_SWITCHES} LẦN`;
        if (progressEl) progressEl.style.width = `${(tabSwitchCount / MAX_ALLOWED_SWITCHES) * 100}%`;
        if (warnModal) warnModal.classList.remove('hidden');
    }
}

function dismissTabWarning() {
    const warnModal = document.getElementById('tab-warning-modal');
    if (warnModal) warnModal.classList.add('hidden');
    lastSwitchTime = Date.now();
}

function playWarningSound() {
    try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;
        const ctx = new AudioContext();
        
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(520, ctx.currentTime);
        osc.frequency.setValueAtTime(780, ctx.currentTime + 0.15);
        gain.gain.setValueAtTime(0.3, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.45);
        
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.45);
    } catch(e) {}
}

function showAntiCheatToast(msg) {
    const toast = document.getElementById('anti-cheat-toast');
    const msgEl = document.getElementById('anti-cheat-toast-msg');
    if (!toast || !msgEl) return;

    msgEl.innerText = msg;
    toast.classList.remove('opacity-0', 'pointer-events-none', '-translate-y-6');
    toast.classList.add('opacity-100', 'translate-y-0');

    if (toastTimeout) clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
        toast.classList.remove('opacity-100', 'translate-y-0');
        toast.classList.add('opacity-0', 'pointer-events-none', '-translate-y-6');
    }, 2800);
}

function requestExamFullscreen() {
    const docEl = document.documentElement;
    if (!document.fullscreenElement && !document.webkitFullscreenElement) {
        if (docEl.requestFullscreen) {
            docEl.requestFullscreen().catch(() => {});
        } else if (docEl.webkitRequestFullscreen) {
            docEl.webkitRequestFullscreen();
        }
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen().catch(() => {});
        }
    }
}
