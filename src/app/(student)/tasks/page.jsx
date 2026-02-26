"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import styles from "./tasks.module.scss";
import Icon from "@/shared/icons/Icon";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

function clamp(n, min, max) {
  return Math.max(min, Math.min(max, n));
}

function masteryColor(m) {
  // 0-100
  if (m >= 75) return "green";
  if (m >= 50) return "orange";
  return "red";
}

export default function TasksPage() {
  const router = useRouter();

  const [loading, setLoading] = useState(true);
  const [subjects, setSubjects] = useState([]);
  const [error, setError] = useState("");

  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("none"); // none | asc | desc

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
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) {
          let detail = "Ошибка загрузки предметов";
          try {
            const data = await res.json();
            if (data?.detail) detail = data.detail;
          } catch (_) {}
          throw new Error(detail);
        }

        const data = await res.json(); // SubjectProgress[] :contentReference[oaicite:2]{index=2}
        setSubjects(Array.isArray(data) ? data : []);
      } catch (e) {
        setError(e?.message || "Ошибка");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [router]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();

    let list = subjects.map((s) => {
      const topics = Array.isArray(s.topics) ? s.topics : [];
      const avg =
        topics.length === 0
          ? null
          : Math.round(
              topics.reduce(
                (sum, t) => sum + (Number(t.mastery_level) || 0),
                0,
              ) / topics.length,
            );

      return {
        id: s.subject_id,
        name: s.name,
        mastery: avg, // может быть null
      };
    });

    if (q) {
      list = list.filter((s) => s.name.toLowerCase().includes(q));
    }

    if (sort !== "none") {
      const dir = sort === "asc" ? 1 : -1;
      list = [...list].sort((a, b) => {
        const am = a.mastery ?? -1;
        const bm = b.mastery ?? -1;
        return (am - bm) * dir;
      });
    }

    return list;
  }, [subjects, query, sort]);

  const toggleSort = () => {
    setSort((prev) => {
      if (prev === "none") return "desc"; // сначала сильные
      if (prev === "desc") return "asc"; // потом слабые
      return "none";
    });
  };

  const sortLabel = sort === "none" ? "—" : sort === "desc" ? "↓" : "↑";

  return (
    <div className={styles.page}>
      <div className={styles.headerRow}>
        <h1 className={styles.title}>Выберите Предмет</h1>

        <div className={`${styles.userBadge} border-gradient`}>
          <div className={styles.avatar} />
          <div className={styles.userText}>
            <div className={styles.userName}>Нурдаулет Б.</div>
            <div className={styles.userRole}>Студент</div>
          </div>
          <div className={styles.chev}>▾</div>
        </div>
      </div>

      <div className={styles.controls}>
        <div className={`${styles.search} border-gradient`}>
          <input
            className={styles.searchInput}
            placeholder="Поиск"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <span className={styles.searchIcon}>
            <Icon name="search" size={22} />
          </span>
        </div>

        <button
          type="button"
          className={`${styles.sortBtn} border-gradient`}
          onClick={toggleSort}
          aria-label="Сортировка по уровню"
          title={`Сортировка: ${sort === "none" ? "выкл" : sort === "desc" ? "по убыванию" : "по возрастанию"}`}
        >
          <span className={styles.sortIcon}>
            {/* если нет подходящей иконки — оставим текст */}
            <span className={styles.sortArrow}>{sortLabel}</span>
          </span>
        </button>
      </div>

      {loading && <div className={styles.state}>Загрузка...</div>}
      {error && <div className={styles.stateError}>{error}</div>}

      {!loading && !error && (
        <div className={styles.list}>
          {filtered.map((s) => {
            const m = s.mastery;
            const c = masteryColor(m ?? 0);

            return (
              <button
                key={s.id}
                type="button"
                className={`${styles.item} border-gradient`}
                onClick={() => router.push(`/tasks/${s.id}`)}
              >
                <div className={styles.left}>
                  <div className={`${styles.bullet} border-gradient-circle`} />
                  <div className={styles.name}>{s.name}</div>
                </div>

                {m !== null && (
                  <div className={`${styles.score} ${styles[c]}`}>
                    <div className={styles.scoreNum}>{clamp(m, 0, 100)}</div>
                  </div>
                )}
              </button>
            );
          })}

          {filtered.length === 0 && (
            <div className={styles.state}>Ничего не найдено</div>
          )}
        </div>
      )}
    </div>
  );
}
