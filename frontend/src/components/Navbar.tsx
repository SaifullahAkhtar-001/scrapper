import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  Tag,
  Ban,
  Database,
  Package,
  Settings,
  LogOut,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/Button';

const navItems = [
  { to: '/', label: 'Home', icon: Home, exact: true },
  { to: '/keywords', label: 'Keywords', icon: Tag },
  { to: '/stopwords', label: 'Stopwords', icon: Ban },
  { to: '/data', label: 'All Data', icon: Database },
  { to: '/cigarsdata', label: 'Cigars', icon: Package },
  { to: '/settings', label: 'Settings', icon: Settings },
];

const Navbar = () => {
  const location = useLocation();
  const { user, signOut } = useAuth();

  const isActive = (to: string, exact?: boolean) =>
    exact ? location.pathname === to : location.pathname.startsWith(to);

  return (
    <header className="sticky top-0 z-50 w-full bg-white border-b border-zinc-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex h-14 items-center justify-between gap-4">
          <Link to="/" className="flex items-center gap-2.5 shrink-0">
            <div className="flex items-center justify-center w-7 h-7 rounded-md bg-zinc-900">
              <Tag className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="text-sm font-semibold text-zinc-900 tracking-tight">
              Scraper
            </span>
          </Link>

          <nav className="flex items-center gap-1 overflow-x-auto">
            {navItems.map(({ to, label, icon: Icon, exact }) => {
              const active = isActive(to, exact);
              return (
                <Link
                  key={to}
                  to={to}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors whitespace-nowrap ${
                    active
                      ? 'bg-zinc-100 text-zinc-900'
                      : 'text-zinc-500 hover:text-zinc-900 hover:bg-zinc-50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden sm:inline">{label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center gap-2 shrink-0">
            {user?.email && (
              <span className="hidden md:block text-xs text-zinc-500 truncate max-w-[140px]">
                {user.email}
              </span>
            )}
            <Button variant="ghost" size="sm" onClick={signOut} title="Sign out">
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Sign out</span>
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
