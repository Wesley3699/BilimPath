"use client";

import { useEffect, useMemo } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import styles from "./layout.module.scss";
import Icon from "@/shared/icons/Icon";

export default function StudentLayout({ children }) {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("role");

    // если нет токена — на роль/логин
    if (!token) router.replace("/role");

    // если вдруг teacher — отправим на teacher (пока можно просто на /role)
    if (role && role !== "student") router.replace("/role");
  }, [router]);

  const nav = useMemo(
    () => [
      { href: "/", label: "Главная", icon: "home" }, // добавь HomeIcon, если нет — поменяешь на существующий
      { href: "/tasks", label: "Задания", icon: "check" },
      { href: "/progress", label: "Прогресс", icon: "chart" }, // добавь ChartIcon или замени
      { href: "/mentor", label: "AI-наставник", icon: "brain" }, // добавь BrainIcon или замени
    ],
    [],
  );

  return (
    <div className={styles.wrapper}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <Image
            src="/imgs/logo.png"
            alt="BilimPath Logo"
            width={42}
            height={44}
            priority
          />
          <span className={styles.brandTxt}>BilimPath AI</span>
        </div>

        <nav className={styles.nav}>
          {nav.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`${styles.navItem} ${active ? styles.active : ""}`}
              >
                <span className={styles.navIcon}>
                  <Icon name={item.icon} size={22} />
                </span>
                <span className={styles.navLabel}>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <button
          type="button"
          className={styles.logout}
          onClick={() => {
            localStorage.removeItem("access_token");
            localStorage.removeItem("token_type");
            localStorage.removeItem("role");
            router.push("/role");
          }}
        >
          Выйти
        </button>
      </aside>

      <main className={styles.content}>{children}</main>
    </div>
  );
}
