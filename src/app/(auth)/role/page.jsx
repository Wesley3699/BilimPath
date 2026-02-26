"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import styles from "./role.module.scss";
import Image from "next/image";
import Icon from "@/shared/icons/Icon";

export default function RolePage() {
  const [selectedRole, setSelectedRole] = useState(null);
  const router = useRouter();

  const handleContinue = () => {
    if (!selectedRole) return;

    if (selectedRole === "student") {
      router.push("/login?role=student");
    } else {
      router.push("/login?role=teacher");
    }
  };

  return (
    <div className={styles.inner}>
      {/* Logo Block */}
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
        <h1 className={styles.title}>Выберите свою роль</h1>

        <div className={styles.roles}>
          <button
            type="button"
            onClick={() => setSelectedRole("student")}
            className={`${styles.roleItem} border-gradient ${
              selectedRole === "student" ? styles.active : ""
            }`}
          >
            <div className={`${styles.iconCircle} border-gradient-circle`}>
              <div className={styles.roleIconInner}>
                <Icon name="cap" size={34} />
              </div>
            </div>

            <div className={styles.roleText}>
              <h2>Студент</h2>
              <p>Проверить знания и получить персональный план обучения</p>
            </div>
          </button>

          <button
            type="button"
            onClick={() => setSelectedRole("teacher")}
            className={`${styles.roleItem} border-gradient ${
              selectedRole === "teacher" ? styles.active : ""
            }`}
          >
            <div className={`${styles.iconCircle} border-gradient-circle`}>
              <div className={styles.roleIconInner}>
                <Icon name="teacher" size={34} />
              </div>
            </div>

            <div className={styles.roleText}>
              <h2>Преподаватель</h2>
              <p>Создать программу и отслеживать прогресс группы</p>
            </div>
          </button>
        </div>

        <button
          className={styles.continueBtn}
          disabled={!selectedRole}
          onClick={handleContinue}
        >
          Войти
        </button>
      </div>
    </div>
  );
}
