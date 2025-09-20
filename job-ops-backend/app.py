
from flask import Flask, request, jsonify, redirect, session, url_for
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, JobApplication
import os
import pathlib
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import re
import base64
import unicodedata
from datetime import datetime
import html as htmllib
from flask_jwt_extended import JWTManager
from auth import auth_bp


app = Flask(__name__)
app.secret_key = 'your-super-secret-key'  # Change this to a secure value
# Session cookie settings for local OAuth
app.config.update(
    SESSION_COOKIE_NAME='jobops_session',
    SESSION_COOKIE_SAMESITE='Lax',  # send cookie on top-level GET (OAuth redirect)
    SESSION_COOKIE_SECURE=False,    # ok for http://localhost in dev
    SESSION_COOKIE_HTTPONLY=True,
)
CORS(app)  # Enable CORS for all routes
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a secure value
db.init_app(app)
jwt = JWTManager(app)
app.register_blueprint(auth_bp)


# Allow HTTP for local OAuth redirects (DEV ONLY)
os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')

# Google OAuth2 config
GOOGLE_CLIENT_SECRETS_FILE = str(pathlib.Path(__file__).parent / 'client_secret_819508917411-gjd9btjkmn6nlte5u0n27i5ok8crf7h9.apps.googleusercontent.com.json')
GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]
GOOGLE_REDIRECT_URI = 'http://localhost:5001/gmail/callback'

# Gmail OAuth endpoints
@app.route('/gmail/login')
def gmail_login():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=GOOGLE_SCOPES
    )
    # Force localhost to match Google Console redirect and keep session domain consistent
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/gmail/callback')
def gmail_callback():
    # Prefer saved session state; fall back to query param for resilience
    state = session.get('state') or request.args.get('state')
    if not state:
        return jsonify({'error': 'Missing OAuth state. Please start the Gmail connect again.'}), 400
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=GOOGLE_SCOPES,
        state=state
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    # Store credentials in session (for demo; use DB for production)
    session['gmail_token'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    return redirect(url_for('gmail_fetch_jobs'))

@app.route('/gmail/fetch_jobs')
def gmail_fetch_jobs():
    # Load credentials from session
    creds_data = session.get('gmail_token')
    if not creds_data:
        return jsonify({'error': 'No Gmail credentials'}), 401
    creds = google.oauth2.credentials.Credentials(
        **creds_data
    )
    service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)
    # Example: search for job application emails
    results = service.users().messages().list(userId='me', q='(application OR interview OR offer) newer_than:1y category:primary').execute()
    messages = results.get('messages', [])
    jobs = []
    for msg in messages[:10]:  # Limit to 10 for demo
        msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        snippet = msg_detail.get('snippet', '')
        snippet = _clean_text(snippet)
        jobs.append({'snippet': snippet, 'id': msg['id']})
    return jsonify({'jobs': jobs})


@app.route('/gmail/import_jobs', methods=['POST'])
@jwt_required()
def gmail_import_jobs():
    """Fetch recent Gmail messages and insert simple JobApplication rows for the current user.
    This uses a naive heuristic on the message snippet. Intended for demo/dev.
    """
    user_id = int(get_jwt_identity())
    creds_data = session.get('gmail_token')
    if not creds_data:
        return jsonify({'error': 'No Gmail connection. Click Connect Gmail first.'}), 401
    creds = google.oauth2.credentials.Credentials(**creds_data)
    service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', q='(application OR interview OR offer) newer_than:1y category:primary').execute()
    messages = results.get('messages', [])

    imported = 0
    for msg in messages[:25]:
        msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = {h['name'].lower(): h['value'] for h in msg_detail.get('payload', {}).get('headers', [])}
        subject = _clean_text(headers.get('subject', ''))
        from_header = headers.get('from', '')

        body_text = _extract_message_text(msg_detail.get('payload', {}))
        body_text = _clean_text(body_text)
        snippet = _clean_text(msg_detail.get('snippet', ''))

        company, title = _parse_company_title(subject, from_header)
        status = _infer_status(subject + ' ' + body_text)

        # Use Gmail internalDate as date_applied if present
        ts = msg_detail.get('internalDate')
        date_applied = ''
        if ts:
            try:
                date_applied = datetime.utcfromtimestamp(int(ts)/1000).date().isoformat()
            except Exception:
                date_applied = ''

        notes = (body_text or snippet)[:1000]

        job = JobApplication(
            user_id=user_id,
            title=(title or 'Application Update')[:120],
            company=(company or 'Unknown')[:120],
            date_applied=date_applied,
            status=status,
            notes=notes
        )
        db.session.add(job)
        imported += 1

    db.session.commit()
    return jsonify({'imported': imported})


# ---------- Helpers ----------
def _clean_text(text: str) -> str:
    if not text:
        return ''
    # Decode HTML entities and normalize
    text = htmllib.unescape(text)
    text = unicodedata.normalize('NFKC', text)
    # Remove zero-width and formatting/control chars but keep common whitespace
    text = re.sub(r'[\u200B-\u200D\u2060\uFEFF\u034F]', '', text)
    text = ''.join(ch for ch in text if not (unicodedata.category(ch).startswith('C') and ch not in '\n\r\t'))
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _decode_b64url(data: str) -> str:
    if not data:
        return ''
    try:
        padded = data + '=' * (-len(data) % 4)
        return base64.urlsafe_b64decode(padded.encode()).decode(errors='replace')
    except Exception:
        return ''


def _extract_message_text(payload: dict) -> str:
    """Extract plain text from a Gmail message payload, prefer text/plain, fallback to stripped HTML."""
    mime = payload.get('mimeType')
    body = payload.get('body', {})
    data = body.get('data')

    # If multipart, walk parts
    if 'parts' in payload:
        # Prefer text/plain
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain':
                txt = _decode_b64url(part.get('body', {}).get('data', ''))
                if txt:
                    return txt
        # Fallback to first HTML
        for part in payload['parts']:
            if part.get('mimeType') == 'text/html':
                html_text = _decode_b64url(part.get('body', {}).get('data', ''))
                return _strip_html(html_text)
        # Recurse into subparts
        for part in payload['parts']:
            txt = _extract_message_text(part)
            if txt:
                return txt
        return ''

    # Single part
    if mime == 'text/plain':
        return _decode_b64url(data)
    if mime == 'text/html':
        return _strip_html(_decode_b64url(data))
    return ''


def _strip_html(s: str) -> str:
    if not s:
        return ''
    # Very naive tag strip; good enough for summaries
    s = re.sub(r'<\s*script[^>]*>.*?<\s*/\s*script\s*>', ' ', s, flags=re.I | re.S)
    s = re.sub(r'<\s*style[^>]*>.*?<\s*/\s*style\s*>', ' ', s, flags=re.I | re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return s


def _parse_company_title(subject: str, from_header: str):
    subject = subject or ''
    patterns = [
        # received your application for <Title> at <Company>
        r'received your application for\s+(.+?)\s+at\s+(.+)',
        # application to <Company> for <Title>
        r'application to\s+(.+?)\s+for\s+(.+)',
        # interview for <Title> at <Company>
        r'interview for\s+(.+?)\s+at\s+(.+)',
    ]
    for pat in patterns:
        m = re.search(pat, subject, re.IGNORECASE)
        if m:
            g1, g2 = m.group(1).strip(), m.group(2).strip()
            # Heuristic: if the first looks like a company domain, swap
            if '@' in g1 or len(g1.split()) == 1 and len(g2.split()) > 1:
                # leave as is; otherwise we could swap when needed
                pass
            return g2, g1  # company, title (for the first pattern swap)

    # Couldn’t parse from subject; guess company from email domain
    company = None
    m = re.search(r'@([\w.-]+)', from_header or '')
    if m:
        dom = m.group(1)
        parts = dom.split('.')
        if len(parts) >= 2:
            company = parts[-2].capitalize()
        else:
            company = parts[0]
    title = subject
    return company, title


def _infer_status(text: str) -> str:
    t = (text or '').lower()
    if 'interview' in t:
        return 'Interview'
    if 'offer' in t:
        return 'Offer'
    if 'reject' in t or 'unfortunately' in t:
        return 'Rejected'
    if 'received your application' in t or 'thank you for applying' in t or 'application received' in t:
        return 'Applied'
    return 'Imported'


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
    # Bind to localhost explicitly to avoid IPv6 (::1) mismatch issues
    app.run(debug=True, host='localhost', port=5001)
