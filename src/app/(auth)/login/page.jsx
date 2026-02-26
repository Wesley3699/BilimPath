import styles from "./login.module.scss";
import Image from "next/image";
import Icon from "@/shared/icons/Icon";

export default function LoginPage() {
  return (
    <>
      <div className={styles.inner}>
        <div className={styles.bilimPath}>
          <div className={styles.logo}>
            <Image
              src="/imgs/logo.png"
              alt="BilimPath Logo"
              className={styles.logoImg}
              width={50}
              height={53}
            />
            <span className={styles.logoTxt}>BilimPath AI</span>
          </div>
          <p className={styles.description}>
            AI-наставник для персонального обучения
          </p>
        </div>
        <div className={`${styles.card} border-gradient`}>
          <h1 className={styles.title}>Логин</h1>
          <div className={styles.form}>
            <div className={styles.inputs}>
              <label>
                <input className={styles.input} placeholder="Ваша почта" />
                <div className={styles.Icon}>
                  <Icon name="user" size={24} />
                </div>
              </label>
              <input className={styles.input} placeholder="Пароль" />
            </div>
            <div className={styles.buttons}>
              <p className={styles.forgotPass}>Забыли пароль?</p>
              <button className="btn">Войти</button>
              <button className="btn-primary border-gradient">
                Зарегистрироваться
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
