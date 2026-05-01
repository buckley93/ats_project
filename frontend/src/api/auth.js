import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

export const login = async (username, password) => {
  const res = await axios.post(`${API_URL}/login`, { username, password });
  return res.data;
};

export const register = async (username, password) => {
  const res = await axios.post(`${API_URL}/register`, { username, password });
  return res.data;
};
