"use client";

import { useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import styles from "./register.module.scss";
import Image from "next/image";
import Icon from "@/shared/icons/Icon";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function RegisterPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // роль можно передавать из role page: /register?role=student|teacher
  const role = useMemo(() => {
    const r = searchParams.get("role");
    return r === "teacher" ? "teacher" : "student";
  }, [searchParams]);

  const codeLabel = role === "teacher" ? "Код учреждения" : "Код группы";
  const codePlaceholder =
    role === "teacher" ? "Введите institution code" : "Введите invite code";

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function registerUser() {
    // /auth/register ожидает поля UserCreate (JSON) :contentReference[oaicite:2]{index=2}
    const payload = {
      email: email.trim(),
      password,
      full_name: fullName.trim(),
      role, // "student" | "teacher" :contentReference[oaicite:3]{index=3}
      ...(role === "teacher"
        ? { institution_code: code.trim() } // required for teachers :contentReference[oaicite:4]{index=4}
        : { invite_code: code.trim() }), // required for students :contentReference[oaicite:5]{index=5}
    };

    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      let detail = "Ошибка регистрации";
      try {
        const data = await res.json();
        if (data?.detail) detail = data.detail;
      } catch (_) {}
      throw new Error(detail);
    }

    return res.json(); // UserResponse :contentReference[oaicite:6]{index=6}
  }

  async function loginAfterRegister() {
    // /auth/login принимает form-data username/password :contentReference[oaicite:7]{index=7}
    const form = new URLSearchParams();
    form.set("username", email.trim());
    form.set("password", password);

    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form.toString(),
    });

    if (!res.ok) {
      let detail = "Регистрация успешна, но вход не выполнен";
      try {
        const data = await res.json();
        if (data?.detail) detail = data.detail;
      } catch (_) {}
      throw new Error(detail);
    }

    return res.json(); // Token {access_token, token_type} :contentReference[oaicite:8]{index=8}
  }

  async function onSubmit(e) {
    e.preventDefault();
    setError("");

    // Мини-валидация
    if (!fullName.trim() || !email.trim() || !password.trim() || !code.trim()) {
      setError("Заполните все поля");
      return;
    }
    if (!email.includes("@")) {
      setError("Введите корректную почту");
      return;
    }
    if (password.length < 6) {
      setError("Пароль должен быть минимум 6 символов");
      return;
    }

    try {
      setLoading(true);

      await registerUser();

      // auto-login (чтобы сразу попасть в продукт)
      const tokenData = await loginAfterRegister();
      const token = tokenData?.access_token;

      if (token) {
        localStorage.setItem("access_token", token);
        localStorage.setItem("token_type", tokenData?.token_type || "bearer");
        localStorage.setItem("role", role);
      }

      // редирект (подстрой под свои реальные страницы)
      router.push(role === "teacher" ? "/teacher" : "/");
    } catch (err) {
      setError(err?.message || "Ошибка регистрации");
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
        <h1 className={styles.title}>Регистрация</h1>

        <form className={styles.form} onSubmit={onSubmit}>
          <div className={styles.inputs}>
            <div className={styles.inputWrapper}>
              <Icon name="user" size={26} className={styles.inputIcon} />
              <input
                className={styles.input}
                placeholder="Введите ФИО"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                autoComplete="name"
              />
            </div>

            <div className={styles.inputWrapper}>
              <Icon name="user" size={26} className={styles.inputIcon} />
              <input
                type="email"
                className={styles.input}
                placeholder="Введите почту"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>

            <div className={styles.inputWrapper}>
              <Icon name="check" size={26} className={styles.inputIcon} />
              <input
                className={styles.input}
                placeholder={`${codeLabel}: ${codePlaceholder}`}
                value={code}
                onChange={(e) => setCode(e.target.value)}
              />
            </div>

            <div className={styles.inputWrapper}>
              <Icon name="lock" size={26} className={styles.inputIcon} />
              <input
                type="password"
                className={styles.input}
                placeholder="Придумайте пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="new-password"
              />
            </div>
          </div>

          {error && <p className={styles.error}>{error}</p>}

          <div className={styles.buttons}>
            <button className="btn" type="submit" disabled={loading}>
              {loading ? "Создаём аккаунт..." : "Создать аккаунт"}
            </button>

            <button
              type="button"
              className={`${styles.outlineBtn} border-gradient`}
              onClick={() => router.push(`/login?role=${role}`)}
            >
              Уже есть аккаунт? Войти
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
