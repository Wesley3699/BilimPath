import styles from "./layout.module.scss";

export default function AuthLayout({ children }) {
  return <div className={styles.wrapper}>{children}</div>;
}
