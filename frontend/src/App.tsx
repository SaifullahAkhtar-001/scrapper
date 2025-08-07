import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import KeywordsPage from './pages/KeywordsPage';
import DataPage from './pages/DataPage';
import CigarsData from './pages/CigarsData';
import StopwordsPage from './pages/StopwordsPage';

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/keywords" element={<KeywordsPage />} />
        <Route path="/data" element={<DataPage />} />
        <Route path="/cigarsdata" element={<CigarsData />} />
        <Route path="/stopwords" element={<StopwordsPage />} />
      </Routes>
    </Router>
  );
}

export default App
