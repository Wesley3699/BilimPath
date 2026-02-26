import { SearchIcon, CheckIcon, UserIcon } from "./index";

const icons = {
  search: SearchIcon,
  check: CheckIcon,
  user: UserIcon,
};

export default function Icon({ name, size = 20, ...props }) {
  const Component = icons[name];
  if (!Component) return null;
  return <Component width={size} height={size} {...props} />;
}
