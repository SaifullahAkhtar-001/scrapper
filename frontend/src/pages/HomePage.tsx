import { Link } from 'react-router-dom';
import { BookOpen, ArrowRight, Sparkles } from 'lucide-react';

const HomePage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-100 flex flex-col justify-center items-center p-4">
      <div className="max-w-2xl w-full bg-white/80 backdrop-blur-md rounded-3xl shadow-2xl border border-white/30 p-10 flex flex-col items-center">
        <div className="flex items-center gap-4 mb-6">
          <Sparkles className="w-10 h-10 text-indigo-500 animate-pulse" />
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
            Welcome to the Keyword Manager
          </h1>
        </div>
        <p className="text-lg text-slate-700 mb-8 text-center">
          Effortlessly manage your multilingual keywords. Add, edit, and organize your keywords with ease. Start by exploring your keywords or add new ones!
        </p>
        <div className="flex gap-4">
          <Link
            to="/keywords"
            className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl"
          >
            <BookOpen className="w-5 h-5" />
            Go to Keywords
            <ArrowRight className="w-4 h-4 ml-1" />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default HomePage; 