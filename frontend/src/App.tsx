import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import KeywordsPage from './pages/KeywordsPage';
import DataPage from './pages/DataPage';
import CigarsData from './pages/CigarsData';
import StopwordsPage from './pages/StopwordsPage';
import ScrapeRunnerPage from './pages/ScrapeRunnerPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-zinc-50">
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/keywords" element={<KeywordsPage />} />
          <Route path="/data" element={<DataPage />} />
          <Route path="/cigarsdata" element={<CigarsData />} />
          <Route path="/stopwords" element={<StopwordsPage />} />
          <Route path="/scrape" element={<ScrapeRunnerPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
