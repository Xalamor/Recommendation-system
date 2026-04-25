import { NavLink } from 'react-router-dom'

const links = [
  ['/', 'Главная'],
  ['/dataset', 'Датасет'],
  ['/model', 'Модель'],
  ['/demo', 'Демонстрация'],
  ['/results', 'Результаты'],
  ['/business', 'Бизнес-идея'],
]

export default function Navbar() {
  return (
    <header className="navbar">
      <div className="brand">DL Book Recommender</div>
      <nav>
        {links.map(([to, label]) => (
          <NavLink key={to} to={to} className={({ isActive }) => (isActive ? 'active' : '')}>
            {label}
          </NavLink>
        ))}
      </nav>
    </header>
  )
}
