import {
  SearchIcon,
  CheckIcon,
  UserIcon,
  LockIcon,
  GraduationCap,
  TeacherIcon,
  InstIcon,
} from "./index";

const icons = {
  search: SearchIcon,
  check: CheckIcon,
  user: UserIcon,
  lock: LockIcon,
  cap: GraduationCap,
  teacher: TeacherIcon,
  lock: LockIcon,
  inst: InstIcon,
};

export default function Icon({ name, size = 20, ...props }) {
  const Component = icons[name];
  if (!Component) return null;
  return <Component width={size} height={size} {...props} />;
}
