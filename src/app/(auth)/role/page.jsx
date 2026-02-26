// src/app/(auth)/role/page.js
import styles from "./role.module.scss";
import Image from "next/image";
import Icon from "@/shared/icons/Icon";

export default function RolePage() {
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
        <h1 className={styles.title}>Выберите свою роль</h1>

        <div className={styles.roles}>
          <button
            className={`${styles.roleItem} border-gradient`}
            type="button"
          >
            <div
              className="border-gradient-circle"
              style={{ width: 72, height: 72 }}
            >
              <div className={styles.roleIconInner}>
                <Icon name="cap" size={36} />
              </div>
            </div>

            <div className={styles.roleText}>
              <h2>Студент</h2>
              <p>Проверить знания и получить персональный план обучения</p>
            </div>
          </button>

          <button
            className={`${styles.roleItem} border-gradient`}
            type="button"
          >
            <div
              className="border-gradient-circle"
              style={{ width: 72, height: 72 }}
            >
              <div className={`${styles.roleIconInner} ${styles.iconGradient}`}>
                <Icon name="teacher" size={36} />
              </div>
            </div>

            <div className={styles.roleText}>
              <h2>Преподаватель</h2>
              <p>Создать программу и отслеживать прогресс группы</p>
            </div>
          </button>
        </div>

        <button className="btn" type="button">
          Войти
        </button>
      </div>
    </div>
  );
}
