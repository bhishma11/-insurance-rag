import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/auth';
import { LemonLogo } from '../components/Common/LemonLogo';
import { LoadingSkeleton } from '../components/Common/LoadingSkeleton';
import '../styles/globals.css';

const Signup: React.FC = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [company, setCompany] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ text: string; type: string } | null>(null);
  const [isPageLoading, setIsPageLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsPageLoading(false), 800);
    return () => clearTimeout(timer);
  }, []);

  if (isPageLoading) {
    return <LoadingSkeleton type="login" />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const response = await authService.signup({ name, email, company });
      if (response.success) {
        setMessage({
          text: '✅ Request submitted! Check your email for admin approval.',
          type: 'success'
        });
        setTimeout(() => navigate('/login'), 3000);
      }
    } catch (err: any) {
      setMessage({
        text: err.response?.data?.detail || 'Signup failed. Please try again.',
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="logo-icon">
            <LemonLogo size={44} animated={true} />
          </div>
          <h1>Lemonade <span>AI</span></h1>
          <p>Request Access to Insurance Intelligence</p>
        </div>

        {message && <div className={`toast show ${message.type}`}>{message.text}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Full Name</label>
            <input
              type="text"
              placeholder="John Doe"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Email Address</label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Company (Optional)</label>
            <input
              type="text"
              placeholder="Your Company"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
            />
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Submitting...
              </span>
            ) : (
              '📩 Request Access'
            )}
          </button>
        </form>

        <div className="auth-links">
          <Link to="/login">Already have an account? <strong>Sign In</strong></Link>
        </div>
      </div>
    </div>
  );
};

export default Signup;