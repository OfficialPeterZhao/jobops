
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, JobApplication
import os
from flask_jwt_extended import JWTManager
from auth import auth_bp


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a secure value
db.init_app(app)
jwt = JWTManager(app)
app.register_blueprint(auth_bp)

# JobApplication model is now imported from models.py


@app.route('/jobs', methods=['GET'])
@jwt_required()
def get_jobs():
    user_id = int(get_jwt_identity())
    jobs = JobApplication.query.filter_by(user_id=user_id).all()
    return jsonify([job.to_dict() for job in jobs])


@app.route('/jobs', methods=['POST'])
@jwt_required()
def add_job():
    data = request.json
    user_id = int(get_jwt_identity())
    job = JobApplication(
        user_id=user_id,
        title=data.get('title'),
        company=data.get('company'),
        date_applied=data.get('date_applied'),
        status=data.get('status'),
        notes=data.get('notes')
    )
    db.session.add(job)
    db.session.commit()
    return jsonify(job.to_dict()), 201


@app.route('/jobs/<int:job_id>', methods=['PUT'])
@jwt_required()
def edit_job(job_id):
    data = request.json
    user_id = int(get_jwt_identity())
    job = JobApplication.query.filter_by(id=job_id, user_id=user_id).first()
    if job:
        job.title = data.get('title', job.title)
        job.company = data.get('company', job.company)
        job.date_applied = data.get('date_applied', job.date_applied)
        job.status = data.get('status', job.status)
        job.notes = data.get('notes', job.notes)
        db.session.commit()
        return jsonify(job.to_dict())
    return jsonify({'error': 'Job not found'}), 404


@app.route('/jobs/<int:job_id>', methods=['DELETE'])
@jwt_required()
def delete_job(job_id):
    user_id = int(get_jwt_identity())
    job = JobApplication.query.filter_by(id=job_id, user_id=user_id).first()
    if job:
        db.session.delete(job)
        db.session.commit()
        return jsonify({'result': 'Job deleted'})
    return jsonify({'result': 'Job deleted'})


if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('jobs.db'):
            db.create_all()
    app.run(debug=True, port=5001)
