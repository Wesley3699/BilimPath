import styles from "./layout.module.scss";

export default function StudentLayout({ children }) {
  return (
    <div className={styles.wrapper}>
      <aside className={styles.sidebar}>Sidebar</aside>

      <main className={styles.content}>{children}</main>
    </div>
  );
}
