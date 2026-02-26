"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import styles from "./topics.module.scss";
import Icon from "@/shared/icons/Icon";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

function masteryColorClass(v, styles) {
  const val = Number(v || 0);
  if (val >= 70) return styles.masteryGreen;
  if (val >= 40) return styles.masteryOrange;
  return styles.masteryRed;
}

export default function TopicsPage() {
  const { subjectId } = useParams();
  const router = useRouter();

  const [loading, setLoading] = useState(true);
  const [subject, setSubject] = useState(null);
  const [query, setQuery] = useState("");
  const [sortDir, setSortDir] = useState("desc"); // desc | asc
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        setError("");

        const token = localStorage.getItem("access_token");
        if (!token) {
          router.replace("/role");
          return;
        }

        const res = await fetch(`${API_BASE}/subjects/my-progress`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) {
          throw new Error("Не удалось загрузить прогресс");
        }

        const data = await res.json();

        const found = (Array.isArray(data) ? data : []).find(
          (s) => String(s.id) === String(subjectId),
        );

        if (!found) {
          throw new Error("Предмет не найден");
        }

        setSubject(found);
      } catch (e) {
        setError(e?.message || "Ошибка");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [router, subjectId]);

  const topics = useMemo(() => {
    const list = subject?.topics ? [...subject.topics] : [];

    // search
    const q = query.trim().toLowerCase();
    const filtered = q
      ? list.filter((t) => (t.title || "").toLowerCase().includes(q))
      : list;

    // sort by mastery
    filtered.sort((a, b) => {
      const av = Number(a.mastery_level || 0);
      const bv = Number(b.mastery_level || 0);
      return sortDir === "desc" ? bv - av : av - bv;
    });

    return filtered;
  }, [query, sortDir, subject]);

  function goExam(topicId) {
    router.push(
      `/tasks/${subjectId}/exam?topicId=${encodeURIComponent(topicId)}`,
    );
  }

  function goAi(topicId) {
    // если у тебя будет AI-страница — замени путь
    router.push(`/ai?topicId=${encodeURIComponent(topicId)}`);
  }

  if (loading) {
    return <div className={styles.page}>Загрузка...</div>;
  }

  if (error) {
    return <div className={styles.page}>{error}</div>;
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Список тем</h1>

      <div className={styles.toolbar}>
        <div className={`${styles.search} border-gradient`}>
          <input
            className={styles.searchInput}
            placeholder="Поиск"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <div className={styles.searchIcon}>
            <Icon name="search" size={22} />
          </div>
        </div>

        <button
          type="button"
          className={`${styles.sortBtn} border-gradient`}
          onClick={() => setSortDir((p) => (p === "desc" ? "asc" : "desc"))}
          title="Сортировка"
        >
          <span className={styles.sortArrow}>
            {sortDir === "desc" ? "↓" : "↑"}
          </span>
        </button>
      </div>

      <div className={styles.list}>
        {topics.map((t, idx) => (
          <div key={t.id} className={`${styles.item} border-gradient`}>
            <div className={styles.itemLeft}>
              <div className={styles.itemTitle}>
                {idx + 1}. {t.title}
              </div>

              <div className={styles.actions}>
                <button
                  className={styles.actionBtn}
                  type="button"
                  onClick={() => goAi(t.id)}
                >
                  Разобраться с ИИ
                </button>
                <button
                  className={styles.actionBtn}
                  type="button"
                  onClick={() => goExam(t.id)}
                >
                  Решить задачи
                </button>
              </div>
            </div>

            <div
              className={`${styles.mastery} ${masteryColorClass(t.mastery_level, styles)}`}
            >
              <span>{Math.round(Number(t.mastery_level || 0))}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
