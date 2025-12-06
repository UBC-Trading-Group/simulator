import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import logoUrl from '/logo.png'

export function Login({ onSwitchTab }: { onSwitchTab: (tab: 'login' | 'register') => void }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [rememberMe, setRememberMe] = useState(true)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    
    try {
      await login(username, password)
      navigate('/') // Redirect to home on success
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-card">
      <div className="auth-heading">
        <h1>Welcome back</h1>
        <p>Welcome back! Please enter your details</p>
      </div>

      {error && (
        <div style={{ padding: '12px', background: '#fee2e2', color: '#b91c1c', borderRadius: '10px', border: '1px solid #fecdd3' }}>
          {error}
        </div>
      )}

      <form onSubmit={handleLogin} style={{ display: 'grid', gap: 16 }}>
        <div>
          <label className="input-label">Email</label>
          <input 
            className="input" 
            type="text" 
            placeholder="Enter your email"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="input-label">Password</label>
          <input 
            className="input" 
            type="password" 
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <div className="auth-row">
          <label className="checkbox">
            <input 
              type="checkbox" 
              checked={rememberMe} 
              onChange={(e) => setRememberMe(e.target.checked)} 
            />
            Remember for 30 days
          </label>
          <button type="button" className="link-subtle">Forgot password</button>
        </div>

        <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
          {loading ? 'Signing in...' : 'Sign in'}
        </button>
        <button type="button" className="btn btn-ghost btn-block" style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 10 }}>
          <span role="img" aria-label="Google">🌐</span>
          <span>Sign in with Google</span>
        </button>
      </form>

      <div className="auth-footer">
        Don&apos;t have an account?{' '}
        <button onClick={() => onSwitchTab('register')}>Sign up</button>
      </div>
    </div>
  )
}

export function Register({ onSwitchTab }: { onSwitchTab: (tab: 'login' | 'register') => void }) {
  return (
    <div className="auth-card">
      <div className="auth-heading">
        <h1>Create account</h1>
        <p>Please enter your details to sign up</p>
      </div>
      <div style={{ display: 'grid', gap: 12 }}>
        <div>
          <label className="input-label">Username</label>
          <input className="input" type="text" placeholder="Username" />
        </div>
        <div>
          <label className="input-label">Email</label>
          <input className="input" type="email" placeholder="Email" />
        </div>
        <div>
          <label className="input-label">Full Name</label>
          <input className="input" type="text" placeholder="Full name" />
        </div>
        <div>
          <label className="input-label">Password</label>
          <input className="input" type="password" placeholder="Password" />
        </div>
        <div>
          <label className="input-label">Confirm Password</label>
          <input className="input" type="password" placeholder="Confirm password" />
        </div>
        <button className="btn btn-primary btn-block">Register</button>
        <div className="auth-footer">
          Already have an account?{' '}
          <button onClick={() => onSwitchTab('login')}>Log in here</button>
        </div>
      </div>
    </div>
  )
}

function LoginPage() {
  const [tab, setTab] = useState<'login' | 'register'>('login')
  const [searchParams, setSearchParams] = useSearchParams()

  useEffect(() => {
    const mode = searchParams.get('mode')
    if (mode === 'signup' || mode === 'register') {
      setTab('register')
    } else if (mode === 'login') {
      setTab('login')
    }
  }, [searchParams])

  const setTabAndUrl = (next: 'login' | 'register') => {
    setTab(next)
    setSearchParams(next === 'register' ? { mode: 'signup' } : { mode: 'login' })
  }

  return (
    <div className="auth-layout">
      <div className="auth-pane">
        <div className="auth-pane-inner">
          <div className="auth-logo">
            <img src={logoUrl} alt="Trading Group UBC" />
            <span>Trading Simulator</span>
          </div>

          {tab === 'login' ? <Login onSwitchTab={setTabAndUrl} /> : <Register onSwitchTab={setTabAndUrl} />}
        </div>
      </div>

      <div className="auth-hero">
      </div>
    </div>
  )
}

export default LoginPage


