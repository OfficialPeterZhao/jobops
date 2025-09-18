
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
  const jwtToken = localStorage.getItem('jwtToken') || '';

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

  return (
    <div>
      <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>Job Applications ({rowData.length})</h2>
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
            transition: 'transform 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
          onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
        >
          + Add Job
        </button>
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
