"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import styles from "./login.module.scss";
import Image from "next/image";
import Icon from "@/shared/icons/Icon";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const role = searchParams.get("role") || "student"; // student | teacher

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setError("");

    // Мини-валидация
    if (!email.trim() || !password.trim()) {
      setError("Заполните почту и пароль");
      return;
    }

    try {
      setLoading(true);

      // ВАЖНО: бек ждёт form-data: username + password :contentReference[oaicite:2]{index=2}
      const form = new URLSearchParams();
      form.set("username", email.trim());
      form.set("password", password);

      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: form.toString(),
      });

      if (!res.ok) {
        // FastAPI часто возвращает { detail: "..." }
        let detail = "Ошибка входа";
        try {
          const data = await res.json();
          if (data?.detail) detail = data.detail;
        } catch (_) {}

        if (res.status === 401) detail = detail || "Неверная почта или пароль";
        throw new Error(detail);
      }

      const data = await res.json();
      // { access_token, token_type } :contentReference[oaicite:3]{index=3}
      const token = data?.access_token;
      if (!token) throw new Error("Токен не получен");

      // Сохраняем токен и роль (для MVP достаточно localStorage)
      localStorage.setItem("access_token", token);
      localStorage.setItem("token_type", data?.token_type || "bearer");
      localStorage.setItem("role", role);

      // Роутинг: подстрой под свои реальные страницы
      // (сейчас у тебя есть (student)/page.js — значит логично туда)
      router.push(role === "teacher" ? "/teacher" : "/");
    } catch (err) {
      setError(err?.message || "Ошибка входа");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.inner}>
      <div className={styles.bilimPath}>
        <div className={styles.logo}>
          <Image
            src="/imgs/logo.png"
            alt="BilimPath Logo"
            className={styles.logoImg}
            width={50}
            height={53}
            priority
          />
          <span className={styles.logoTxt}>BilimPath AI</span>
        </div>
        <p className={styles.description}>
          AI-наставник для персонального обучения
        </p>
      </div>

      <div className={`${styles.card} border-gradient`}>
        <h1 className={styles.title}>Логин</h1>

        <form className={styles.form} onSubmit={onSubmit}>
          <div className={styles.inputs}>
            <div className={styles.inputWrapper}>
              <Icon name="user" size={30} className={styles.inputIcon} />
              <input
                className={styles.input}
                placeholder="Введите почту"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>

            <div className={styles.inputWrapper}>
              <Icon name="lock" size={30} className={styles.inputIcon} />
              <input
                className={styles.input}
                placeholder="Введите пароль"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
            </div>
          </div>

          {error && <p className={styles.error}>{error}</p>}

          <div className={styles.buttons}>
            <p className={styles.forgotPass}>Забыли пароль?</p>

            <button className="btn" type="submit" disabled={loading}>
              {loading ? "Вход..." : "Войти"}
            </button>

            <button
              className="btn-primary border-gradient"
              type="button"
              onClick={() => router.push("/register")}
            >
              Зарегистрироваться
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
