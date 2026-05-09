import React, { useRef, useState }  from 'react';
import { uploadResume } from '../api/user';

function Profile() {
  const fileInput = useRef();
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleUpload = async (e) => {
    e.preventDefault();
    const file = fileInput.current.files[0];
    if (!file) return;
    setError('');
    setSuccess('');
    try {
      const data = await uploadResume(file);
      setSuccess(data.message || 'Resume uploaded successfully!');
      setTimeout(() => {
        // Optionally, you can clear the file input after successful upload
        fileInput.current.value = '';
      }, 1000);
    } catch (err) {
      console.error('Upload error:', err);
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError(err.response?.data?.detail || err.message || 'Upload failed.');
      }
    }
  };

  return (
    <div className="container mt-5 d-flex flex-column align-items-center">
      <div className="card shadow p-4" style={{ maxWidth: 400, width: '100%' }}>
        <h2 className="mb-3 text-center">Profile</h2>
        <form onSubmit={handleUpload}>
          <div className="mb-3">
            <input type='text' className="form-control" placeholder="Enter your resume name" required></input>
            <input type="file" className="form-control" ref={fileInput} accept=".pdf,.doc,.docx,.txt" required />
          </div>
          <button type="submit" className="btn btn-primary w-100">Upload Resume</button>
        </form>
      </div>
    </div>
  );
}

export default Profile;
