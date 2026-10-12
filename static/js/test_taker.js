// Interactive Test Taker Logic (Slides, Audio, Answers, Timer)

let currentSlide = 1;
let totalSlides = typeof TOTAL_SLIDES !== 'undefined' ? TOTAL_SLIDES : 1;
let totalQuestions = typeof TOTAL_QUESTIONS !== 'undefined' ? TOTAL_QUESTIONS : 0;
let timeLimitMinutes = typeof TIME_LIMIT_MINUTES !== 'undefined' ? TIME_LIMIT_MINUTES : 15;

let timeRemainingSeconds = timeLimitMinutes * 60;
let timeElapsedSeconds = 0;
let timerInterval = null;

document.addEventListener('DOMContentLoaded', () => {
    initSlideViewer();
    initKeyboardNav();
    initTimer();
    initAudioPlayer();
    updateAnsweredCount();
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
    document.getElementById('submit-modal').classList.add('hidden');
}

function finalizeSubmit() {
    closeModal();
    if (timerInterval) clearInterval(timerInterval);
    document.getElementById('exam-form').submit();
}
