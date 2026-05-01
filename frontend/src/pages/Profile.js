import React, { useRef } from 'react';


function Profile() {
  const fileInput = useRef();

  const handleUpload = (e) => {
    e.preventDefault();
    const file = fileInput.current.files[0];
    if (!file) return;
    // TODO: Upload file to backend
    alert('Resume upload not implemented.');
  };

  return (
    <div className="container mt-5 d-flex flex-column align-items-center">
      <div className="card shadow p-4" style={{ maxWidth: 400, width: '100%' }}>
        <h2 className="mb-3 text-center">Profile</h2>
        <form onSubmit={handleUpload}>
          <div className="mb-3">
            <input type="file" className="form-control" ref={fileInput} accept=".pdf,.doc,.docx,.txt" required />
          </div>
          <button type="submit" className="btn btn-primary w-100">Upload Resume</button>
        </form>
      </div>
    </div>
  );
}

export default Profile;
