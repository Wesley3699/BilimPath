"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import styles from "./exam.module.scss";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

function parseCorrectAnswers(questions, answers) {
  return questions.map((q, i) => {
    const selected = answers[i] || null;
    const correct = q.correct_answer;
    const ok = selected && selected === correct;
    return { index: i, question: q.question, ok };
  });
}

export default function ExamPage() {
  const { subjectId } = useParams();
  const router = useRouter();
  const sp = useSearchParams();
  const topicId = sp.get("topicId");

  const [stage, setStage] = useState("loading"); // loading | test | result
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [difficulty] = useState(3); // 1-5 (можешь сделать выбор позже)

  const [examId, setExamId] = useState(null);
  const [topicTitle, setTopicTitle] = useState("");
  const [questions, setQuestions] = useState([]);
  const [current, setCurrent] = useState(0);

  // answers: { [index]: "selected option text" }
  const [answers, setAnswers] = useState({});
  const [backendResult, setBackendResult] = useState(null);

  useEffect(() => {
    if (!topicId) {
      router.replace(`/tasks/${subjectId}`);
      return;
    }

    async function generate() {
      try {
        setStage("loading");
        setError("");

        const token = localStorage.getItem("access_token");
        if (!token) {
          router.replace("/role");
          return;
        }

        // POST /exams/generate { topic_id, difficulty } (1-5)
        const res = await fetch(`${API_BASE}/exams/generate`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ topic_id: topicId, difficulty }),
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
        setExamId(data.exam_id);
        setTopicTitle(data.topic || "");
        setQuestions(Array.isArray(data.questions) ? data.questions : []);
        setAnswers({});
        setCurrent(0);
        setBackendResult(null);
        setStage("test");
      } catch (e) {
        setError(e?.message || "Ошибка");
        setStage("test");
      }
    }

    generate();
  }, [difficulty, router, subjectId, topicId]);

  const total = questions.length || 0;
  const currentQ = questions[current];

  const canFinish = useMemo(() => {
    if (!total) return false;
    return Object.keys(answers).length === total;
  }, [answers, total]);

  function pick(optionText) {
    setAnswers((p) => ({ ...p, [current]: optionText }));
  }

  function prev() {
    setCurrent((p) => Math.max(0, p - 1));
  }

  function next() {
    setCurrent((p) => Math.min(total - 1, p + 1));
  }

  async function submit() {
    try {
      setLoading(true);
      setError("");

      const token = localStorage.getItem("access_token");
      if (!token) {
        router.replace("/role");
        return;
      }

      const payload = {
        answers: questions.map((q, idx) => ({
          question_index: idx,
          selected_option: answers[idx] || "",
        })),
      };

      const res = await fetch(`${API_BASE}/exams/${examId}/submit`, {
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
      setBackendResult(data);
      setStage("result");
    } catch (e) {
      setError(e?.message || "Ошибка");
    } finally {
      setLoading(false);
    }
  }

  const review = useMemo(() => {
    if (!questions.length) return [];
    return parseCorrectAnswers(questions, answers);
  }, [answers, questions]);

  return (
    <div className={styles.page}>
      {error && <div className={styles.error}>{error}</div>}

      {stage === "loading" && <div className={styles.center}>Генерация...</div>}

      {stage === "test" && currentQ && (
        <>
          <div className={styles.headerRow}>
            <div className={styles.leftTitle}>
              <div className={styles.smallTitle}>Задание {current + 1}</div>
              <div className={styles.topic}>{topicTitle}</div>
            </div>
            <div className={styles.counter}>
              {current + 1}/{total}
            </div>
          </div>

          <div className={`${styles.card} border-gradient`}>
            <div className={styles.questionBox}>{currentQ.question}</div>

            <div className={styles.options}>
              {currentQ.options?.map((opt) => {
                const active = answers[current] === opt;
                return (
                  <button
                    key={opt}
                    type="button"
                    className={`${styles.option} ${active ? styles.optionActive : ""}`}
                    onClick={() => pick(opt)}
                  >
                    {opt}
                  </button>
                );
              })}
            </div>

            <div className={styles.navRow}>
              <button
                className={styles.navBtn}
                type="button"
                onClick={prev}
                disabled={current === 0}
              >
                ← Назад
              </button>

              {current < total - 1 ? (
                <button className={styles.navBtn} type="button" onClick={next}>
                  Вперед →
                </button>
              ) : (
                <button
                  className={`${styles.navBtn} ${styles.finishBtn}`}
                  type="button"
                  onClick={submit}
                  disabled={!canFinish || loading}
                >
                  {loading
                    ? "Отправка..."
                    : canFinish
                      ? "Завершить"
                      : "Ответьте на все"}
                </button>
              )}
            </div>
          </div>
        </>
      )}

      {stage === "result" && (
        <div className={styles.result}>
          <h2 className={styles.resultTitle}>Ответы:</h2>

          <div className={styles.resultList}>
            {review.map((r) => (
              <div
                key={r.index}
                className={`${styles.resultItem} border-gradient`}
              >
                <div className={styles.resultText}>
                  {r.index + 1}. {r.question}
                </div>
                <div
                  className={`${styles.badge} ${r.ok ? styles.ok : styles.bad}`}
                >
                  {r.ok ? "✓" : "✕"}
                </div>
              </div>
            ))}
          </div>

          <div className={styles.resultButtons}>
            <button
              className={styles.smallBtn}
              type="button"
              onClick={() =>
                router.replace(
                  `/tasks/${subjectId}/exam?topicId=${encodeURIComponent(topicId)}`,
                )
              }
            >
              Решить еще ↻
            </button>

            <button
              className={styles.smallBtn}
              type="button"
              onClick={() =>
                alert(
                  backendResult?.analysis?.explanation || "Пока нет анализа",
                )
              }
            >
              Разобраться с ИИ 🧠
            </button>
          </div>

          <button
            className={styles.bigBtn}
            type="button"
            onClick={() => router.push(`/tasks/${subjectId}`)}
          >
            К другим темам 📋
          </button>

          {backendResult?.analysis && (
            <div className={`${styles.analysis} border-gradient`}>
              <div className={styles.analysisRow}>
                <div className={styles.analysisScore}>
                  {Math.round(Number(backendResult.score || 0))}%
                </div>
                <div className={styles.analysisMeta}>
                  <div>Правильных: {backendResult.correct_answers}</div>
                  <div className={styles.muted}>
                    Рекомендация: {backendResult.analysis.recommendation}
                  </div>
                </div>
              </div>

              <div className={styles.muted}>
                {backendResult.analysis.explanation}
              </div>
              {!!backendResult.analysis.weak_topics?.length && (
                <div className={styles.weak}>
                  Слабые темы: {backendResult.analysis.weak_topics.join(", ")}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
