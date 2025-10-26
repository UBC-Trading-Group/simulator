import { Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import HomePage from './pages/index'
import TradesPage from './pages/trades'
import LoginPage from './pages/login'
import ProfilePage from './pages/profile'
import './App.css'

function App() {
  return (
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
  )
}

export default App
