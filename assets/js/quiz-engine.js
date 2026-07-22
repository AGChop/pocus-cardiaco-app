// Motor de Cuestionarios Educativos de POCUS Cardíaco
const QuizEngine = {
    // Diccionario de textos de interfaz en Español como idioma base y de respaldo
    uiStrings: {
        title: "Cuestionarios",
        noQuizzes: "No hay cuestionarios disponibles en este momento.",
        start: "Iniciar Cuestionario",
        continue: "Continuar Cuestionario",
        retry: "Reintentar Cuestionario",
        restartAttempt: "Reiniciar Intento",
        previous: "Anterior",
        next: "Siguiente",
        submit: "Confirmar Respuesta",
        complete: "Finalizar Cuestionario",
        questionIndex: "Pregunta {x} de {y}",
        progress: "Progreso",
        score: "Puntaje",
        result: "Resultado",
        passed: "Aprobado",
        failed: "No aprobado",
        answerSubmitted: "Respuesta registrada",
        selectAnswer: "Por favor, selecciona una respuesta antes de continuar.",
        backToList: "Volver a Cuestionarios",
        attempt: "Intento",
        completedStatus: "Completado",
        inProgressStatus: "En progreso",
        educationalDisclaimer: "Aviso: Esta es una herramienta de autoevaluación formativa. El resultado tiene fines únicamente educativos y no constituye una certificación clínica o acreditación profesional médica.",
        changeAnswer: "Cambiar Respuesta",
        minPassingScore: "Nota mínima: {score}%",
        difficultyBeginner: "Principiante",
        difficultyIntermediate: "Intermedio",
        difficultyAdvanced: "Avanzado"
    },

    // --- CORRECCIÓN 1: SEGURIDAD DE RENDERIZADO Y SANEAMIENTO ---
    escapeHTML(value) {
        if (value === null || value === undefined) return "";
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    },

    isValidStableId(value) {
        if (typeof value !== "string" || !value) return false;
        return /^[A-Za-z0-9_-]+$/.test(value);
    },

    safeStableId(value) {
        if (this.isValidStableId(value)) return value;
        throw new Error("Invalid stable ID format");
    },

    normalizeLocalizedText(value, language = "es") {
        if (!value) return "";
        if (typeof value === "string") return value;
        if (typeof value === "object") {
            return value[language] || value["es"] || value["en"] || "";
        }
        return String(value);
    },

    shuffleQuestionOrder(questionIds, randomFn = Math.random) {
        if (!Array.isArray(questionIds)) return [];
        const arr = [...questionIds];
        for (let i = arr.length - 1; i > 0; i--) {
            const j = Math.floor(randomFn() * (i + 1));
            [arr[i], arr[j]] = [arr[j], arr[i]];
        }
        return arr;
    },

    // 1. Obtener cuestionario por ID
    getQuizById(quizzes, quizId) {
        if (!Array.isArray(quizzes)) return null;
        return quizzes.find(q => q.id === quizId) || null;
    },

    // 2. Validación defensiva de la estructura de un cuestionario
    validateQuizDefinition(quiz) {
        if (!quiz || typeof quiz !== 'object') return false;
        if (!this.isValidStableId(quiz.id)) return false;

        const titleText = this.normalizeLocalizedText(quiz.title);
        if (!titleText || typeof titleText !== 'string') return false;

        if (typeof quiz.passing_score !== 'number' || !Number.isFinite(quiz.passing_score) || quiz.passing_score < 0 || quiz.passing_score > 100) return false;
        if (!Array.isArray(quiz.questions) || quiz.questions.length === 0) return false;

        const allowedTypes = ['single_choice', 'multiple_choice', 'true_false'];
        const questionIds = new Set();

        for (const q of quiz.questions) {
            if (!q || typeof q !== 'object') return false;
            if (!this.isValidStableId(q.id)) return false;
            if (questionIds.has(q.id)) return false;
            questionIds.add(q.id);

            if (!allowedTypes.includes(q.type)) return false;

            const promptText = this.normalizeLocalizedText(q.prompt);
            if (!promptText || typeof promptText !== 'string') return false;

            // points es obligatorio, finito y no negativo
            if (typeof q.points !== 'number' || !Number.isFinite(q.points) || q.points < 0) return false;

            if (q.type === 'single_choice' || q.type === 'multiple_choice') {
                if (!Array.isArray(q.options) || q.options.length < 2) return false;
                const optionIds = new Set();
                for (const opt of q.options) {
                    if (!opt || typeof opt !== 'object' || !this.isValidStableId(opt.id)) return false;
                    if (optionIds.has(opt.id)) return false;
                    optionIds.add(opt.id);

                    const optText = this.normalizeLocalizedText(opt.text);
                    if (!optText || typeof optText !== 'string') return false;
                }

                if (q.type === 'single_choice') {
                    if (typeof q.correct_answer !== 'string' || !optionIds.has(q.correct_answer)) return false;
                } else {
                    if (!Array.isArray(q.correct_answer) || q.correct_answer.length === 0) return false;
                    const correctSet = new Set();
                    for (const ansId of q.correct_answer) {
                        if (typeof ansId !== 'string' || !optionIds.has(ansId) || correctSet.has(ansId)) return false;
                        correctSet.add(ansId);
                    }
                }
            } else if (q.type === 'true_false') {
                if (typeof q.correct_answer !== 'boolean') return false;
            }
        }

        return true;
    },

    // 3. Validación de respuestas
    validateSubmittedAnswer(question, answer) {
        if (!question || !question.type || answer === undefined || answer === null) return false;

        if (question.type === 'single_choice') {
            if (typeof answer !== 'string' || !this.isValidStableId(answer)) return false;
            return question.options.some(opt => opt.id === answer);
        }

        if (question.type === 'multiple_choice') {
            if (!Array.isArray(answer) || answer.length === 0) return false;
            const seen = new Set();
            for (const item of answer) {
                if (typeof item !== 'string' || !this.isValidStableId(item) || seen.has(item)) return false;
                seen.add(item);
                if (!question.options.some(opt => opt.id === item)) return false;
            }
            return true;
        }

        if (question.type === 'true_false') {
            return typeof answer === 'boolean' || answer === 'true' || answer === 'false';
        }

        return false;
    },

    normalizeTrueFalseAnswer(answer) {
        if (typeof answer === 'boolean') return answer;
        if (answer === 'true') return true;
        if (answer === 'false') return false;
        return null;
    },

    // 4. Crear una nueva sesión de cuestionario
    createQuizSession(quiz) {
        if (!this.validateQuizDefinition(quiz)) return null;

        const questionIds = quiz.questions.map(q => q.id);
        const questionOrder = quiz.randomize_questions ? this.shuffleQuestionOrder(questionIds) : questionIds;

        return {
            quiz_id: quiz.id,
            schema_version: "1.0",
            started_at: Date.now(),
            updated_at: Date.now(),
            current_question_index: 0,
            question_order: questionOrder,
            answers_by_question_id: {},
            confirmed_answers: {},
            attempt_number: 1,
            completed: false
        };
    },

    // 5. Restaurar una sesión guardada
    restoreQuizSession(quiz, quizId) {
        if (!quiz || typeof Storage === "undefined") return null;
        try {
            const session = Storage.getProgress('quiz', quizId);
            if (!session) return null;

            if (session.quiz_id !== quizId) return this._discardSession(quizId);
            if (session.schema_version !== "1.0") return this._discardSession(quizId);
            if (!Array.isArray(session.question_order) || session.question_order.length === 0) return this._discardSession(quizId);
            if (session.question_order.length !== quiz.questions.length) return this._discardSession(quizId);

            const questionIds = new Set(session.question_order);
            if (questionIds.size !== session.question_order.length) return this._discardSession(quizId);
            const allOrderValid = session.question_order.every(qId => this.isValidStableId(qId));
            if (!allOrderValid) return this._discardSession(quizId);

            const validQuizIds = new Set(quiz.questions.map(q => q.id));
            if (questionIds.size !== validQuizIds.size) return this._discardSession(quizId);
            for (const qId of questionIds) {
                if (!validQuizIds.has(qId)) return this._discardSession(quizId);
            }

            if (typeof session.current_question_index !== 'number' || !Number.isInteger(session.current_question_index) || session.current_question_index < 0) return this._discardSession(quizId);
            if (session.current_question_index >= session.question_order.length) return this._discardSession(quizId);

            if (typeof session.attempt_number !== 'number' || !Number.isInteger(session.attempt_number) || session.attempt_number <= 0) return this._discardSession(quizId);
            if (typeof session.completed !== 'boolean') return this._discardSession(quizId);

            if (typeof session.answers_by_question_id !== 'object' || session.answers_by_question_id === null) return this._discardSession(quizId);
            if (typeof session.confirmed_answers !== 'object' || session.confirmed_answers === null) return this._discardSession(quizId);

            for (const qId in session.answers_by_question_id) {
                if (!validQuizIds.has(qId)) return this._discardSession(quizId);
                const question = quiz.questions.find(q => q.id === qId);
                const ans = session.answers_by_question_id[qId];
                if (!this.validateSubmittedAnswer(question, ans)) return this._discardSession(quizId);
            }

            for (const qId in session.confirmed_answers) {
                if (!validQuizIds.has(qId)) return this._discardSession(quizId);
                if (typeof session.confirmed_answers[qId] !== 'boolean') return this._discardSession(quizId);
                if (session.confirmed_answers[qId]) {
                    if (session.answers_by_question_id[qId] === undefined) return this._discardSession(quizId);
                }
            }

            if (session.started_at !== undefined && (typeof session.started_at !== 'number' || !Number.isFinite(session.started_at))) return this._discardSession(quizId);
            if (session.updated_at !== undefined && (typeof session.updated_at !== 'number' || !Number.isFinite(session.updated_at))) return this._discardSession(quizId);

            return session;
        } catch (e) {
            console.warn("QuizEngine: Error restaurando sesión, descartando:", e);
            return this._discardSession(quizId);
        }
    },

    _discardSession(quizId) {
        if (typeof Storage !== "undefined") {
            try {
                Storage.removeProgress('quiz', quizId);
            } catch (e) {
                console.error("QuizEngine: Error eliminando progreso:", e);
            }
        }
        return null;
    },

    // 6. Guardar la sesión
    saveQuizSession(session) {
        if (!session || !session.quiz_id) return false;
        session.updated_at = Date.now();
        if (typeof Storage !== "undefined") {
            Storage.saveProgress('quiz', session.quiz_id, session);
            return true;
        }
        return false;
    },

    // 7. Evaluar respuesta
    evaluateAnswer(question, answer) {
        if (!question || !question.type || answer === undefined || answer === null) return false;

        switch (question.type) {
            case 'single_choice':
                return answer === question.correct_answer;

            case 'true_false':
                return this.normalizeTrueFalseAnswer(answer) === question.correct_answer;

            case 'multiple_choice':
                const correct = Array.isArray(question.correct_answer) ? question.correct_answer : [];
                const submitted = Array.isArray(answer) ? answer : [];
                if (correct.length !== submitted.length) return false;
                return correct.every(item => submitted.includes(item)) && submitted.every(item => correct.includes(item));

            default:
                return false;
        }
    },

    // 8. Enviar respuesta
    submitAnswer(session, question, answer) {
        if (!session || !question) return false;
        if (!this.validateSubmittedAnswer(question, answer)) return false;

        let finalAnswer = answer;
        if (question.type === 'true_false') {
            finalAnswer = this.normalizeTrueFalseAnswer(answer);
        }

        session.answers_by_question_id[question.id] = finalAnswer;
        session.confirmed_answers[question.id] = true;
        session.updated_at = Date.now();

        this.saveQuizSession(session);
        return true;
    },

    // 9. Calcular puntaje
    calculateQuizScore(session, quiz) {
        if (!session || !quiz) return { score: 0, passed: false, earned: 0, max: 0, correct_count: 0, total_questions: 0 };

        let earned = 0;
        let max = 0;
        let correctCount = 0;

        quiz.questions.forEach(q => {
            const points = q.points; // Garantizado por validación obligatoria
            max += points;
            const ans = session.answers_by_question_id[q.id];
            if (ans !== undefined && this.evaluateAnswer(q, ans)) {
                earned += points;
                correctCount++;
            }
        });

        const score = max > 0 ? Math.round((earned / max) * 100) : 0;
        const passed = score >= (quiz.passing_score || 0);

        return {
            score,
            passed,
            earned,
            max,
            correct_count: correctCount,
            total_questions: quiz.questions.length
        };
    },

    canCompleteQuiz(session, quiz) {
        if (!session || !quiz) return false;
        return session.question_order.every(qId => {
            const question = quiz.questions.find(q => q.id === qId);
            if (!question) return false;
            const hasAns = session.answers_by_question_id[qId] !== undefined;
            const isConf = !!session.confirmed_answers[qId];
            return hasAns && isConf && this.validateSubmittedAnswer(question, session.answers_by_question_id[qId]);
        });
    },

    completeQuiz(session, quiz) {
        if (!session || !quiz) return null;
        if (!this.canCompleteQuiz(session, quiz)) return null;

        session.completed = true;
        const result = this.calculateQuizScore(session, quiz);
        this.saveQuizSession(session);
        return result;
    },

    restartQuiz(session, quiz) {
        if (!quiz) return null;
        if (quiz.allow_retry === false) return null;

        const newSession = this.createQuizSession(quiz);
        if (newSession && session) {
            newSession.attempt_number = (session.attempt_number || 1) + 1;
        }
        if (newSession) {
            this.saveQuizSession(newSession);
        }
        return newSession;
    },

    // Métodos de navegación
    getCurrentQuestion(session, quiz) {
        if (!session || !quiz) return null;
        const index = session.current_question_index;
        if (index < 0 || index >= session.question_order.length) return null;
        const qId = session.question_order[index];
        return quiz.questions.find(q => q.id === qId) || null;
    },

    goToNextQuestion(session, quiz) {
        if (!session || !quiz) return false;
        if (session.current_question_index < session.question_order.length - 1) {
            session.current_question_index++;
            this.saveQuizSession(session);
            return true;
        }
        return false;
    },

    goToPreviousQuestion(session, quiz) {
        if (!session || !quiz) return false;
        if (session.current_question_index > 0) {
            session.current_question_index--;
            this.saveQuizSession(session);
            return true;
        }
        return false;
    },

    isQuestionAnswered(session, questionId) {
        if (!session || !questionId) return false;
        return session.answers_by_question_id[questionId] !== undefined;
    },

    isQuestionConfirmed(session, questionId) {
        if (!session || !questionId) return false;
        return !!session.confirmed_answers[questionId];
    },

    getQuizProgress(session, quiz) {
        if (!session || !quiz) return { current: 0, total: 0, percentage: 0 };
        const current = session.current_question_index + 1;
        const total = session.question_order.length;
        const percentage = total > 0 ? Math.round((current / total) * 100) : 0;
        return { current, total, percentage };
    },

    // --- CORRECCIÓN 7: RENDERIZADO INTERACTIVO ACCESIBLE Y SEGURO ---
    refreshQuizView(container, quiz, session, mediaResources = []) {
        if (!container || !quiz) return;

        if (!session) {
            this.renderQuizDetail(container, quiz, null);
        } else if (session.completed) {
            this.renderQuizSummary(container, quiz, session);
        } else {
            const question = this.getCurrentQuestion(session, quiz);
            if (question) {
                this.renderQuizQuestion(container, quiz, session, question, mediaResources);
            } else {
                this.renderQuizDetail(container, quiz, session);
            }
        }
    },

    renderQuizList(container, quizzes) {
        if (!container) return;

        const validQuizzes = Array.isArray(quizzes) ? quizzes.filter(q => q.review_status === "approved" && this.validateQuizDefinition(q)) : [];

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← Volver al Inicio</a>
                <h2>${this.escapeHTML(this.uiStrings.title)}</h2>
            </div>
            <div class="quiz-page">
        `;

        if (validQuizzes.length === 0) {
            html += `
                <div class="quiz-empty-state card">
                    <p style="text-align: center; color: var(--text-muted-light); padding: 2rem 0;">
                        ${this.escapeHTML(this.uiStrings.noQuizzes)}
                    </p>
                </div>
            `;
        } else {
            html += `<div class="quiz-list">`;
            validQuizzes.forEach(quiz => {
                const session = this.restoreQuizSession(quiz, quiz.id);
                let progressText = this.uiStrings.inProgressStatus;
                let actionBtnText = this.uiStrings.start;
                let actionAttr = "start";
                let badgeClass = "badge-new";

                if (session) {
                    if (session.completed) {
                        const scoreData = this.calculateQuizScore(session, quiz);
                        progressText = `${this.uiStrings.completedStatus} - ${scoreData.score}% (${scoreData.passed ? this.uiStrings.passed : this.uiStrings.failed})`;
                        badgeClass = scoreData.passed ? "badge-success" : "badge-error";

                        if (quiz.allow_retry !== false) {
                            actionBtnText = this.uiStrings.retry;
                            actionAttr = "restart";
                        } else {
                            actionBtnText = "";
                        }
                    } else {
                        const progress = this.getQuizProgress(session, quiz);
                        progressText = `${this.uiStrings.inProgressStatus} (${progress.current}/${progress.total})`;
                        badgeClass = "badge-warning";
                        actionBtnText = this.uiStrings.continue;
                        actionAttr = "start";
                    }
                } else {
                    progressText = "No iniciado";
                }

                const difficulty = quiz.difficulty || "beginner";
                const diffLabel = this.uiStrings[`difficulty${difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}`] || difficulty;

                const qIdEscaped = this.escapeHTML(this.safeStableId(quiz.id));
                const titleEscaped = this.escapeHTML(this.normalizeLocalizedText(quiz.title));
                const descEscaped = this.escapeHTML(this.normalizeLocalizedText(quiz.description));
                const diffEscaped = this.escapeHTML(diffLabel);
                const timeEscaped = this.escapeHTML(String(quiz.estimated_minutes || 0));
                const sizeEscaped = this.escapeHTML(String(quiz.questions.length));

                html += `
                    <div class="quiz-card card">
                        <div class="quiz-card-header" style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <h3 style="margin: 0; font-size: 1.15rem; color: var(--primary-medium);">${titleEscaped}</h3>
                            <span class="result-badge ${this.escapeHTML(badgeClass)}" style="font-size: 0.75rem; white-space: nowrap;">${this.escapeHTML(progressText)}</span>
                        </div>
                        <p style="font-size: 0.9rem; margin-bottom: 0.75rem; line-height: 1.4;">${descEscaped}</p>
                        <div class="quiz-meta" style="display: flex; gap: 0.75rem; flex-wrap: wrap; font-size: 0.8rem; color: var(--text-muted-light); margin-bottom: 1rem;">
                            <span><strong>Dificultad:</strong> ${diffEscaped}</span>
                            <span><strong>Tiempo:</strong> ${timeEscaped} min</span>
                            <span><strong>Preguntas:</strong> ${sizeEscaped}</span>
                        </div>
                        ${actionBtnText ? `
                        <a href="#/cuestionarios/${qIdEscaped}" class="btn-primary" style="display: block; text-align: center; text-decoration: none;" data-quiz-action="${this.escapeHTML(actionAttr)}" data-quiz-id="${qIdEscaped}">
                            ${this.escapeHTML(actionBtnText)}
                        </a>` : `
                        <a href="#/cuestionarios/${qIdEscaped}" class="btn-secondary" style="display: block; text-align: center; text-decoration: none;" data-quiz-action="view" data-quiz-id="${qIdEscaped}">
                            Ver Resultados
                        </a>`}
                    </div>
                `;
            });
            html += `</div>`;
        }

        html += `</div>`;
        container.innerHTML = html;
        this.initializeQuizInteractions(container, null, null);
    },

    renderQuizDetail(container, quiz, session) {
        if (!container) return;

        const difficulty = quiz.difficulty || "beginner";
        const diffLabel = this.uiStrings[`difficulty${difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}`] || difficulty;
        const totalQuestions = quiz.questions.length;
        const minPassing = quiz.passing_score;

        let actionBtnText = this.uiStrings.start;
        let actionAttr = "start";
        let showReset = false;

        if (session) {
            if (session.completed) {
                if (quiz.allow_retry !== false) {
                    actionBtnText = this.uiStrings.retry;
                    actionAttr = "restart";
                } else {
                    actionBtnText = "";
                }
            } else {
                actionBtnText = this.uiStrings.continue;
                actionAttr = "start";
                showReset = true;
            }
        }

        const titleEscaped = this.escapeHTML(this.normalizeLocalizedText(quiz.title));
        const descEscaped = this.escapeHTML(this.normalizeLocalizedText(quiz.description));
        const diffEscaped = this.escapeHTML(diffLabel);
        const timeEscaped = this.escapeHTML(String(quiz.estimated_minutes || 0));
        const totalEscaped = this.escapeHTML(String(totalQuestions));
        const minEscaped = this.escapeHTML(String(minPassing));
        const attemptEscaped = session ? this.escapeHTML(String(session.attempt_number)) : "";
        const instEscaped = quiz.instructions ? this.escapeHTML(this.normalizeLocalizedText(quiz.instructions)) : "";

        let html = `
            <div class="navigation-header">
                <a href="#/cuestionarios" class="btn-back" data-quiz-action="back-to-list">← ${this.escapeHTML(this.uiStrings.backToList)}</a>
                <h2>${titleEscaped}</h2>
            </div>
            <div class="quiz-introduction card">
                <p style="font-size: 1.05rem; margin-bottom: 1rem; line-height: 1.5;">${descEscaped}</p>
                <div style="margin: 1rem 0; padding: 1rem; background-color: var(--primary-bg-light); border-radius: 6px; border-left: 4px solid var(--primary-medium);">
                    <h4 style="margin: 0 0 0.5rem 0; color: var(--primary-medium);">${this.escapeHTML(this.uiStrings.progress)}</h4>
                    <ul style="margin: 0; padding-left: 1.25rem; font-size: 0.95rem; line-height: 1.6; color: var(--text-main-light);">
                        <li><strong>Dificultad:</strong> ${diffEscaped}</li>
                        <li><strong>Duración estimada:</strong> ${timeEscaped} minutos</li>
                        <li><strong>Cantidad de preguntas:</strong> ${totalEscaped}</li>
                        <li><strong>Nota de aprobación:</strong> ${minEscaped}%</li>
                        ${session ? `<li><strong>Intento actual:</strong> ${attemptEscaped}</li>` : ''}
                    </ul>
                </div>

                ${quiz.instructions ? `
                <div style="margin-top: 1rem;">
                    <strong style="font-size: 0.95rem;">Instrucciones:</strong>
                    <p style="font-size: 0.9rem; margin-top: 0.25rem; line-height: 1.5; color: var(--text-muted-light);">${instEscaped}</p>
                </div>` : ''}

                <div class="quiz-disclaimer" style="margin: 1.5rem 0; font-size: 0.8rem; font-style: italic; color: var(--text-muted-light); line-height: 1.4;">
                    ${this.escapeHTML(this.uiStrings.educationalDisclaimer)}
                </div>

                <div class="quiz-actions" style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 1.5rem;">
                    ${actionBtnText ? `<button class="btn-primary" data-quiz-action="${this.escapeHTML(actionAttr)}" style="flex: 1; min-width: 150px;">${this.escapeHTML(actionBtnText)}</button>` : ''}
                    ${showReset ? `<button class="btn-secondary" data-quiz-action="restart" style="min-width: 150px;">${this.escapeHTML(this.uiStrings.restartAttempt)}</button>` : ''}
                </div>
            </div>
        `;

        container.innerHTML = html;
        this.initializeQuizInteractions(container, quiz, session);
    },

    renderQuizQuestion(container, quiz, session, question, mediaResources = []) {
        if (!container || !session || !question) return;

        const progress = this.getQuizProgress(session, quiz);
        const answered = this.isQuestionAnswered(session, question.id);
        const confirmed = this.isQuestionConfirmed(session, question.id);
        const savedAnswer = session.answers_by_question_id[question.id];

        let mediaHTML = "";
        if (question.media_resource_ids && question.media_resource_ids.length > 0 && typeof MediaViewer !== "undefined") {
            const filteredMedia = mediaResources.filter(m => question.media_resource_ids.includes(m.id));
            if (filteredMedia.length > 0) {
                // MediaViewer.renderMediaSection produce marcado confiable de componente
                mediaHTML = `
                    <div class="quiz-media-container" style="margin: 1rem 0; text-align: center;">
                        ${MediaViewer.renderMediaSection(filteredMedia)}
                    </div>
                `;
            }
        }

        let optionsHTML = "";
        const qIdEscaped = this.escapeHTML(this.safeStableId(question.id));

        if (question.type === 'single_choice' || question.type === 'multiple_choice') {
            optionsHTML += `<fieldset class="quiz-options" style="border: none; padding: 0; margin: 1rem 0;">`;
            optionsHTML += `<legend class="quiz-legend" tabindex="-1" style="outline: none;">Selecciona tu respuesta:</legend>`;

            question.options.forEach(opt => {
                const optId = opt.id;
                const optIdEscaped = this.escapeHTML(this.safeStableId(optId));
                const optText = opt.text?.es || opt.text?.en;
                const optTextEscaped = this.escapeHTML(optText);
                const inputType = question.type === 'single_choice' ? 'radio' : 'checkbox';
                const inputName = `question-${qIdEscaped}`;
                let isChecked = false;

                if (question.type === 'single_choice') {
                    isChecked = savedAnswer === optId;
                } else {
                    isChecked = Array.isArray(savedAnswer) && savedAnswer.includes(optId);
                }

                // ID accesible id/for
                const inputDomId = `opt-${qIdEscaped}-${optIdEscaped}`;

                optionsHTML += `
                    <label class="quiz-option" for="${inputDomId}" style="display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.75rem; border: 1px solid var(--border-light); border-radius: 6px; margin-bottom: 0.5rem; cursor: pointer;">
                        <input type="${inputType}" name="${inputName}" id="${inputDomId}" data-option-id="${optIdEscaped}" ${isChecked ? 'checked' : ''} ${confirmed ? 'disabled' : ''} style="margin-top: 0.2rem;">
                        <span style="font-size: 0.95rem;">${optTextEscaped}</span>
                    </label>
                `;
            });
            optionsHTML += `</fieldset>`;
        } else if (question.type === 'true_false') {
            optionsHTML += `<fieldset class="quiz-options" style="border: none; padding: 0; margin: 1rem 0;">`;
            optionsHTML += `<legend class="quiz-legend" tabindex="-1" style="outline: none;">Selecciona si es Verdadero o Falso:</legend>`;

            const tfOptions = [
                { id: "true", text: "Verdadero" },
                { id: "false", text: "Falso" }
            ];

            tfOptions.forEach(opt => {
                const optIdEscaped = this.escapeHTML(opt.id);
                const isChecked = String(savedAnswer) === opt.id;
                const inputDomId = `opt-${qIdEscaped}-${optIdEscaped}`;

                optionsHTML += `
                    <label class="quiz-option" for="${inputDomId}" style="display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.75rem; border: 1px solid var(--border-light); border-radius: 6px; margin-bottom: 0.5rem; cursor: pointer;">
                        <input type="radio" name="question-${qIdEscaped}" id="${inputDomId}" data-option-id="${optIdEscaped}" ${isChecked ? 'checked' : ''} ${confirmed ? 'disabled' : ''} style="margin-top: 0.2rem;">
                        <span style="font-size: 0.95rem;">${this.escapeHTML(opt.text)}</span>
                    </label>
                `;
            });
            optionsHTML += `</fieldset>`;
        }

        let feedbackHTML = "";
        if (confirmed && quiz.show_feedback) {
            const isCorrect = this.evaluateAnswer(question, savedAnswer);
            const feedbackText = question.explanation?.es || question.explanation?.en || "";
            const feedbackTextEscaped = this.escapeHTML(feedbackText);
            const feedbackClass = isCorrect ? "quiz-feedback-correct" : "quiz-feedback-incorrect";
            const feedbackLabel = isCorrect ? "Correcto" : "Incorrecto";

            feedbackHTML = `
                <div class="quiz-feedback ${feedbackClass}" style="margin: 1rem 0; padding: 1rem; border-radius: 6px;" aria-live="polite">
                    <strong>${this.escapeHTML(feedbackLabel)}</strong>
                    ${feedbackText ? `<p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; line-height: 1.4;">${feedbackTextEscaped}</p>` : ''}
                </div>
            `;
        }

        const isFirst = session.current_question_index === 0;
        const isLast = session.current_question_index === session.question_order.length - 1;

        let primaryActionBtn = "";
        if (!confirmed) {
            primaryActionBtn = `<button class="btn-primary" data-quiz-action="submit" style="flex: 1;">${this.escapeHTML(this.uiStrings.submit)}</button>`;
        } else {
            if (isLast) {
                primaryActionBtn = `<button class="btn-primary" data-quiz-action="complete" style="flex: 1;">${this.escapeHTML(this.uiStrings.complete)}</button>`;
            } else {
                primaryActionBtn = `<button class="btn-primary" data-quiz-action="next" style="flex: 1;">${this.escapeHTML(this.uiStrings.next)}</button>`;
            }
        }

        let changeBtnHTML = "";
        if (confirmed && !session.completed) {
            changeBtnHTML = `<button class="btn-secondary" data-quiz-action="change-answer" style="margin-right: auto;">${this.escapeHTML(this.uiStrings.changeAnswer)}</button>`;
        }

        const progressIndexEscaped = this.escapeHTML(this.uiStrings.questionIndex.replace('{x}', progress.current).replace('{y}', progress.total));
        const pointsEscaped = this.escapeHTML(String(question.points));
        const promptEscaped = this.escapeHTML(this.normalizeLocalizedText(question.prompt));

        let html = `
            <div class="navigation-header">
                <a href="#/cuestionarios" class="btn-back" data-quiz-action="back-to-list">← ${this.escapeHTML(this.uiStrings.backToList)}</a>
                <h2 class="quiz-question-title" tabindex="-1" style="outline: none;">${this.escapeHTML(this.normalizeLocalizedText(quiz.title))}</h2>
            </div>

            <div class="quiz-question-card card">
                <div class="quiz-progress-container" style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-muted-light); margin-bottom: 0.25rem;">
                        <span>${progressIndexEscaped}</span>
                        <span><strong>Puntos:</strong> ${pointsEscaped}</span>
                    </div>
                    <div class="quiz-progress" style="width: 100%; height: 6px; background-color: var(--primary-bg-light); border-radius: 3px; overflow: hidden;">
                        <div class="quiz-progress-bar" role="progressbar" aria-valuemin="1" aria-valuemax="${this.escapeHTML(String(progress.total))}" aria-valuenow="${this.escapeHTML(String(progress.current))}" aria-valuetext="Pregunta ${this.escapeHTML(String(progress.current))} de ${this.escapeHTML(String(progress.total))}" style="width: ${this.escapeHTML(String(progress.percentage))}%; height: 100%; background-color: var(--primary-medium); transition: width 0.3s ease;">
                        </div>
                    </div>
                </div>

                <h3 class="quiz-question-prompt" tabindex="-1" style="font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; color: var(--primary-medium); line-height: 1.4; outline: none;">
                    ${promptEscaped}
                </h3>

                ${mediaHTML}

                <div id="quiz-options-container">
                    ${optionsHTML}
                </div>

                <div id="quiz-error-message" style="display: none; color: #dc2626; font-size: 0.9rem; margin-bottom: 0.5rem;" aria-live="polite">
                    ${this.escapeHTML(this.uiStrings.selectAnswer)}
                </div>

                ${feedbackHTML}

                <div class="quiz-actions" style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 1.5rem; align-items: center;">
                    <button class="btn-secondary" data-quiz-action="previous" ${isFirst ? 'disabled' : ''}>${this.escapeHTML(this.uiStrings.previous)}</button>
                    ${changeBtnHTML}
                    ${primaryActionBtn}
                </div>
            </div>
        `;

        container.innerHTML = html;

        // Foco accesible al encabezado o prompt de la pregunta actual
        const promptEl = container.querySelector(".quiz-question-prompt");
        if (promptEl) {
            promptEl.focus();
        }

        this.initializeQuizInteractions(container, quiz, session, mediaResources);
        if (typeof MediaViewer !== "undefined") {
            MediaViewer.initializeMediaInteractions(container);
        }
    },

    renderQuizSummary(container, quiz, session) {
        if (!container || !session) return;

        const scoreData = this.calculateQuizScore(session, quiz);
        const badgeClass = scoreData.passed ? "badge-success" : "badge-error";
        const statusText = scoreData.passed ? this.uiStrings.passed : this.uiStrings.failed;

        const scoreEscaped = this.escapeHTML(String(scoreData.score));
        const earnedEscaped = this.escapeHTML(String(scoreData.earned));
        const maxEscaped = this.escapeHTML(String(scoreData.max));
        const titleEscaped = this.escapeHTML(this.normalizeLocalizedText(quiz.title));
        const passingEscaped = this.escapeHTML(String(quiz.passing_score));
        const attemptEscaped = this.escapeHTML(String(session.attempt_number));
        const correctCountEscaped = this.escapeHTML(String(scoreData.correct_count));
        const totalQuestionsEscaped = this.escapeHTML(String(scoreData.total_questions));

        let html = `
            <div class="navigation-header">
                <a href="#/cuestionarios" class="btn-back" data-quiz-action="back-to-list">← ${this.escapeHTML(this.uiStrings.backToList)}</a>
                <h2>${this.escapeHTML(this.uiStrings.result)}: ${titleEscaped}</h2>
            </div>

            <div class="quiz-summary card">
                <div style="text-align: center; padding: 1.5rem 0;">
                    <div class="quiz-status ${this.escapeHTML(badgeClass)}" style="display: inline-block; padding: 0.4rem 1rem; border-radius: 20px; font-weight: bold; font-size: 1.2rem; margin-bottom: 1rem;">
                        ${this.escapeHTML(statusText)}
                    </div>
                    <div class="quiz-score" style="font-size: 3rem; font-weight: 800; color: var(--primary-medium); line-height: 1;">
                        ${scoreEscaped}%
                    </div>
                    <p style="margin-top: 0.5rem; color: var(--text-muted-light); font-size: 0.95rem;">
                        Puntos obtenidos: <strong>${earnedEscaped}</strong> de <strong>${maxEscaped}</strong>
                    </p>
                </div>

                <div style="margin: 1.5rem 0; padding: 1rem; background-color: var(--primary-bg-light); border-radius: 6px; font-size: 0.9rem; line-height: 1.5; color: var(--text-main-light);">
                    <ul style="margin: 0; padding-left: 1.25rem;">
                        <li><strong>Cuestionario:</strong> ${titleEscaped}</li>
                        <li><strong>Respuestas correctas:</strong> ${correctCountEscaped} de ${totalQuestionsEscaped}</li>
                        <li><strong>Nota de aprobación requerida:</strong> ${passingEscaped}%</li>
                        <li><strong>Intento número:</strong> ${attemptEscaped}</li>
                    </ul>
                </div>

                <div class="quiz-disclaimer" style="margin: 1.5rem 0; font-size: 0.8rem; font-style: italic; color: var(--text-muted-light); line-height: 1.4;">
                    ${this.escapeHTML(this.uiStrings.educationalDisclaimer)}
                </div>

                <div class="quiz-actions" style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 1.5rem;">
                    ${quiz.allow_retry !== false ? `
                    <button class="btn-primary" data-quiz-action="restart" style="flex: 1; min-width: 150px;">${this.escapeHTML(this.uiStrings.retry)}</button>
                    ` : ''}
                    <a href="#/cuestionarios" class="btn-secondary" style="flex: 1; min-width: 150px; display: inline-flex; align-items: center; justify-content: center; text-decoration: none;" data-quiz-action="back-to-list">
                        ${this.escapeHTML(this.uiStrings.backToList)}
                    </a>
                </div>
            </div>
        `;

        container.innerHTML = html;
        this.initializeQuizInteractions(container, quiz, session);
    },

    initializeQuizInteractions(container, quiz, session, mediaResources = []) {
        if (!container) return;

        const actionButtons = container.querySelectorAll("[data-quiz-action]");
        actionButtons.forEach(btn => {
            btn.addEventListener("click", (e) => {
                const action = btn.getAttribute("data-quiz-action");
                const targetQuizId = btn.getAttribute("data-quiz-id") || (quiz ? quiz.id : null);
                if (!targetQuizId) return;

                if (action === "back-to-list") {
                    window.location.hash = "#/cuestionarios";
                    return;
                }

                // Operar localmente en lugar de confiar en Router
                if (action === "start") {
                    let activeSession = this.restoreQuizSession(quiz, targetQuizId);
                    if (!activeSession) {
                        activeSession = this.createQuizSession(quiz);
                        this.saveQuizSession(activeSession);
                    }
                    this.refreshQuizView(container, quiz, activeSession, mediaResources);
                } else if (action === "restart") {
                    const activeSession = this.restoreQuizSession(quiz, targetQuizId);
                    const newSession = this.restartQuiz(activeSession, quiz);
                    this.refreshQuizView(container, quiz, newSession, mediaResources);
                } else if (action === "change-answer") {
                    if (session && quiz) {
                        const question = this.getCurrentQuestion(session, quiz);
                        if (question) {
                            session.confirmed_answers[question.id] = false;
                            this.saveQuizSession(session);
                            this.renderQuizQuestion(container, quiz, session, question, mediaResources);
                        }
                    }
                } else if (action === "submit") {
                    if (session && quiz) {
                        const question = this.getCurrentQuestion(session, quiz);
                        if (question) {
                            const inputs = container.querySelectorAll(`input[name="question-${question.id}"]:checked`);
                            if (inputs.length === 0) {
                                const errEl = container.querySelector("#quiz-error-message");
                                if (errEl) errEl.style.display = "block";

                                // A11y: Foco al primer elemento interactivo o legend al haber error
                                const legendEl = container.querySelector(".quiz-legend");
                                if (legendEl) legendEl.focus();
                                return;
                            }

                            let answerVal = null;
                            if (question.type === 'single_choice' || question.type === 'true_false') {
                                answerVal = inputs[0].getAttribute("data-option-id");
                            } else {
                                answerVal = Array.from(inputs).map(inp => inp.getAttribute("data-option-id"));
                            }

                            const ok = this.submitAnswer(session, question, answerVal);
                            if (ok) {
                                this.renderQuizQuestion(container, quiz, session, question, mediaResources);
                            }
                        }
                    }
                } else if (action === "next") {
                    if (session && quiz) {
                        this.goToNextQuestion(session, quiz);
                        const question = this.getCurrentQuestion(session, quiz);
                        this.renderQuizQuestion(container, quiz, session, question, mediaResources);
                    }
                } else if (action === "previous") {
                    if (session && quiz) {
                        this.goToPreviousQuestion(session, quiz);
                        const question = this.getCurrentQuestion(session, quiz);
                        this.renderQuizQuestion(container, quiz, session, question, mediaResources);
                    }
                } else if (action === "complete") {
                    if (session && quiz) {
                        this.completeQuiz(session, quiz);
                        this.renderQuizSummary(container, quiz, session);
                    }
                }
            });
        });
    }
};
