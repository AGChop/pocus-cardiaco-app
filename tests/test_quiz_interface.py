import subprocess
import tempfile
import os
import json
import re
import pytest
import urllib.request

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def run_js_in_chrome(js_payload):
    # Read quiz-engine.js code
    with open("assets/js/quiz-engine.js", "r", encoding="utf-8") as f:
        quiz_engine_code = f.read()

    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body>
    <div id="results"></div>
    <script>
        // Mock Storage
        const _storage = {};
        const Storage = {
            getProgress: (type, id) => _storage[type + "_" + id] || null,
            saveProgress: (type, id, data) => { _storage[type + "_" + id] = data; },
            removeProgress: (type, id) => { delete _storage[type + "_" + id]; }
        };

        // Mock MediaViewer
        const MediaViewer = {
            renderMediaSection: (media) => "<div>MOCK_MEDIA</div>",
            initializeMediaInteractions: (container) => {}
        };

        // Mock DataLoader
        const DataLoader = {
            getQuizzes: async () => [],
            getMediaResources: async () => []
        };

        // Inject QuizEngine
        //QUIZ_ENGINE_CODE//

        // Run user payload synchronously
        try {
            const resultsEl = document.getElementById("results");
            const res = (() => {
                //JS_PAYLOAD//
            })();
            resultsEl.textContent = JSON.stringify({ success: true, data: res });
        } catch (e) {
            document.getElementById("results").textContent = JSON.stringify({ success: false, error: e.message });
        } finally {
            window.close();
        }
    </script>
</body>
</html>
""".replace("//QUIZ_ENGINE_CODE//", quiz_engine_code).replace("//JS_PAYLOAD//", js_payload)

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8", dir="./") as tmp:
        tmp.write(html_content)
        tmp_path = tmp.name

    with tempfile.TemporaryDirectory(dir="./") as user_data_dir:
        try:
            cmd = [
                CHROME_PATH,
                "--headless",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--no-sandbox",
                "--incognito",
                "--allow-file-access-from-files",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--disable-sync",
                "--disable-background-networking",
                "--disable-component-update",
                "--password-store=basic",
                "--use-mock-keychain",
                f"--user-data-dir={os.path.abspath(user_data_dir)}",
                "--dump-dom",
                "file://" + urllib.request.pathname2url(os.path.abspath(tmp_path))
            ]
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
                stdin=subprocess.DEVNULL
            )

            if res.returncode != 0:
                pytest.fail(
                    f"Chrome execution failed with returncode {res.returncode}.\n"
                    f"STDOUT:\n{res.stdout}\n"
                    f"STDERR:\n{res.stderr}"
                )

            match = re.search(r'<div id="results">(.*?)</div>', res.stdout)
            if match:
                return json.loads(match.group(1))
            else:
                return {"success": False, "error": "No results div found", "output": res.stdout}
        except subprocess.TimeoutExpired as e:
            # e.stdout and e.stderr might be bytes or None in some Python versions if timeout occurs before stdout/stderr decode.
            # We safely handle bytes decoding.
            out_decoded = e.stdout.decode('utf-8', errors='replace') if isinstance(e.stdout, bytes) else str(e.stdout)
            err_decoded = e.stderr.decode('utf-8', errors='replace') if isinstance(e.stderr, bytes) else str(e.stderr)
            pytest.fail(
                f"Chrome headless excedió el tiempo máximo de 20 segundos.\n"
                f"STDOUT parcial:\n{out_decoded}\n"
                f"STDERR parcial:\n{err_decoded}"
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

def test_quiz_definition_validation_headless():
    payload = """
    const validQuiz = {
        id: "quiz-1",
        title: { es: "Cuestionario de prueba", en: "Test Quiz" },
        description: { es: "Descripcion", en: "Description" },
        passing_score: 80,
        difficulty: "beginner",
        estimated_minutes: 5,
        review_status: "approved",
        questions: [
            {
                id: "q-1",
                type: "single_choice",
                prompt: { es: "Pregunta 1", en: "Question 1" },
                points: 10,
                options: [
                    { id: "opt-a", text: { es: "Opcion A", en: "Option A" } },
                    { id: "opt-b", text: { es: "Opcion B", en: "Option B" } }
                ],
                correct_answer: "opt-a"
            }
        ]
    };

    const isVal1 = QuizEngine.validateQuizDefinition(validQuiz);

    // Sin points
    const invalidQuizNoPoints = JSON.parse(JSON.stringify(validQuiz));
    delete invalidQuizNoPoints.questions[0].points;
    const isVal2 = QuizEngine.validateQuizDefinition(invalidQuizNoPoints);

    // IDs de preguntas duplicados
    const invalidQuizDupIds = JSON.parse(JSON.stringify(validQuiz));
    invalidQuizDupIds.questions.push({
        id: "q-1",
        type: "true_false",
        prompt: { es: "Pregunta 2" },
        points: 5,
        correct_answer: true
    });
    const isVal3 = QuizEngine.validateQuizDefinition(invalidQuizDupIds);

    return { isVal1, isVal2, isVal3 };
    """
    res = run_js_in_chrome(payload)
    assert res["success"]
    assert res["data"]["isVal1"] is True
    assert res["data"]["isVal2"] is False
    assert res["data"]["isVal3"] is False

def test_answer_validation_and_scoring_headless():
    payload = """
    const quiz = {
        id: "quiz-1",
        title: { es: "Test" },
        passing_score: 70,
        questions: [
            {
                id: "q-1",
                type: "single_choice",
                points: 15,
                prompt: { es: "Pregunta 1" },
                options: [{ id: "opt-a", text: { es: "A" } }, { id: "opt-b", text: { es: "B" } }],
                correct_answer: "opt-a"
            },
            {
                id: "q-2",
                type: "multiple_choice",
                points: 20,
                prompt: { es: "Pregunta 2" },
                options: [{ id: "opt-c", text: { es: "C" } }, { id: "opt-d", text: { es: "D" } }],
                correct_answer: ["opt-c", "opt-d"]
            },
            {
                id: "q-3",
                type: "true_false",
                points: 10,
                prompt: { es: "Pregunta 3" },
                correct_answer: true
            }
        ]
    };

    // Validar respuestas
    const v1 = QuizEngine.validateSubmittedAnswer(quiz.questions[0], "opt-a"); // true
    const v2 = QuizEngine.validateSubmittedAnswer(quiz.questions[0], "opt-z"); // false (no existe)
    const v3 = QuizEngine.validateSubmittedAnswer(quiz.questions[1], ["opt-c", "opt-d"]); // true
    const v4 = QuizEngine.validateSubmittedAnswer(quiz.questions[1], ["opt-c", "opt-c"]); // false (duplicados)
    const v5 = QuizEngine.validateSubmittedAnswer(quiz.questions[2], true); // true

    // Crear sesion
    const session = QuizEngine.createQuizSession(quiz);

    // Contestar
    QuizEngine.submitAnswer(session, quiz.questions[0], "opt-a");
    QuizEngine.submitAnswer(session, quiz.questions[1], ["opt-c", "opt-d"]);
    QuizEngine.submitAnswer(session, quiz.questions[2], false); // Incorrecta

    const scoreData = QuizEngine.calculateQuizScore(session, quiz);

    return { v1, v2, v3, v4, v5, scoreData };
    """
    res = run_js_in_chrome(payload)
    assert res["success"]
    data = res["data"]
    assert data["v1"] is True
    assert data["v2"] is False
    assert data["v3"] is True
    assert data["v4"] is False
    assert data["v5"] is True

    score = data["scoreData"]
    assert score["max"] == 45
    assert score["earned"] == 35
    assert score["score"] == 78
    assert score["correct_count"] == 2
    assert score["passed"] is True

def test_session_restoration_and_corruption_headless():
    payload = """
    const quiz = {
        id: "quiz-1",
        title: { es: "Test" },
        passing_score: 50,
        questions: [
            {
                id: "q-1",
                type: "single_choice",
                points: 10,
                prompt: { es: "Pregunta 1" },
                options: [{ id: "opt-a", text: { es: "A" } }, { id: "opt-b", text: { es: "B" } }],
                correct_answer: "opt-a"
            }
        ]
    };

    const validSession = {
        quiz_id: "quiz-1",
        schema_version: "1.0",
        started_at: Date.now(),
        updated_at: Date.now(),
        current_question_index: 0,
        question_order: ["q-1"],
        answers_by_question_id: {},
        confirmed_answers: {},
        attempt_number: 1,
        completed: false
    };

    // Guardar sesion valida
    Storage.saveProgress("quiz", "quiz-1", validSession);
    const r1 = QuizEngine.restoreQuizSession(quiz, "quiz-1");

    // Corrupta: Index decimal
    const s2 = JSON.parse(JSON.stringify(validSession));
    s2.current_question_index = 0.5;
    Storage.saveProgress("quiz", "quiz-1", s2);
    const r2 = QuizEngine.restoreQuizSession(quiz, "quiz-1");

    // Corrupta: Order vacio
    const s3 = JSON.parse(JSON.stringify(validSession));
    s3.question_order = [];
    Storage.saveProgress("quiz", "quiz-1", s3);
    const r3 = QuizEngine.restoreQuizSession(quiz, "quiz-1");

    return { r1: !!r1, r2: !!r2, r3: !!r3 };
    """
    res = run_js_in_chrome(payload)
    assert res["success"]
    assert res["data"]["r1"] is True
    assert res["data"]["r2"] is False
    assert res["data"]["r3"] is False

def test_randomization_fisher_yates_headless():
    payload = """
    const questionIds = ["q1", "q2", "q3", "q4", "q5"];

    // Stub determinista de Math.random que siempre retorna un valor fijo
    const order1 = QuizEngine.shuffleQuestionOrder(questionIds, () => 0.1);
    const order2 = QuizEngine.shuffleQuestionOrder(questionIds, () => 0.8);

    return { order1, order2 };
    """
    res = run_js_in_chrome(payload)
    assert res["success"]
    assert res["data"]["order1"] != res["data"]["order2"]
    assert len(res["data"]["order1"]) == 5

def test_completion_and_retry_limits_headless():
    payload = """
    const quiz = {
        id: "quiz-1",
        title: { es: "Test" },
        passing_score: 50,
        allow_retry: false,
        questions: [
            {
                id: "q-1",
                type: "single_choice",
                points: 10,
                prompt: { es: "Pregunta 1" },
                options: [{ id: "opt-a", text: { es: "A" } }, { id: "opt-b", text: { es: "B" } }],
                correct_answer: "opt-a"
            }
        ]
    };

    const session = QuizEngine.createQuizSession(quiz);

    // Intenta completar sin responder
    const c1 = QuizEngine.completeQuiz(session, quiz); // null

    // Responde y completa
    QuizEngine.submitAnswer(session, quiz.questions[0], "opt-a");
    const c2 = QuizEngine.completeQuiz(session, quiz); // object score

    // Intenta reintentar con allow_retry = false
    const restartResult = QuizEngine.restartQuiz(session, quiz); // null

    return { c1: !!c1, c2: !!c2, restartResult: !!restartResult };
    """
    res = run_js_in_chrome(payload)
    assert res["success"]
    assert res["data"]["c1"] is False
    assert res["data"]["c2"] is True
    assert res["data"]["restartResult"] is False

def test_xss_protection_headless():
    payload = """
    const quiz = {
        id: "quiz-1",
        title: { es: "<script>document.documentElement.dataset.xssTitle = 'executed'</" + "script>" },
        description: { es: "<img src=\\"invalid\\" onerror=\\"document.documentElement.dataset.xssImage='executed'\\">" },
        passing_score: 50,
        review_status: "approved",
        questions: [
            {
                id: "q-1",
                type: "single_choice",
                points: 10,
                prompt: { es: "<script>document.documentElement.dataset.xssPrompt = 'executed'</" + "script>" },
                options: [
                    { id: "opt-a", text: { es: "<script>document.documentElement.dataset.xssOptA = 'executed'</" + "script>" } },
                    { id: "opt-b", text: { es: "B" } }
                ],
                correct_answer: "opt-a",
                explanation: { es: "<script>document.documentElement.dataset.xssExpl = 'executed'</" + "script>" }
            }
        ]
    };

    const container = document.createElement("div");
    QuizEngine.renderQuizList(container, [quiz]);
    const listHasScript = container.querySelector("script") !== null;
    const listHasImg = container.querySelector("img") !== null;
    const listHTML = container.innerHTML;

    const session = QuizEngine.createQuizSession(quiz);
    QuizEngine.renderQuizQuestion(container, quiz, session, quiz.questions[0]);
    const questionHasScript = container.querySelector("script") !== null;
    const questionHasImg = container.querySelector("img") !== null;

    // Check dataset execution marks
    const dataset = document.documentElement.dataset;
    const xssTitleExecuted = dataset.xssTitle === "executed";
    const xssImageExecuted = dataset.xssImage === "executed";
    const xssPromptExecuted = dataset.xssPrompt === "executed";
    const xssOptAExecuted = dataset.xssOptA === "executed";
    const xssExplExecuted = dataset.xssExpl === "executed";

    // Check active onerror attribute in parsed elements
    let hasActiveOnError = false;
    container.querySelectorAll("*").forEach(el => {
        if (el.hasAttribute("onerror") || el.onerror !== null) {
            hasActiveOnError = true;
        }
    });

    return {
        listHasScript,
        listHasImg,
        questionHasScript,
        questionHasImg,
        xssTitleExecuted,
        xssImageExecuted,
        xssPromptExecuted,
        xssOptAExecuted,
        xssExplExecuted,
        hasActiveOnError,
        listHTML
    };
    """
    res = run_js_in_chrome(payload)
    assert res["success"]
    data = res["data"]
    assert data["listHasScript"] is False
    assert data["listHasImg"] is False
    assert data["questionHasScript"] is False
    assert data["questionHasImg"] is False
    assert data["xssTitleExecuted"] is False
    assert data["xssImageExecuted"] is False
    assert data["xssPromptExecuted"] is False
    assert data["xssOptAExecuted"] is False
    assert data["xssExplExecuted"] is False
    assert data["hasActiveOnError"] is False
    assert "&amp;lt;script&amp;gt;" in data["listHTML"]

def test_static_verifications():
    # Rutas e i18n
    with open("assets/js/router.js", "r", encoding="utf-8") as f:
        router_content = f.read()
    assert "#/cuestionarios" in router_content

    # Cache v17
    with open("service-worker.js", "r", encoding="utf-8") as f:
        sw_content = f.read()
    assert "pocus-cardiaco-cache-v17" in sw_content

def test_analytics_is_disabled_strictly():
    with open("assets/js/analytics.js", "r", encoding="utf-8") as f:
        analytics_code = f.read()

    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body>
    <div id="results"></div>
    <script>
        const Storage = {
            getPreference: (key, defVal) => defVal
        };
        //ANALYTICS_CODE//
        try {
            const res = Analytics.isAnalyticsEnabled();
            document.getElementById("results").textContent = JSON.stringify({ success: true, enabled: res });
        } catch(e) {
            document.getElementById("results").textContent = JSON.stringify({ success: false, error: e.message });
        }
    </script>
</body>
</html>
""".replace("//ANALYTICS_CODE//", analytics_code)

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8", dir="./") as tmp:
        tmp.write(html_content)
        tmp_path = tmp.name

    out_tmp_path = None
    with tempfile.NamedTemporaryFile(suffix=".log", delete=False, mode="w", encoding="utf-8", dir="./") as out_tmp:
        out_tmp_path = out_tmp.name

    with tempfile.TemporaryDirectory(dir="./") as user_data_dir:
        try:
            cmd = [
                CHROME_PATH,
                "--headless=old",
                "--disable-gpu",
                "--no-sandbox",
                "--allow-file-access-from-files",
                "--virtual-time-budget=3000",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--disable-sync",
                "--disable-background-networking",
                "--disable-component-update",
                "--password-store=basic",
                "--use-mock-keychain",
                f"--user-data-dir={os.path.abspath(user_data_dir)}",
                "--dump-dom",
                "file://" + urllib.request.pathname2url(os.path.abspath(tmp_path))
            ]
            with open(out_tmp_path, "w", encoding="utf-8") as out_f:
                process = subprocess.Popen(cmd, stdout=out_f, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
                import time
                start_time = time.time()
                stdout_content = ""
                success = False
                while time.time() - start_time < 5.0:
                    if os.path.exists(out_tmp_path):
                        with open(out_tmp_path, "r", encoding="utf-8") as r_f:
                            stdout_content = r_f.read()
                        if '<div id="results">' in stdout_content:
                            success = True
                            break
                    time.sleep(0.1)
                process.kill()
                process.wait()

            if not success:
                pytest.fail(f"Chrome timed out or failed to output results. Output: {stdout_content}")

            match = re.search(r'<div id="results">(.*?)</div>', stdout_content)
            assert match is not None
            result_data = json.loads(match.group(1))
            assert result_data["success"] is True
            assert result_data["enabled"] is False
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            if out_tmp_path and os.path.exists(out_tmp_path):
                os.remove(out_tmp_path)
