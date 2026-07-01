import api from './api';

export async function requestOtp(phone) {
  const { data } = await api.post('/api/auth/otp/request', { phone });
  return data;
}

export async function verifyOtp({ phone, otp, role, name }) {
  const { data } = await api.post('/api/auth/otp/verify', { phone, otp, role, name });
  return data; // { access_token, refresh_token, user }
}

export async function fetchMe() {
  const { data } = await api.get('/api/auth/me');
  return data;
}
