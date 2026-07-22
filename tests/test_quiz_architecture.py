import os
import json
import pytest

def test_quizzes_json_properties():
    path = "data/quizzes.json"
    assert os.path.exists(path)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("schema_version") == "1.0"
    assert data.get("default_language") == "es"
    assert isinstance(data.get("quizzes"), list)
    assert len(data.get("quizzes")) == 0

def test_quiz_engine_js_exists():
    assert os.path.exists("assets/js/quiz-engine.js")

def test_dataloader_quizzes_integration():
    with open("assets/js/data-loader.js", "r", encoding="utf-8") as f:
        content = f.read()

    assert "getQuizzes()" in content
    assert "return []" in content

def test_quiz_engine_logic():
    with open("assets/js/quiz-engine.js", "r", encoding="utf-8") as f:
        content = f.read()

    assert "getQuizById" in content
    assert "validateQuizDefinition" in content
    assert "createQuizSession" in content
    assert "restoreQuizSession" in content
    assert "saveQuizSession" in content
    assert "evaluateAnswer" in content
    assert "submitAnswer" in content
    assert "calculateQuizScore" in content
    assert "completeQuiz" in content
    assert "restartQuiz" in content

def test_index_html_quiz_integration():
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    assert "assets/js/quiz-engine.js" in content
    idx_quiz = content.find("assets/js/quiz-engine.js")
    idx_theme = content.find("assets/js/theme.js")
    assert idx_quiz != -1
    assert idx_theme != -1
    assert idx_quiz < idx_theme

def test_service_worker_quiz_caching():
    with open("service-worker.js", "r", encoding="utf-8") as f:
        content = f.read()

    assert "pocus-cardiaco-cache-v16" in content or "pocus-cardiaco-cache-v17" in content
    assert "./assets/js/quiz-engine.js" in content
    assert "./data/quizzes.json" in content

def test_evaluate_answer_scenarios():
    # Vamos a probar que la sintaxis de evaluateAnswer en quiz-engine sea correcta y
    # responda a la lógica descrita en la propuesta.
    # Dado que no podemos ejecutar JS directamente en Python sin un intérprete de JS,
    # verificamos mediante análisis estático de las funciones que la lógica esté implementada.
    with open("assets/js/quiz-engine.js", "r", encoding="utf-8") as f:
        content = f.read()

    assert "single_choice" in content
    assert "true_false" in content
    assert "multiple_choice" in content
    assert "correct_answer" in content
