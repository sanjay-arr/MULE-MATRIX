import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { NetworkExplorer } from './pages/NetworkExplorer';
import { AccountExplorer } from './pages/AccountExplorer';
import { Investigation } from './pages/Investigation';
import { Alerts } from './pages/Alerts';
import { Analytics } from './pages/Analytics';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />

        <div className="main-content">
          <Header />

          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/networks" element={<NetworkExplorer />} />
            <Route path="/accounts" element={<AccountExplorer />} />
            <Route path="/investigations" element={<Investigation />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;