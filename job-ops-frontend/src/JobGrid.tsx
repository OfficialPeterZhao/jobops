
import React, { useState, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import AddJobForm from './AddJobForm';

interface Job {
  id?: number;
  company: string;
  title: string;
  dateApplied: string;
  status: string;
  notes: string;
}

const defaultColDef: ColDef<Job> = {
  editable: true,
  sortable: true,
  filter: true,
};

const JobGrid: React.FC = () => {
  const [rowData, setRowData] = useState<Job[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [importing, setImporting] = useState(false);
  const jwtToken = localStorage.getItem('jwtToken') || localStorage.getItem('token') || '';

  const fetchJobs = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5001/jobs', {
        headers: {
          'Authorization': `Bearer ${jwtToken}`,
          'Content-Type': 'application/json',
        },
      });
      if (response.ok) {
        const jobs = await response.json();
        setRowData(jobs.map((job: any) => ({
          id: job.id,
          company: job.company,
          title: job.title,
          dateApplied: job.date_applied,
          status: job.status,
          notes: job.notes,
        })));
      } else {
        setRowData([]);
      }
    } catch (error) {
      setRowData([]);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [jwtToken]);

  const handleJobAdded = (newJob: any) => {
    setShowAddForm(false);
    fetchJobs(); // Refresh the grid
  };

  const [columnDefs] = useState<ColDef<Job>[]>([
    { headerName: 'Company', field: 'company' },
    { headerName: 'Job Title', field: 'title' },
    { headerName: 'Date Applied', field: 'dateApplied' },
    { headerName: 'Status', field: 'status' },
    { headerName: 'Notes', field: 'notes' },
  ]);

  // Gmail OAuth handler
  const handleConnectGmail = () => {
    // Navigate browser to backend OAuth start endpoint to allow 302 redirect
    window.location.href = 'http://localhost:5001/gmail/login';
  };

  const handleImportGmail = async () => {
    if (!jwtToken) {
      alert('Please log in first.');
      return;
    }
    try {
      setImporting(true);
      const resp = await fetch('http://localhost:5001/gmail/import_jobs', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${jwtToken}`,
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });
      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data.error || 'Failed to import from Gmail');
      }
      await fetchJobs();
      alert(`Imported ${data.imported || 0} jobs from Gmail.`);
    } catch (e: any) {
      alert(e.message || 'Import failed');
    } finally {
      setImporting(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>Job Applications ({rowData.length})</h2>
        <div>
          <button 
            onClick={() => setShowAddForm(true)}
            style={{
              padding: '0.75rem 1.5rem',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'transform 0.2s',
              marginRight: '10px'
            }}
            onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
            onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
          >
            + Add Job
          </button>
          <button
            onClick={handleConnectGmail}
            style={{
              padding: '0.75rem 1.5rem',
              background: 'linear-gradient(135deg, #ea6060 0%, #a274ba 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'transform 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
            onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
          >
            Connect Gmail
          </button>
          <button
            onClick={handleImportGmail}
            disabled={importing}
            style={{
              padding: '0.75rem 1.5rem',
              marginLeft: '10px',
              background: 'linear-gradient(135deg, #34d399 0%, #10b981 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              fontWeight: '600',
              cursor: importing ? 'not-allowed' : 'pointer',
              opacity: importing ? 0.7 : 1,
              transition: 'transform 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.transform = importing ? 'none' : 'translateY(-2px)'}
            onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
          >
            {importing ? 'Importing…' : 'Import from Gmail'}
          </button>
        </div>
      </div>
      <div className="ag-theme-alpine" style={{ height: 500, width: '100%' }}>
        <AgGridReact<Job>
          rowData={rowData}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
        />
      </div>
      {showAddForm && (
        <AddJobForm
          onJobAdded={handleJobAdded}
          onCancel={() => setShowAddForm(false)}
        />
      )}
    </div>
  );
};

export default JobGrid;
