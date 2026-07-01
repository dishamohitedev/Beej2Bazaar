import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../../components/Button';
import Input from '../../components/Input';
import Card from '../../components/Card';
import { useAuth } from '../../context/AuthContext';
import { requestOtp, verifyOtp } from '../../services/authService';
import { ROLES } from './roles';

const STEP = { PHONE: 'phone', OTP: 'otp', ROLE: 'role' };

export default function LoginPage() {
  const [step, setStep] = useState(STEP.PHONE);
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [role, setRole] = useState(null);
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const toE164 = (raw) => (raw.startsWith('+') ? raw : `+91${raw.replace(/\D/g, '')}`);

  const handleSendOtp = async () => {
    setError('');
    if (phone.replace(/\D/g, '').length < 10) {
      setError('Enter a valid phone number');
      return;
    }
    setLoading(true);
    try {
      await requestOtp(toE164(phone));
      setStep(STEP.OTP);
    } catch (e) {
      setError(e.response?.data?.detail || 'Could not send OTP. Try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (selectedRole) => {
    setError('');
    setLoading(true);
    try {
      const result = await verifyOtp({
        phone: toE164(phone), otp, role: selectedRole || undefined, name: name || undefined,
      });
      login(result);
      navigate('/dashboard');
    } catch (e) {
      const detail = e.response?.data?.detail;
      if (e.response?.status === 400 && detail?.includes('role')) {
        setStep(STEP.ROLE); // new user, needs to pick a role
      } else {
        setError(detail || 'Invalid OTP. Try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 'var(--space-5)', paddingTop: 'var(--space-8)' }}>
      <div style={{ textAlign: 'center', marginBottom: 'var(--space-6)' }}>
        <div style={{ fontSize: 44 }}>🌾</div>
        <h1 style={{ fontSize: 'var(--font-size-xl)', margin: '8px 0 4px', color: 'var(--color-primary-700)' }}>
          BeejBazaar
        </h1>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-sm)' }}>
          Smart farming, made simple
        </p>
      </div>

      <Card>
        {step === STEP.PHONE && (
          <>
            <Input
              label="Phone Number"
              placeholder="98765 43210"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              type="tel"
              autoFocus
            />
            {error && <ErrorText text={error} />}
            <Button onClick={handleSendOtp} disabled={loading}>
              {loading ? 'Sending OTP...' : 'Send OTP'}
            </Button>
          </>
        )}

        {step === STEP.OTP && (
          <>
            <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginTop: 0 }}>
              Enter the OTP sent to {toE164(phone)}
              {' '}<span style={{ color: 'var(--color-primary-500)' }}>(dev mode: use 123456)</span>
            </p>
            <Input
              label="OTP"
              placeholder="123456"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              maxLength={6}
              autoFocus
            />
            {error && <ErrorText text={error} />}
            <Button onClick={() => handleVerifyOtp()} disabled={loading || otp.length < 4}>
              {loading ? 'Verifying...' : 'Verify & Continue'}
            </Button>
            <div style={{ marginTop: 'var(--space-3)', textAlign: 'center' }}>
              <Button variant="ghost" onClick={() => setStep(STEP.PHONE)}>Change phone number</Button>
            </div>
          </>
        )}

        {step === STEP.ROLE && (
          <>
            <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginTop: 0 }}>
              Welcome! Tell us who you are to set up your dashboard.
            </p>
            <Input label="Your Name" placeholder="e.g. Ramesh Patil" value={name} onChange={(e) => setName(e.target.value)} />
            <div style={{
              display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)', marginBottom: 'var(--space-4)',
            }}>
              {ROLES.map((r) => (
                <div
                  key={r.value}
                  onClick={() => setRole(r.value)}
                  style={{
                    padding: 'var(--space-3)', borderRadius: 'var(--radius-md)',
                    border: `2px solid ${role === r.value ? 'var(--color-primary-500)' : 'var(--color-border)'}`,
                    background: role === r.value ? 'var(--color-primary-50)' : 'var(--color-surface)',
                    textAlign: 'center', cursor: 'pointer', transition: 'all var(--transition-fast)',
                  }}
                >
                  <div style={{ fontSize: 24 }}>{r.icon}</div>
                  <div style={{ fontSize: 'var(--font-size-xs)', fontWeight: 600, marginTop: 4 }}>{r.label}</div>
                </div>
              ))}
            </div>
            {error && <ErrorText text={error} />}
            <Button onClick={() => handleVerifyOtp(role)} disabled={loading || !role || !name}>
              {loading ? 'Creating account...' : 'Get Started'}
            </Button>
          </>
        )}
      </Card>
    </div>
  );
}

function ErrorText({ text }) {
  return (
    <div style={{ color: 'var(--color-danger)', fontSize: 'var(--font-size-sm)', marginBottom: 'var(--space-3)' }}>
      {text}
    </div>
  );
}
