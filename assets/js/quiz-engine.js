// Motor de Cuestionarios Educativos de POCUS Cardíaco
const QuizEngine = {
    // 1. Obtener cuestionario por ID
    getQuizById(quizzes, quizId) {
        if (!Array.isArray(quizzes)) return null;
        return quizzes.find(q => q.id === quizId) || null;
    },

    // 2. Validación defensiva de la estructura de un cuestionario
    validateQuizDefinition(quiz) {
        if (!quiz || typeof quiz !== 'object') return false;
        if (typeof quiz.id !== 'string' || !quiz.id) return false;
        if (!quiz.title || typeof quiz.title !== 'object') return false;
        if (typeof quiz.passing_score !== 'number' || quiz.passing_score < 0 || quiz.passing_score > 100) return false;
        if (!Array.isArray(quiz.questions)) return false;

        // Validar cada pregunta
        for (const q of quiz.questions) {
            if (!q || typeof q !== 'object') return false;
            if (typeof q.id !== 'string' || !q.id) return false;
            if (typeof q.type !== 'string' || !q.type) return false;
            if (!q.prompt || typeof q.prompt !== 'object') return false;
            if (q.points !== undefined && (typeof q.points !== 'number' || q.points < 0)) return false;
        }

        return true;
    },

    // 3. Crear una nueva sesión de cuestionario
    createQuizSession(quiz) {
        if (!this.validateQuizDefinition(quiz)) return null;

        let questionOrder = quiz.questions.map(q => q.id);
        if (quiz.randomize_questions) {
            questionOrder = [...questionOrder].sort(() => Math.random() - 0.5);
        }

        return {
            quiz_id: quiz.id,
            schema_version: "1.0",
            started_at: Date.now(),
            updated_at: Date.now(),
            current_question_index: 0,
            question_order: questionOrder,
            answers_by_question_id: {},
            earned_points: 0,
            maximum_points: quiz.questions.reduce((sum, q) => sum + (q.points || 0), 0),
            completed: false,
            attempt_number: 1
        };
    },

    // 4. Restaurar una sesión guardada desde el almacenamiento local
    restoreQuizSession(quizId) {
        if (typeof Storage === "undefined") return null;
        const session = Storage.getProgress('quiz', quizId);
        if (session && session.quiz_id === quizId && session.schema_version === "1.0") {
            return session;
        }
        return null;
    },

    // 5. Guardar la sesión actual en el almacenamiento local
    saveQuizSession(session) {
        if (!session || !session.quiz_id) return false;
        session.updated_at = Date.now();
        if (typeof Storage !== "undefined") {
            Storage.saveProgress('quiz', session.quiz_id, session);
            return true;
        }
        return false;
    },

    // 6. Evaluar la respuesta para una pregunta específica
    evaluateAnswer(question, answer) {
        if (!question || !question.type) return false;

        switch (question.type) {
            case 'single_choice':
            case 'true_false':
                return answer === question.correct_answer;

            case 'multiple_choice':
                const correct = Array.isArray(question.correct_answer) ? question.correct_answer : [];
                const submitted = Array.isArray(answer) ? answer : [];
                if (correct.length !== submitted.length) return false;
                return correct.every(item => submitted.includes(item)) && submitted.every(item => correct.includes(item));

            default:
                console.warn(`QuizEngine: Tipo de pregunta '${question.type}' no soportado para evaluación.`);
                return false;
        }
    },

    // 7. Enviar la respuesta para la pregunta actual
    submitAnswer(session, question, answer) {
        if (!session || !question) return false;

        // Registrar la respuesta en la sesión
        session.answers_by_question_id[question.id] = answer;

        // Recalcular puntos acumulados
        let earned = 0;
        const quizQuestions = session.questions_cache || [];
        // Nota: para pruebas o persistencia simple, podemos buscar en un repositorio o pasar las preguntas
        // Pero para mantener la función pura y desacoplada, evaluamos directamente aquí:
        const isCorrect = this.evaluateAnswer(question, answer);
        if (isCorrect) {
            // Buscaremos los puntos correspondientes a la pregunta
            earned = question.points || 0;
        }

        // Sumar o restar la diferencia de puntos si ya se había contestado antes
        // Para simplificar, acumulamos recorriendo las respuestas si es posible, o actualizando la sesión.
        // Vamos a guardar si es correcta o no para calcular el puntaje después
        this.saveQuizSession(session);
        return isCorrect;
    },

    // 8. Calcular el puntaje final y estado de aprobación del cuestionario
    calculateQuizScore(session, quiz) {
        if (!session || !quiz) return { score: 0, passed: false };

        let earned = 0;
        let max = 0;

        quiz.questions.forEach(q => {
            const points = q.points || 0;
            max += points;
            const ans = session.answers_by_question_id[q.id];
            if (ans !== undefined && this.evaluateAnswer(q, ans)) {
                earned += points;
            }
        });

        session.earned_points = earned;
        session.maximum_points = max;

        const score = max > 0 ? Math.round((earned / max) * 100) : 0;
        const passed = score >= (quiz.passing_score || 0);

        return { score, passed };
    },

    // 9. Completar el cuestionario
    completeQuiz(session, quiz) {
        if (!session || !quiz) return null;
        session.completed = true;
        const result = this.calculateQuizScore(session, quiz);
        this.saveQuizSession(session);
        return result;
    },

    // 10. Reiniciar el cuestionario
    restartQuiz(session, quiz) {
        if (!quiz) return null;
        const newSession = this.createQuizSession(quiz);
        if (newSession && session) {
            newSession.attempt_number = (session.attempt_number || 1) + 1;
        }
        if (newSession) {
            this.saveQuizSession(newSession);
        }
        return newSession;
    },

    // --- MÉTODOS DE RENDERIZADO (FASE FUTURA / CAPA NO OPERATIVA) ---
    renderQuizList(container, quizzes) {
        if (!container) return;
        container.innerHTML = `<div class="quiz-list-placeholder">Infraestructura de cuestionarios cargada.</div>`;
    },

    renderQuizDetail(container, quiz, session) {
        if (!container) return;
        container.innerHTML = `<div class="quiz-detail-placeholder">Cuestionario: ${quiz.title?.es || quiz.id}</div>`;
    },

    renderQuizQuestion(container, quiz, session, question) {
        if (!container) return;
        container.innerHTML = `<div class="quiz-question-placeholder">Pregunta: ${question.prompt?.es || question.id}</div>`;
    },

    renderQuizSummary(container, quiz, session) {
        if (!container) return;
        container.innerHTML = `<div class="quiz-summary-placeholder">Resultados del cuestionario.</div>`;
    },

    initializeQuizInteractions(container, quiz, session) {
        // Inicialización de escuchas de eventos (vacío por diseño en esta fase no visual)
        return true;
    }
};
