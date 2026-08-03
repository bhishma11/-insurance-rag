// src/hooks/useSessionTimeout.js
import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';  // ✅ Use react-router-dom instead of next/router

export function useSessionTimeout(timeoutMinutes = 5) {
  const navigate = useNavigate();
  const timerRef = useRef(null);

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');  // ✅ Use navigate from react-router-dom
  };

  const resetTimer = () => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(logout, timeoutMinutes * 60 * 1000);
  };

  useEffect(() => {
    resetTimer();
    
    // Reset timer on user activity
    window.addEventListener('click', resetTimer);
    window.addEventListener('keypress', resetTimer);
    window.addEventListener('scroll', resetTimer);
    window.addEventListener('mousemove', resetTimer);
    window.addEventListener('touchstart', resetTimer);  // ✅ Added for mobile

    return () => {
      clearTimeout(timerRef.current);
      window.removeEventListener('click', resetTimer);
      window.removeEventListener('keypress', resetTimer);
      window.removeEventListener('scroll', resetTimer);
      window.removeEventListener('mousemove', resetTimer);
      window.removeEventListener('touchstart', resetTimer);
    };
  }, []);
}