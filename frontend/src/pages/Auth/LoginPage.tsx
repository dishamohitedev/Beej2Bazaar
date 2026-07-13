import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Sprout, Mail, Lock, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const LoginPage: React.FC = () => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, signup } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email.trim() || !password) {
      setError('Please fill in all fields.');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }

    setLoading(true);
    try {
      if (isSignUp) {
        await signup(email.trim(), password);
      } else {
        await login(email.trim(), password);
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        (isSignUp ? 'Registration failed. Check if email is already in use.' : 'Invalid email or password.')
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#F4F9F2] via-white to-[#EAF2E7] px-4 py-12">
      <div className="w-full max-w-md">
        {/* Brand Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="h-16 w-16 bg-[#2E7D32]/10 rounded-3xl flex items-center justify-center text-[#2E7D32] mb-3 shadow-sm">
            <Sprout size={36} className="animate-pulse" />
          </div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">BeejBazaar</h1>
          <p className="text-xs text-slate-500 font-bold mt-1 uppercase tracking-wider">
            Farmer Suitability & Decisions
          </p>
        </div>

        {/* Card Frame */}
        <div className="bg-white/85 backdrop-blur-md rounded-3xl p-8 border border-white shadow-elevation">
          <h2 className="text-xl font-black text-slate-800 mb-2">
            {isSignUp ? 'Create Account' : 'Sign In'}
          </h2>
          <p className="text-xs font-semibold text-slate-500 mb-6 leading-relaxed">
            {isSignUp 
              ? 'Enter your details below to register a new farmer account.' 
              : 'Sign in to access your dashboard, recommendations, and irrigation setup.'
            }
          </p>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Input */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Mail size={16} />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="w-full pl-10 pr-4 py-3 bg-slate-50/50 border border-slate-100 rounded-2xl text-slate-800 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-[#2E7D32]/25 focus:border-[#2E7D32] transition-all"
                  disabled={loading}
                  autoFocus
                />
              </div>
            </div>

            {/* Password Input */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock size={16} />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-3 bg-slate-50/50 border border-slate-100 rounded-2xl text-slate-800 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-[#2E7D32]/25 focus:border-[#2E7D32] transition-all"
                  disabled={loading}
                />
              </div>
            </div>

            {error && (
              <div className="text-xs font-bold text-red-500 bg-red-50/50 border border-red-100/50 p-3.5 rounded-xl">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 px-4 bg-[#2E7D32] hover:bg-[#256428] text-white rounded-2xl text-xs font-black uppercase tracking-wider transition-colors shadow-sm flex items-center justify-center gap-2 cursor-pointer disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {loading ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                isSignUp ? 'Register & Continue' : 'Sign In'
              )}
            </button>
          </form>

          {/* Toggle link */}
          <div className="mt-6 text-center">
            <button
              onClick={() => {
                setIsSignUp(!isSignUp);
                setError('');
              }}
              className="text-xs font-bold text-[#2E7D32] hover:underline cursor-pointer"
            >
              {isSignUp ? 'Already have an account? Sign In' : 'New to BeejBazaar? Create Account'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
