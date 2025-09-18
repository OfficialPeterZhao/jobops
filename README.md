# JobOps - Job Application Tracker

A full-stack web application for tracking job applications with a spreadsheet-like interface. Built with React frontend and Python Flask backend.

![JobOps Demo](https://img.shields.io/badge/Status-Active-green) ![React](https://img.shields.io/badge/React-19.1.1-blue) ![Flask](https://img.shields.io/badge/Flask-Latest-orange) ![TypeScript](https://img.shields.io/badge/TypeScript-4.9.5-blue)

## 🚀 Features

### Core Functionality
- **📊 Spreadsheet Interface**: Excel-like grid using AG Grid for intuitive job tracking
- **🔐 User Authentication**: Secure JWT-based login and registration system
- **✨ Manual Job Entry**: Add job applications with detailed information
- **👤 User-Specific Data**: Each user sees only their own job applications
- **💾 Persistent Storage**: SQLite database for reliable data storage

### Planned Features
- **📧 Email Scraping**: Automatically extract job applications from emails
- **🔗 API Integration**: Connect with job boards and career sites
- **📈 Analytics**: Track application success rates and trends

## 🛠️ Tech Stack

### Frontend
- **React 19.1.1** with TypeScript
- **AG Grid** for the spreadsheet interface
- **CSS3** for styling and responsive design
- **JWT** for authentication

### Backend
- **Python Flask** REST API
- **SQLAlchemy** ORM for database operations
- **Flask-JWT-Extended** for authentication
- **Flask-CORS** for cross-origin requests
- **SQLite** database

## 📋 Prerequisites

- Node.js (v14 or higher)
- Python 3.7+
- npm or yarn

## 🚦 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/OfficialPeterZhao/jobops.git
cd jobops
```

### 2. Backend Setup
```bash
cd job-ops-backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install flask flask-sqlalchemy flask-jwt-extended flask-cors

# Initialize the database
python app.py
```

### 3. Frontend Setup
```bash
cd ../job-ops-frontend

# Install dependencies
npm install

# Start the development server
npm start
```

## 🎯 Usage

### Starting the Application

1. **Start the Backend Server** (Terminal 1):
   ```bash
   cd job-ops-backend
   python app.py
   ```
   Backend runs on: `http://localhost:5001`

2. **Start the Frontend Server** (Terminal 2):
   ```bash
   cd job-ops-frontend
   npm start
   ```
   Frontend runs on: `http://localhost:3001`

### Using the Application

1. **Register/Login**: Create an account or log in with existing credentials
2. **View Jobs**: See all your job applications in a spreadsheet format
3. **Add Jobs**: Click "Add Job" to manually enter new job applications
4. **Manage Data**: Edit, sort, and filter your job applications

### Job Application Fields
- Company Name
- Position Title
- Application Date
- Status (Applied, Interview, Offer, Rejected)
- Location
- Salary Range
- Notes

## 📁 Project Structure

```
jobops/
├── job-ops-backend/          # Flask backend
│   ├── app.py               # Main Flask application
│   ├── models.py            # Database models
│   ├── auth.py              # Authentication routes
│   └── jobs.db              # SQLite database
├── job-ops-frontend/         # React frontend
│   ├── src/
│   │   ├── App.tsx          # Main application component
│   │   ├── JobGrid.tsx      # AG Grid spreadsheet component
│   │   ├── AddJobForm.tsx   # Job entry form
│   │   ├── Login.tsx        # Authentication component
│   │   └── index.tsx        # Application entry point
│   ├── public/              # Static assets
│   └── package.json         # Frontend dependencies
├── README.md                # This file
└── LICENSE                  # MIT License
```

## 🔧 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login

### Jobs
- `GET /jobs` - Get all jobs for authenticated user
- `POST /jobs` - Create new job application
- `PUT /jobs/<id>` - Update job application
- `DELETE /jobs/<id>` - Delete job application

## 🎨 Screenshots

*Screenshots coming soon...*

## 🚧 Development Roadmap

### Phase 1 (Completed ✅)
- [x] Basic CRUD operations for job applications
- [x] User authentication system
- [x] Spreadsheet-like interface
- [x] Manual job entry form

### Phase 2 (Planned)
- [ ] Email integration for automatic job detection
- [ ] Job board API integrations
- [ ] Advanced filtering and search
- [ ] Data export functionality

### Phase 3 (Future)
- [ ] Analytics dashboard
- [ ] Job application templates
- [ ] Reminder notifications
- [ ] Mobile responsive design improvements

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Peter Zhao** ([@OfficialPeterZhao](https://github.com/OfficialPeterZhao))

## 🐛 Issues & Support

If you encounter any issues or have questions:
1. Check existing [Issues](https://github.com/OfficialPeterZhao/jobops/issues)
2. Create a new issue with detailed description
3. Include steps to reproduce any bugs

## 🙏 Acknowledgments

- AG Grid community for the excellent spreadsheet component
- Flask and React communities for comprehensive documentation
- SQLAlchemy for making database operations simple

---

⭐ **Star this repository if you find it helpful!**