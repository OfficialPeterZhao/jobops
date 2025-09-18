import React, { useState } from 'react';
import './AddJobForm.css';

interface Job {
  title: string;
  company: string;
  date_applied: string;
  status: string;
  notes: string;
}

interface AddJobFormProps {
  onJobAdded: (job: Job) => void;
  onCancel: () => void;
}

const AddJobForm: React.FC<AddJobFormProps> = ({ onJobAdded, onCancel }) => {
  const [formData, setFormData] = useState({
    title: '',
    company: '',
    date_applied: new Date().toISOString().split('T')[0], // Today's date
    status: 'Applied',
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('jwtToken');
      const response = await fetch('http://127.0.0.1:5001/jobs', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const newJob = await response.json();
        onJobAdded(newJob);
        // Reset form
        setFormData({
          title: '',
          company: '',
          date_applied: new Date().toISOString().split('T')[0],
          status: 'Applied',
          notes: ''
        });
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to add job');
      }
    } catch (error) {
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="add-job-overlay">
      <div className="add-job-form">
        <h3>Add New Job Application</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Job Title *</label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label>Company *</label>
            <input
              type="text"
              name="company"
              value={formData.company}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label>Date Applied *</label>
            <input
              type="date"
              name="date_applied"
              value={formData.date_applied}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label>Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
            >
              <option value="Applied">Applied</option>
              <option value="Interview Scheduled">Interview Scheduled</option>
              <option value="Interview Completed">Interview Completed</option>
              <option value="Offer Received">Offer Received</option>
              <option value="Rejected">Rejected</option>
              <option value="Withdrawn">Withdrawn</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>Notes</label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={3}
              placeholder="Add any additional notes about this application..."
            />
          </div>
          
          {error && <div className="error">{error}</div>}
          
          <div className="form-buttons">
            <button type="button" onClick={onCancel} className="cancel-btn">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="submit-btn">
              {loading ? 'Adding...' : 'Add Job'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddJobForm;
