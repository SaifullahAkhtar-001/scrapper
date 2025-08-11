import { Link, useLocation } from 'react-router-dom';
import { BookOpen, Home, Database } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();
  return (
    <nav className="w-full bg-white/80 backdrop-blur-md shadow-sm border-b border-slate-100">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent select-none">
            Keyword Manager
          </span>
        </div>
        <div className="flex gap-2">
          <Link
            to="/"
            className={`flex items-center gap-1 px-4 py-2 rounded-lg font-medium transition-colors ${location.pathname === '/' ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-blue-50'}`}
          >
            <Home className="w-4 h-4" /> Home
          </Link>
          <Link
            to="/keywords"
            className={`flex items-center gap-1 px-4 py-2 rounded-lg font-medium transition-colors ${location.pathname.startsWith('/keywords') ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-blue-50'}`}
          >
            <BookOpen className="w-4 h-4" /> Keywords
          </Link>
          <Link
            to="/stopwords"
            className={`flex items-center gap-1 px-4 py-2 rounded-lg font-medium transition-colors ${location.pathname.startsWith('/stopwords') ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-blue-50'}`}
          >
            <Database className="w-4 h-4" /> Stopwords
          </Link>
          <Link
            to="/data"
            className={`flex items-center gap-1 px-4 py-2 rounded-lg font-medium transition-colors ${location.pathname.startsWith('/data') ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-blue-50'}`}
          >
            <Database className="w-4 h-4" /> All Data
          </Link>
          <Link
            to="/cigarsdata"
            className={`flex items-center gap-1 px-4 py-2 rounded-lg font-medium transition-colors ${location.pathname.startsWith('/cigarsdata') ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-blue-50'}`}
          >
            <Database className="w-4 h-4" /> Cigars Data
          </Link>
          {/* <Link
            to="/scrape"
            className={`flex items-center gap-1 px-4 py-2 rounded-lg font-medium transition-colors ${location.pathname.startsWith('/scrape') ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-blue-50'}`}
          >
            <Play className="w-4 h-4" /> Run Scrapers
          </Link> */}
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 