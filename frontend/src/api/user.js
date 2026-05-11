import axios from 'axios';

const API_URL = 'http://localhost:8000/api/users';

export const login = async (username, password) => {
  const res = await axios.post(`${API_URL}/login`, { username, password });
  localStorage.setItem('user_id', res.data.user_id);
  return res.data;
};

export const register = async (username, password, email) => {
  const res = await axios.post(`${API_URL}/register`, { username, password, email });
  return res.data;
};

export const uploadResume = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('user_id', localStorage.getItem('user_id')); // Replace with actual user ID
  try {
    const response = await axios.post(`${API_URL}/upload_resume`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading resume:', error);
    throw error;
  }
};

export const deleteAccount = async () => {
  const user_id = localStorage.getItem('user_id');
  try {
    const response = await axios.delete(`${API_URL}/${user_id}`);
    localStorage.removeItem('user_id');
    window.location.href = '/login'; // Redirect to login page after account deletion
    return null;
  } catch (error) {
    console.error('Error deleting account:', error);
    throw error;
  }
};