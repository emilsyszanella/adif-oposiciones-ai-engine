/**
 * ADIF OPOSICIONES PREP - Interactive Study Engine
 * Downstream Agent Specialized Study Application
 * 
 * Features:
 * - 210 Official Verified Exam Questions across all 21 PDF Topics (10 questions per topic)
 * - Dynamic randomized exam mode (25 random questions per exam, or 10, 50, 100, 210)
 * - 3D Flippable Flashcards with 210 full-deck cards and live shuffling
 * - Smart mistakes notebook (persisted in localStorage)
 * - Complete 21-topic syllabus explorer (10 deep questions per topic)
 * - Topic-targeted test mode and topic flashcards
 * - Full offline PWA support and Mobile Connect QR
 */

(function () {
  'use strict';

  // APPLICATION STATE
  const state = {
    allQuestions: [],          // Full 210-question database
    testQuestions: [],         // Active questions for test mode (e.g. 25 random)
    flashcardQuestions: [],    // Active questions for flashcards mode (full 210 deck)
    currentIndex: 0,
    currentMode: 'test',        // 'test', 'flashcards', 'mistakes', 'syllabus'
    selectedBlock: 'ALL',
    searchQuery: '',
    examSize: '25',             // '25', '10', '50', '100', 'ALL'
    activeTopicFilter: null,    // If studying a specific topic from syllabus
    
    // User progress (persisted in localStorage)
    userStats: {
      totalAnswered: 0,
      totalCorrect: 0,
      failedIds: [],
      flaggedIds: [],
      lastActiveDate: null,
      streakDays: 1,
    },
    
    // Active session stats
    sessionStats: {
      answers: {},              // questionId -> selectedIndex
      startTime: null,
      timerInterval: null,
      secondsElapsed: 0,
    },
    
    // Flashcard state
    flashcardIndex: 0,
    isFlipped: false,
  };

  // DOM ELEMENTS
  const els = {
    // Theme & Header
    themeToggleBtn: document.getElementById('theme-toggle-btn'),
    btnMobileConnect: document.getElementById('btn-mobile-connect'),
    mobileModal: document.getElementById('mobile-modal'),
    modalMobileClose: document.getElementById('modal-mobile-close'),
    mobileUrlText: document.getElementById('mobile-url-text'),
    statAccuracy: document.getElementById('stat-accuracy'),
    statCompleted: document.getElementById('stat-completed'),
    statStreak: document.getElementById('stat-streak'),
    failedCountBadge: document.getElementById('failed-count-badge'),

    // Nav Tabs
    tabTest: document.getElementById('tab-mode-test'),
    tabFlashcards: document.getElementById('tab-mode-flashcards'),
    tabMistakes: document.getElementById('tab-mode-mistakes'),
    tabSyllabus: document.getElementById('tab-mode-syllabus'),

    // Sections
    sectionTest: document.getElementById('section-test'),
    sectionFlashcards: document.getElementById('section-flashcards'),
    sectionMistakes: document.getElementById('section-mistakes'),
    sectionSyllabus: document.getElementById('section-syllabus'),

    // Controls
    blockSelect: document.getElementById('block-select'),
    examSizeSelect: document.getElementById('exam-size-select'),
    searchInput: document.getElementById('search-input'),
    btnNewRandomExam: document.getElementById('btn-new-random-exam'),
    btnShuffle: document.getElementById('btn-shuffle-test'),
    btnResetStats: document.getElementById('btn-reset-stats'),

    // Test Elements
    testCounter: document.getElementById('test-question-counter'),
    testProgressPercent: document.getElementById('test-progress-percent'),
    testProgressBar: document.getElementById('test-progress-bar'),
    testTimerClock: document.getElementById('test-timer-clock'),
    qTopicPill: document.getElementById('q-topic-pill'),
    qDiffPill: document.getElementById('q-diff-pill'),
    qTitle: document.getElementById('q-question-title'),
    qOptionsContainer: document.getElementById('q-options-container'),
    qExplanationBox: document.getElementById('q-explanation-box'),
    qStatusIcon: document.getElementById('q-status-icon'),
    qStatusTitle: document.getElementById('q-status-title'),
    qExplanationText: document.getElementById('q-explanation-text'),
    qCitationArticle: document.getElementById('q-citation-article'),
    qCitationSource: document.getElementById('q-citation-source'),
    qCitationPage: document.getElementById('q-citation-page'),
    btnPrevQuestion: document.getElementById('btn-prev-question'),
    btnNextQuestion: document.getElementById('btn-next-question'),
    btnFlagQuestion: document.getElementById('btn-flag-question'),

    // Flashcard Elements
    flashcardCard: document.getElementById('flashcard-card'),
    flashcardCounter: document.getElementById('flashcard-counter'),
    fcTopicFront: document.getElementById('fc-topic-front'),
    fcQuestionFront: document.getElementById('fc-question-front'),
    fcAnswerBack: document.getElementById('fc-answer-back'),
    fcExplanationBack: document.getElementById('fc-explanation-back'),
    fcReferenceBack: document.getElementById('fc-reference-back'),
    btnFcPrev: document.getElementById('btn-fc-prev'),
    btnFcFlip: document.getElementById('btn-fc-flip'),
    btnFcNext: document.getElementById('btn-fc-next'),
    btnFcShuffle: document.getElementById('btn-fc-shuffle'),

    // Mistakes Elements
    mistakesEmptyState: document.getElementById('mistakes-empty-state'),
    mistakesList: document.getElementById('mistakes-list'),
    btnStartTestFromEmpty: document.getElementById('btn-start-test-from-empty'),

    // Syllabus Elements
    syllabusGridContainer: document.getElementById('syllabus-grid-container'),

    // Modal Elements
    resultsModal: document.getElementById('results-modal'),
    modalScoreText: document.getElementById('modal-score-text'),
    modalPercentageText: document.getElementById('modal-percentage-text'),
    modalTimeText: document.getElementById('modal-time-text'),
    modalFeedbackMessage: document.getElementById('modal-feedback-message'),
    modalBtnReview: document.getElementById('modal-btn-review'),
    modalBtnRestart: document.getElementById('modal-btn-restart'),
  };

  // LOCAL STORAGE PERSISTENCE
  const STORAGE_KEY = 'adif_prep_user_data_v1';

  function loadUserStats() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        state.userStats = Object.assign(state.userStats, parsed);
      }
      checkStreak();
    } catch (e) {
      console.warn('No se pudieron cargar las estadísticas locales:', e);
    }
  }

  function saveUserStats() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.userStats));
      updateHeaderStats();
    } catch (e) {
      console.warn('No se pudieron guardar las estadísticas:', e);
    }
  }

  function checkStreak() {
    const today = new Date().toISOString().slice(0, 10);
    if (!state.userStats.lastActiveDate) {
      state.userStats.lastActiveDate = today;
      state.userStats.streakDays = 1;
    } else if (state.userStats.lastActiveDate !== today) {
      const lastDate = new Date(state.userStats.lastActiveDate);
      const currentDate = new Date(today);
      const diffDays = Math.round((currentDate - lastDate) / (1000 * 60 * 60 * 24));
      if (diffDays === 1) {
        state.userStats.streakDays += 1;
      } else if (diffDays > 1) {
        state.userStats.streakDays = 1;
      }
      state.userStats.lastActiveDate = today;
    }
  }

  function updateHeaderStats() {
    const total = state.userStats.totalAnswered;
    const correct = state.userStats.totalCorrect;
    const acc = total > 0 ? Math.round((correct / total) * 100) : 0;

    if (els.statAccuracy) els.statAccuracy.textContent = `${acc}%`;
    if (els.statCompleted) els.statCompleted.textContent = `${total}`;
    if (els.statStreak) els.statStreak.textContent = `${state.userStats.streakDays} ${state.userStats.streakDays === 1 ? 'día' : 'días'}`;
    if (els.failedCountBadge) els.failedCountBadge.textContent = `${state.userStats.failedIds.length}`;
  }

  // TIMER LOGIC
  function startTimer() {
    stopTimer();
    state.sessionStats.secondsElapsed = 0;
    state.sessionStats.startTime = Date.now();
    state.sessionStats.timerInterval = setInterval(() => {
      state.sessionStats.secondsElapsed += 1;
      renderTimer();
    }, 1000);
  }

  function stopTimer() {
    if (state.sessionStats.timerInterval) {
      clearInterval(state.sessionStats.timerInterval);
      state.sessionStats.timerInterval = null;
    }
  }

  function formatTime(totalSeconds) {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }

  function renderTimer() {
    if (els.testTimerClock) {
      els.testTimerClock.textContent = formatTime(state.sessionStats.secondsElapsed);
    }
  }

  // UTILITY: Fisher-Yates shuffle
  function shuffleArray(array) {
    const arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  // QUESTION POOL GENERATOR
  function generateExamBatch(forceShuffle = true) {
    let basePool = state.allQuestions;

    // Filter by specific topic if set
    if (state.activeTopicFilter) {
      basePool = basePool.filter(q => q.tema_id === state.activeTopicFilter);
    } else {
      // Filter by block
      if (state.selectedBlock !== 'ALL') {
        basePool = basePool.filter(q => q.bloque_id === state.selectedBlock);
      }

      // Filter by search query
      if (state.searchQuery.trim()) {
        const qLower = state.searchQuery.toLowerCase();
        basePool = basePool.filter(q =>
          q.pregunta.toLowerCase().includes(qLower) ||
          q.tema_titulo.toLowerCase().includes(qLower) ||
          q.articulo_referencia.toLowerCase().includes(qLower) ||
          q.explicacion.toLowerCase().includes(qLower)
        );
      }
    }

    // Flashcards deck gets all matching questions (all 210 in full mode!)
    state.flashcardQuestions = forceShuffle ? shuffleArray(basePool) : [...basePool];
    state.flashcardIndex = 0;
    state.isFlipped = false;

    // Test mode applies examSize limit (default 25 questions, or 10, 50, 100, ALL)
    let testPool = forceShuffle ? shuffleArray(basePool) : [...basePool];
    if (!state.activeTopicFilter && state.examSize !== 'ALL') {
      const count = parseInt(state.examSize, 10);
      if (!isNaN(count) && count > 0) {
        testPool = testPool.slice(0, count);
      }
    }
    state.testQuestions = testPool;
    state.currentIndex = 0;
    state.sessionStats.answers = {};
    startTimer();

    if (state.currentMode === 'test') {
      renderCurrentTestQuestion();
    } else if (state.currentMode === 'flashcards') {
      renderCurrentFlashcard();
    }
  }

  // TEST QUESTION RENDERING
  function renderCurrentTestQuestion() {
    if (state.testQuestions.length === 0) {
      els.qTitle.textContent = 'No se encontraron preguntas para los filtros seleccionados.';
      els.qOptionsContainer.innerHTML = '';
      els.qExplanationBox.classList.add('hidden');
      els.testCounter.textContent = '0 / 0';
      els.testProgressBar.style.width = '0%';
      return;
    }

    const q = state.testQuestions[state.currentIndex];
    const total = state.testQuestions.length;
    const currNum = state.currentIndex + 1;

    // Progress bar
    els.testCounter.textContent = `Pregunta ${currNum} de ${total}`;
    const pct = Math.round((currNum / total) * 100);
    els.testProgressPercent.textContent = `${pct}%`;
    els.testProgressBar.style.width = `${pct}%`;

    // Metadata
    els.qTopicPill.textContent = q.tema_titulo;
    els.qDiffPill.textContent = q.dificultad || 'Oficial Adif';
    els.qTitle.textContent = q.pregunta;

    // Flag button state
    const isFlagged = state.userStats.flaggedIds.includes(q.id);
    els.btnFlagQuestion.textContent = isFlagged ? '★ Guardada' : '🔖 Guardar para repaso';
    els.btnFlagQuestion.classList.toggle('btn-primary', isFlagged);
    els.btnFlagQuestion.classList.toggle('btn-outline', !isFlagged);

    // Render options
    els.qOptionsContainer.innerHTML = '';
    const letters = ['A', 'B', 'C', 'D'];
    const previouslyAnswered = state.sessionStats.answers[q.id];

    q.opciones.forEach((optText, idx) => {
      const optBtn = document.createElement('div');
      optBtn.className = 'option-item';
      optBtn.setAttribute('data-index', idx);

      const prefix = document.createElement('div');
      prefix.className = 'option-prefix';
      prefix.textContent = letters[idx];

      const content = document.createElement('div');
      content.className = 'option-content';
      content.textContent = optText;

      optBtn.appendChild(prefix);
      optBtn.appendChild(content);

      if (previouslyAnswered !== undefined) {
        optBtn.classList.add('disabled');
        if (idx === q.respuesta_correcta) {
          optBtn.classList.add('correct');
        } else if (idx === previouslyAnswered) {
          optBtn.classList.add('incorrect');
        }
      } else {
        optBtn.addEventListener('click', () => handleOptionSelect(idx));
      }

      els.qOptionsContainer.appendChild(optBtn);
    });

    // Explanation Box
    if (previouslyAnswered !== undefined) {
      showExplanation(previouslyAnswered === q.respuesta_correcta, q);
    } else {
      els.qExplanationBox.classList.add('hidden');
    }

    // Navigation buttons
    els.btnPrevQuestion.disabled = state.currentIndex === 0;
    els.btnNextQuestion.textContent = state.currentIndex === total - 1 ? 'Finalizar Test 🏁' : 'Siguiente ➔';
  }

  function handleOptionSelect(selectedIndex) {
    const q = state.testQuestions[state.currentIndex];
    if (state.sessionStats.answers[q.id] !== undefined) return; // already answered

    state.sessionStats.answers[q.id] = selectedIndex;
    const isCorrect = selectedIndex === q.respuesta_correcta;

    // Update global user stats
    state.userStats.totalAnswered += 1;
    if (isCorrect) {
      state.userStats.totalCorrect += 1;
      // remove from failed if it was there
      state.userStats.failedIds = state.userStats.failedIds.filter(id => id !== q.id);
    } else {
      // add to failed
      if (!state.userStats.failedIds.includes(q.id)) {
        state.userStats.failedIds.push(q.id);
      }
    }
    saveUserStats();

    // Disable all options and highlight
    const optionEls = els.qOptionsContainer.querySelectorAll('.option-item');
    optionEls.forEach((el, idx) => {
      el.classList.add('disabled');
      if (idx === q.respuesta_correcta) {
        el.classList.add('correct');
      } else if (idx === selectedIndex) {
        el.classList.add('incorrect');
      }
    });

    showExplanation(isCorrect, q);
  }

  function showExplanation(isCorrect, q) {
    els.qExplanationBox.classList.remove('hidden');
    els.qExplanationBox.classList.toggle('error', !isCorrect);

    els.qStatusIcon.textContent = isCorrect ? '✓' : '✗';
    els.qStatusTitle.textContent = isCorrect ? '¡Respuesta Correcta!' : 'Respuesta Incorrecta';
    els.qStatusTitle.style.color = isCorrect ? 'var(--status-success)' : 'var(--status-error)';

    els.qExplanationText.textContent = q.explicacion;
    els.qCitationArticle.textContent = q.articulo_referencia;
    els.qCitationSource.textContent = q.documento_origen;
    els.qCitationPage.textContent = `Pág. ${q.pagina_origen}`;
  }

  // FLASHCARD LOGIC (USES 210-CARD DECK)
  function renderCurrentFlashcard() {
    if (state.flashcardQuestions.length === 0) return;
    const q = state.flashcardQuestions[state.flashcardIndex];
    const total = state.flashcardQuestions.length;

    // Reset flip
    state.isFlipped = false;
    els.flashcardCard.classList.remove('is-flipped');

    els.flashcardCounter.textContent = `Tarjeta ${state.flashcardIndex + 1} de ${total}`;
    els.fcTopicFront.textContent = q.tema_titulo;
    els.fcQuestionFront.textContent = q.pregunta;

    const letters = ['A', 'B', 'C', 'D'];
    const correctLetter = letters[q.respuesta_correcta];
    const correctText = q.opciones[q.respuesta_correcta];

    els.fcAnswerBack.textContent = `Opción ${correctLetter}: ${correctText}`;
    els.fcExplanationBack.textContent = q.explicacion;
    els.fcReferenceBack.textContent = `${q.articulo_referencia} • Pág. ${q.pagina_origen}`;
  }

  function flipFlashcard() {
    state.isFlipped = !state.isFlipped;
    els.flashcardCard.classList.toggle('is-flipped', state.isFlipped);
  }

  // MISTAKES SECTION (REFUERZO INTELIGENTE)
  function renderMistakesSection() {
    const failedIds = state.userStats.failedIds;
    if (failedIds.length === 0) {
      els.mistakesEmptyState.classList.remove('hidden');
      els.mistakesList.classList.add('hidden');
      return;
    }

    els.mistakesEmptyState.classList.add('hidden');
    els.mistakesList.classList.remove('hidden');
    els.mistakesList.innerHTML = '';

    const failedQuestions = state.allQuestions.filter(q => failedIds.includes(q.id));

    failedQuestions.forEach(q => {
      const item = document.createElement('div');
      item.className = 'syllabus-card';
      item.innerHTML = `
        <div>
          <span class="topic-pill" style="margin-bottom:0.5rem;display:inline-block;">${q.tema_titulo}</span>
          <h4 class="syllabus-topic-title">${q.pregunta}</h4>
          <p style="font-size:0.85rem;color:var(--text-secondary);margin-top:0.4rem;"><strong>Base jurídica:</strong> ${q.articulo_referencia} (Pág. ${q.pagina_origen})</p>
        </div>
        <button class="btn btn-primary btn-practicar-fallo" data-id="${q.id}">Practicar Pregunta</button>
      `;
      els.mistakesList.appendChild(item);
    });

    els.mistakesList.querySelectorAll('.btn-practicar-fallo').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.target.getAttribute('data-id');
        const found = state.allQuestions.filter(q => q.id === id);
        state.testQuestions = found;
        state.currentIndex = 0;
        state.sessionStats.answers = {};
        startTimer();
        setMode('test');
      });
    });
  }

  // SYLLABUS SECTION (21 TOPICS, 10 QUESTIONS PER TOPIC)
  function renderSyllabusSection() {
    els.syllabusGridContainer.innerHTML = '';

    // Group questions by topic
    const topicsMap = {};
    state.allQuestions.forEach(q => {
      if (!topicsMap[q.tema_id]) {
        topicsMap[q.tema_id] = {
          id: q.tema_id,
          title: q.tema_titulo,
          bloque: q.bloque_id,
          count: 0,
          sourceDoc: q.documento_origen,
        };
      }
      topicsMap[q.tema_id].count += 1;
    });

    Object.values(topicsMap).forEach((topic, idx) => {
      const card = document.createElement('div');
      card.className = 'syllabus-card';
      card.innerHTML = `
        <div>
          <span class="topic-pill" style="margin-bottom: 0.5rem; display: inline-block;">Tema ${idx + 1} • ${topic.bloque}</span>
          <h3 class="syllabus-topic-title">${topic.title}</h3>
          <div class="syllabus-meta" style="margin-top:0.4rem;">
            <span>📄 ${topic.sourceDoc}</span>
          </div>
        </div>
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem;">
          <button class="btn btn-primary btn-tema-test" data-tema="${topic.id}">
            ⚡ Hacer Test de este Tema (${topic.count} preguntas)
          </button>
          <button class="btn btn-secondary btn-tema-fc" data-tema="${topic.id}">
            🗂 Tarjetas (${topic.count})
          </button>
        </div>
      `;
      els.syllabusGridContainer.appendChild(card);
    });

    // Practice test for single topic
    els.syllabusGridContainer.querySelectorAll('.btn-tema-test').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const temaId = e.currentTarget.getAttribute('data-tema');
        state.activeTopicFilter = temaId;
        if (els.examSizeSelect) els.examSizeSelect.value = 'ALL';
        state.examSize = 'ALL';
        generateExamBatch(true);
        setMode('test');
      });
    });

    // Practice flashcards for single topic
    els.syllabusGridContainer.querySelectorAll('.btn-tema-fc').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const temaId = e.currentTarget.getAttribute('data-tema');
        state.activeTopicFilter = temaId;
        if (els.examSizeSelect) els.examSizeSelect.value = 'ALL';
        state.examSize = 'ALL';
        generateExamBatch(true);
        setMode('flashcards');
      });
    });
  }

  // RESULTS MODAL
  function showResultsModal() {
    stopTimer();
    const answeredCount = Object.keys(state.sessionStats.answers).length;
    let correctCount = 0;

    state.testQuestions.forEach(q => {
      const ans = state.sessionStats.answers[q.id];
      if (ans === q.respuesta_correcta) {
        correctCount += 1;
      }
    });

    const total = state.testQuestions.length;
    // Official Adif penalty: -0.33 per wrong answer
    const incorrectCount = answeredCount - correctCount;
    const penaltyScore = Math.max(0, correctCount - (incorrectCount * 0.33));
    const finalPct = total > 0 ? Math.round((penaltyScore / total) * 100) : 0;

    els.modalScoreText.textContent = `${correctCount}/${total}`;
    els.modalPercentageText.textContent = `${finalPct}%`;
    els.modalTimeText.textContent = formatTime(state.sessionStats.secondsElapsed);

    if (finalPct >= 70) {
      els.modalFeedbackMessage.textContent = '🌟 ¡Excelente puntuación! Tienes un dominio sobresaliente de los temas de Adif y la legislación.';
      els.modalFeedbackMessage.style.borderColor = 'var(--status-success)';
      els.modalFeedbackMessage.style.color = 'var(--status-success)';
    } else if (finalPct >= 50) {
      els.modalFeedbackMessage.textContent = '👍 ¡Aprobado! Has superado el corte del examen. Repasa las preguntas falladas para asegurar tu plaza.';
      els.modalFeedbackMessage.style.borderColor = 'var(--status-warning)';
      els.modalFeedbackMessage.style.color = 'var(--status-warning)';
    } else {
      els.modalFeedbackMessage.textContent = '💪 Sigue practicando. El temario legal y ferroviario requiere constancia. ¡Prueba el modo Flashcards!';
      els.modalFeedbackMessage.style.borderColor = 'var(--accent-cyan)';
      els.modalFeedbackMessage.style.color = 'var(--accent-cyan)';
    }

    els.resultsModal.classList.remove('hidden');
  }

  // NAVIGATION / TAB SWITCHING
  function setMode(mode) {
    state.currentMode = mode;

    [els.tabTest, els.tabFlashcards, els.tabMistakes, els.tabSyllabus].forEach(tab => tab && tab.classList.remove('active'));
    [els.sectionTest, els.sectionFlashcards, els.sectionMistakes, els.sectionSyllabus].forEach(sec => sec && sec.classList.remove('active'));

    if (mode === 'test') {
      if (els.tabTest) els.tabTest.classList.add('active');
      if (els.sectionTest) els.sectionTest.classList.add('active');
      renderCurrentTestQuestion();
      if (!state.sessionStats.timerInterval) startTimer();
    } else if (mode === 'flashcards') {
      if (els.tabFlashcards) els.tabFlashcards.classList.add('active');
      if (els.sectionFlashcards) els.sectionFlashcards.classList.add('active');
      renderCurrentFlashcard();
    } else if (mode === 'mistakes') {
      if (els.tabMistakes) els.tabMistakes.classList.add('active');
      if (els.sectionMistakes) els.sectionMistakes.classList.add('active');
      renderMistakesSection();
    } else if (mode === 'syllabus') {
      if (els.tabSyllabus) els.tabSyllabus.classList.add('active');
      if (els.sectionSyllabus) els.sectionSyllabus.classList.add('active');
      renderSyllabusSection();
    }
  }

  // EVENT LISTENERS INITIALIZATION
  function attachEventListeners() {
    // Mode tabs
    if (els.tabTest) els.tabTest.addEventListener('click', () => setMode('test'));
    if (els.tabFlashcards) els.tabFlashcards.addEventListener('click', () => setMode('flashcards'));
    if (els.tabMistakes) els.tabMistakes.addEventListener('click', () => setMode('mistakes'));
    if (els.tabSyllabus) els.tabSyllabus.addEventListener('click', () => setMode('syllabus'));

    // Theme toggle
    if (els.themeToggleBtn) {
      els.themeToggleBtn.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('adif_prep_theme', next);
      });
    }

    // Filter by block
    if (els.blockSelect) {
      els.blockSelect.addEventListener('change', (e) => {
        state.activeTopicFilter = null;
        state.selectedBlock = e.target.value;
        generateExamBatch(true);
      });
    }

    // Exam size change (10, 25, 50, 100, ALL)
    if (els.examSizeSelect) {
      els.examSizeSelect.addEventListener('change', (e) => {
        state.activeTopicFilter = null;
        state.examSize = e.target.value;
        generateExamBatch(true);
      });
    }

    // Search input
    if (els.searchInput) {
      els.searchInput.addEventListener('input', (e) => {
        state.activeTopicFilter = null;
        state.searchQuery = e.target.value;
        generateExamBatch(true);
      });
    }

    // Generate New Random Exam (🎲 button)
    if (els.btnNewRandomExam) {
      els.btnNewRandomExam.addEventListener('click', () => {
        state.activeTopicFilter = null;
        generateExamBatch(true);
      });
    }

    // Shuffle questions currently in test (🔀 button)
    if (els.btnShuffle) {
      els.btnShuffle.addEventListener('click', () => {
        state.testQuestions = shuffleArray(state.testQuestions);
        state.currentIndex = 0;
        state.sessionStats.answers = {};
        startTimer();
        renderCurrentTestQuestion();
      });
    }

    // Reset stats
    if (els.btnResetStats) {
      els.btnResetStats.addEventListener('click', () => {
        if (confirm('¿Deseas reiniciar las estadísticas de progreso y preguntas falladas?')) {
          state.userStats.totalAnswered = 0;
          state.userStats.totalCorrect = 0;
          state.userStats.failedIds = [];
          state.userStats.flaggedIds = [];
          saveUserStats();
          generateExamBatch(true);
        }
      });
    }

    // Test Navigation
    if (els.btnPrevQuestion) {
      els.btnPrevQuestion.addEventListener('click', () => {
        if (state.currentIndex > 0) {
          state.currentIndex -= 1;
          renderCurrentTestQuestion();
        }
      });
    }

    if (els.btnNextQuestion) {
      els.btnNextQuestion.addEventListener('click', () => {
        if (state.currentIndex < state.testQuestions.length - 1) {
          state.currentIndex += 1;
          renderCurrentTestQuestion();
        } else {
          showResultsModal();
        }
      });
    }

    // Flag Question
    if (els.btnFlagQuestion) {
      els.btnFlagQuestion.addEventListener('click', () => {
        const q = state.testQuestions[state.currentIndex];
        if (!q) return;
        const idx = state.userStats.flaggedIds.indexOf(q.id);
        if (idx >= 0) {
          state.userStats.flaggedIds.splice(idx, 1);
        } else {
          state.userStats.flaggedIds.push(q.id);
        }
        saveUserStats();
        renderCurrentTestQuestion();
      });
    }

    // Flashcard Flip & Navigation
    if (els.flashcardCard) els.flashcardCard.addEventListener('click', flipFlashcard);
    if (els.btnFcFlip) els.btnFcFlip.addEventListener('click', flipFlashcard);

    if (els.btnFcPrev) {
      els.btnFcPrev.addEventListener('click', () => {
        if (state.flashcardIndex > 0) {
          state.flashcardIndex -= 1;
          renderCurrentFlashcard();
        }
      });
    }

    if (els.btnFcNext) {
      els.btnFcNext.addEventListener('click', () => {
        if (state.flashcardIndex < state.flashcardQuestions.length - 1) {
          state.flashcardIndex += 1;
          renderCurrentFlashcard();
        }
      });
    }

    // Flashcard Shuffle
    if (els.btnFcShuffle) {
      els.btnFcShuffle.addEventListener('click', () => {
        state.flashcardQuestions = shuffleArray(state.flashcardQuestions);
        state.flashcardIndex = 0;
        state.isFlipped = false;
        renderCurrentFlashcard();
      });
    }

    // Modal buttons
    if (els.modalBtnReview) {
      els.modalBtnReview.addEventListener('click', () => {
        els.resultsModal.classList.add('hidden');
        state.currentIndex = 0;
        renderCurrentTestQuestion();
      });
    }

    if (els.modalBtnRestart) {
      els.modalBtnRestart.addEventListener('click', () => {
        els.resultsModal.classList.add('hidden');
        generateExamBatch(true);
      });
    }

    if (els.btnStartTestFromEmpty) {
      els.btnStartTestFromEmpty.addEventListener('click', () => setMode('test'));
    }

    // Mobile Connect Modal
    if (els.btnMobileConnect && els.mobileModal) {
      els.btnMobileConnect.addEventListener('click', () => {
        const host = window.location.hostname || '192.168.1.206';
        const port = window.location.port ? `:${window.location.port}` : '';
        const protocol = window.location.protocol || 'http:';
        if (els.mobileUrlText) {
          els.mobileUrlText.textContent = `${protocol}//${host}${port}`;
        }
        els.mobileModal.classList.remove('hidden');
      });

      if (els.modalMobileClose) {
        els.modalMobileClose.addEventListener('click', () => {
          els.mobileModal.classList.add('hidden');
        });
      }

      els.mobileModal.addEventListener('click', (e) => {
        if (e.target === els.mobileModal) {
          els.mobileModal.classList.add('hidden');
        }
      });
    }

    // KEYBOARD SHORTCUTS
    window.addEventListener('keydown', (e) => {
      // Don't capture when typing in search input
      if (document.activeElement === els.searchInput) return;

      if (state.currentMode === 'test') {
        const key = e.key.toUpperCase();
        const map = { '1': 0, '2': 1, '3': 2, '4': 3, 'A': 0, 'B': 1, 'C': 2, 'D': 3 };
        if (map[key] !== undefined) {
          handleOptionSelect(map[key]);
        } else if (e.key === 'ArrowRight' || e.key === 'Enter') {
          if (state.currentIndex < state.testQuestions.length - 1) {
            state.currentIndex += 1;
            renderCurrentTestQuestion();
          }
        } else if (e.key === 'ArrowLeft') {
          if (state.currentIndex > 0) {
            state.currentIndex -= 1;
            renderCurrentTestQuestion();
          }
        }
      } else if (state.currentMode === 'flashcards') {
        if (e.code === 'Space') {
          e.preventDefault();
          flipFlashcard();
        } else if (e.key === 'ArrowRight') {
          if (state.flashcardIndex < state.flashcardQuestions.length - 1) {
            state.flashcardIndex += 1;
            renderCurrentFlashcard();
          }
        } else if (e.key === 'ArrowLeft') {
          if (state.flashcardIndex > 0) {
            state.flashcardIndex -= 1;
            renderCurrentFlashcard();
          }
        }
      }
    });
  }

  // INITIAL BOOTSTRAP
  function init() {
    // Load stored theme
    const savedTheme = localStorage.getItem('adif_prep_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);

    loadUserStats();
    attachEventListeners();

    // Register Service Worker for offline PWA
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('./sw.js').catch(err => {
        console.debug('Service Worker no registrado:', err);
      });
    }

    // Load data from global window object (offline bundle)
    if (window.ADIF_EXAM_DATA && Array.isArray(window.ADIF_EXAM_DATA.preguntas)) {
      state.allQuestions = window.ADIF_EXAM_DATA.preguntas;
      generateExamBatch(true);
    } else {
      // Fallback: fetch JSON
      fetch('adif_questions_db.json')
        .then(res => res.json())
        .then(data => {
          state.allQuestions = data;
          generateExamBatch(true);
        })
        .catch(err => {
          console.error('Error cargando preguntas:', err);
          if (els.qTitle) {
            els.qTitle.textContent = 'Error cargando las preguntas del temario de Adif.';
          }
        });
    }
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
