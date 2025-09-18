# JobOps Backend - Flask API

## Setup Instructions

1. **Activate your Python virtual environment:**
   ```zsh
   source venv/bin/activate
   ```

2. **Install dependencies (if not already installed):**
   ```zsh
   pip install flask
   ```

3. **Run the Flask server:**
   ```zsh
   python app.py
   ```
   The server will start at http://127.0.0.1:5000



## Authentication & User-Specific Job Tracking

User authentication is handled with JWT. Each job application is linked to the authenticated user and only visible to its owner.

### Register & Log In
- `POST /register` - Register a new user
   - JSON body: `{ "username": "yourname", "password": "yourpassword" }`
- `POST /login` - Log in and receive a JWT access token
   - JSON body: `{ "username": "yourname", "password": "yourpassword" }`
   - Response: `{ "access_token": "..." }`

### Using the API
Include the access token in the `Authorization` header for all job endpoints:
```
Authorization: Bearer <access_token>
```

### API Endpoints
- `GET /jobs` - List your job applications
- `POST /jobs` - Add a new job application (linked to your user)
- `PUT /jobs/<job_id>` - Edit your job application
- `DELETE /jobs/<job_id>` - Delete your job application

**Note:** The database schema now includes a `user_id` field in `JobApplication` to support user-specific job tracking.

You can use tools like Postman or curl to interact with the API. Register and log in as different users to confirm each user only sees their own jobs.
