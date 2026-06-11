import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import KeywordsPage from './pages/KeywordsPage';
import DataPage from './pages/DataPage';
import CigarsData from './pages/CigarsData';
import StopwordsPage from './pages/StopwordsPage';
import ScrapeRunnerPage from './pages/ScrapeRunnerPage';
import LoginPage from './pages/LoginPage';
import SettingsPage from './pages/SettingsPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <div className="min-h-screen bg-zinc-50">
                  <Navbar />
                  <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/keywords" element={<KeywordsPage />} />
                    <Route path="/data" element={<DataPage />} />
                    <Route path="/cigarsdata" element={<CigarsData />} />
                    <Route path="/stopwords" element={<StopwordsPage />} />
                    <Route path="/scrape" element={<ScrapeRunnerPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                  </Routes>
                </div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
