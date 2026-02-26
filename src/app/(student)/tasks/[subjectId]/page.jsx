"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import styles from "./exam.module.scss";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function SubjectTasksPage() {
  const { subjectId } = useParams();
  const router = useRouter();

  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState("start"); // start | exam | result

  const [difficulty, setDifficulty] = useState("medium"); // easy|medium|hard

  const [subjectName, setSubjectName] = useState("");
  const [exam, setExam] = useState(null); // ExamResponse
  const [answers, setAnswers] = useState({}); // { [questionId]: selectedIndex }
  const [result, setResult] = useState(null); // ExamResult

  const [error, setError] = useState("");

  // Подтянем имя предмета из my-progress (чтобы красиво показать заголовок)
  useEffect(() => {
    async function loadSubject() {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          router.replace("/role");
          return;
        }

        const res = await fetch(`${API_BASE}/subjects/my-progress`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) return;

        const data = await res.json();
        const found = (Array.isArray(data) ? data : []).find(
          (s) => String(s.subject_id) === String(subjectId),
        );
        if (found?.name) setSubjectName(found.name);
      } catch (_) {}
    }

    loadSubject();
  }, [router, subjectId]);

  const questions = useMemo(() => exam?.questions || [], [exam]);

  const canSubmit = useMemo(() => {
    if (!exam) return false;
    if (!questions.length) return false;
    return questions.every((q) => answers[q.id] !== undefined);
  }, [answers, exam, questions]);

  async function generateExam() {
    setError("");
    try {
      setLoading(true);

      const token = localStorage.getItem("access_token");
      if (!token) {
        router.replace("/role");
        return;
      }

      // POST /exams/generate :contentReference[oaicite:0]{index=0}
      const res = await fetch(`${API_BASE}/exams/generate`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          subject_id: Number(subjectId),
          difficulty,
          num_questions: 8,
        }),
      });

      if (!res.ok) {
        let detail = "Ошибка генерации теста";
        try {
          const d = await res.json();
          if (d?.detail) detail = d.detail;
        } catch (_) {}
        throw new Error(detail);
      }

      const data = await res.json();
      setExam(data);
      setAnswers({});
      setResult(null);
      setStage("exam");
    } catch (e) {
      setError(e?.message || "Ошибка");
    } finally {
      setLoading(false);
    }
  }

  function setAnswer(questionId, optionIndex) {
    setAnswers((prev) => ({ ...prev, [questionId]: optionIndex }));
  }

  async function submitExam() {
    setError("");
    try {
      setLoading(true);

      const token = localStorage.getItem("access_token");
      if (!token) {
        router.replace("/role");
        return;
      }

      // POST /exams/submit :contentReference[oaicite:1]{index=1}
      const payload = {
        exam_id: exam.id,
        answers: questions.map((q) => ({
          question_id: q.id,
          selected_option: answers[q.id],
        })),
      };

      const res = await fetch(`${API_BASE}/exams/submit`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        let detail = "Ошибка отправки";
        try {
          const d = await res.json();
          if (d?.detail) detail = d.detail;
        } catch (_) {}
        throw new Error(detail);
      }

      const data = await res.json();
      setResult(data);
      setStage("result");
    } catch (e) {
      setError(e?.message || "Ошибка");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.topRow}>
        <button
          className={styles.back}
          type="button"
          onClick={() => router.push("/tasks")}
        >
          ← Назад
        </button>

        <div className={styles.heading}>
          <h1 className={styles.title}>
            {subjectName ? subjectName : `Предмет #${subjectId}`}
          </h1>
          <p className={styles.sub}>
            {stage === "start"
              ? "Запусти адаптивный тест по предмету"
              : stage === "exam"
                ? "Ответь на все вопросы и отправь результаты"
                : "Готово! Смотри результат и ошибки"}
          </p>
        </div>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {stage === "start" && (
        <div className={`${styles.card} border-gradient`}>
          <div className={styles.row}>
            <div className={styles.block}>
              <div className={styles.label}>Сложность</div>
              <div className={styles.chips}>
                {["easy", "medium", "hard"].map((d) => (
                  <button
                    key={d}
                    type="button"
                    className={`${styles.chip} ${difficulty === d ? styles.chipActive : ""}`}
                    onClick={() => setDifficulty(d)}
                  >
                    {d === "easy"
                      ? "Лёгкая"
                      : d === "medium"
                        ? "Средняя"
                        : "Сложная"}
                  </button>
                ))}
              </div>
            </div>

            <div className={styles.block}>
              <div className={styles.label}>Вопросов</div>
              <div className={styles.value}>8</div>
            </div>
          </div>

          <button
            className={styles.primaryBtn}
            type="button"
            onClick={generateExam}
            disabled={loading}
          >
            {loading ? "Генерация..." : "Сгенерировать тест ▶"}
          </button>
        </div>
      )}

      {stage === "exam" && exam && (
        <div className={styles.exam}>
          {questions.map((q, idx) => (
            <div key={q.id} className={`${styles.qCard} border-gradient`}>
              <div className={styles.qTop}>
                <div className={styles.qNum}>Вопрос {idx + 1}</div>
                {q.topic_title && (
                  <div className={styles.qTopic}>{q.topic_title}</div>
                )}
              </div>

              <div className={styles.qText}>{q.question_text}</div>

              <div className={styles.options}>
                {(q.options || []).map((opt, i) => {
                  const active = answers[q.id] === i;
                  return (
                    <button
                      key={i}
                      type="button"
                      className={`${styles.option} ${active ? styles.optionActive : ""}`}
                      onClick={() => setAnswer(q.id, i)}
                    >
                      <span className={styles.dot} />
                      <span className={styles.optText}>{opt}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}

          <button
            className={styles.primaryBtn}
            type="button"
            onClick={submitExam}
            disabled={!canSubmit || loading}
          >
            {loading
              ? "Отправка..."
              : canSubmit
                ? "Отправить результаты"
                : "Ответьте на все вопросы"}
          </button>
        </div>
      )}

      {stage === "result" && result && (
        <div className={`${styles.card} border-gradient`}>
          <div className={styles.resultTop}>
            <div className={styles.scoreBox}>
              <div className={styles.scoreLabel}>Результат</div>
              <div className={styles.scoreValue}>
                {Math.round(result.score * 100)}%
              </div>
            </div>

            <div className={styles.scoreMeta}>
              <div>
                Правильных: <b>{result.correct_count}</b> /{" "}
                {result.total_questions}
              </div>
              <div className={styles.muted}>
                Точность: {Math.round(result.score * 100)}%
              </div>
            </div>
          </div>

          {!!result?.weak_topics?.length && (
            <div className={styles.weak}>
              <div className={styles.label}>Зоны внимания</div>
              <div className={styles.weakList}>
                {result.weak_topics.slice(0, 3).map((t) => (
                  <div key={t.topic_id} className={styles.weakItem}>
                    <span>{t.topic_title}</span>
                    <span className={styles.muted}>
                      {Math.round(t.mastery_level)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className={styles.actions}>
            <button
              className={styles.primaryBtn}
              type="button"
              onClick={() => setStage("start")}
            >
              Пройти ещё раз
            </button>
            <button
              className={styles.secondaryBtn}
              type="button"
              onClick={() => router.push("/tasks")}
            >
              К предметам
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
