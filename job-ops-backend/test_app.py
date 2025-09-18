import unittest
import json
from app import app
from auth import bcrypt, jwt

class JobOpsBackendTestCase(unittest.TestCase):
    def test_edit_job_not_found(self):
        # Try to edit a job that doesn't exist
        response = self.app.put('/jobs/999', data=json.dumps({
            'status': 'No such job'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_delete_job_not_found(self):
        # Try to delete a job that doesn't exist
        response = self.app.delete('/jobs/999')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], 'Job deleted')
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Clear the JobApplication table before each test
        from app import db, JobApplication, app as flask_app
        with flask_app.app_context():
            db.session.query(JobApplication).delete()
            db.session.commit()

    def test_add_job(self):
        response = self.app.post('/jobs',
            data=json.dumps({
                'title': 'Software Engineer',
                'company': 'Acme Corp',
                'date_applied': '2025-09-17',
                'status': 'Applied',
                'notes': 'Submitted via company website'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Software Engineer')

    def test_get_jobs(self):
        self.app.post('/jobs', data=json.dumps({
            'title': 'Software Engineer',
            'company': 'Acme Corp',
            'date_applied': '2025-09-17',
            'status': 'Applied',
            'notes': 'Submitted via company website'
        }), content_type='application/json')
        response = self.app.get('/jobs')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(len(data) > 0)

    def test_edit_job(self):
        post_response = self.app.post('/jobs', data=json.dumps({
            'title': 'Software Engineer',
            'company': 'Acme Corp',
            'date_applied': '2025-09-17',
            'status': 'Applied',
            'notes': 'Submitted via company website'
        }), content_type='application/json')
        job = json.loads(post_response.data)
        job_id = job['id']
        response = self.app.put(f'/jobs/{job_id}', data=json.dumps({
            'status': 'Interview Scheduled'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'Interview Scheduled')

    def test_delete_job(self):
        self.app.post('/jobs', data=json.dumps({
            'title': 'Software Engineer',
            'company': 'Acme Corp',
            'date_applied': '2025-09-17',
            'status': 'Applied',
            'notes': 'Submitted via company website'
        }), content_type='application/json')
        response = self.app.delete('/jobs/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], 'Job deleted')

if __name__ == '__main__':
    result = unittest.main(exit=False)
    if not result.result.failures and not result.result.errors:
        print('All tests pass!')

bcrypt.init_app(app)
jwt.init_app(app)
