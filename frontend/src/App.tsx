import { Route, Routes } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import RootProvider from './components/provider';
import HomePage from './pages/index';
import LoginPage from './pages/login';
import ProfilePage from './pages/profile';
import TradesPage from './pages/trades';

function App() {
  return (
    <RootProvider>

        <div>
        <Header />
          <main className="main container">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/trades" element={<TradesPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/profile" element={<ProfilePage />} />
            </Routes>
          </main>
        </div>
        </RootProvider>
  );
}

export default App;
