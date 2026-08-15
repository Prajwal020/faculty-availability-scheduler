# Faculty Availability & Appointment Scheduler — Deployment Guide

This guide describes reproducible deployment procedures for **Development**, **Testing**, and **Production** environments.

---

## 1. Environment Configurations

| Setting | Development | Testing | Production |
| :--- | :--- | :--- | :--- |
| **`ENVIRONMENT`** | `development` | `testing` | `production` |
| **`DEBUG`** | `True` | `False` | `False` |
| **`DATABASE_URL`** | `sqlite:///./faculty_scheduler.db` or local PostgreSQL | `sqlite:///:memory:` | `postgresql://user:pass@host:5432/dbname` |
| **`JWT_SECRET_KEY`** | Dev placeholder | Test secret | Secure 64-character random string |
| **`CORS_ORIGINS`** | `http://localhost:5173,http://localhost:3000` | N/A | `https://scheduler.institution.edu` |
| **`TIMEZONE`** | `Asia/Kolkata` | `Asia/Kolkata` | `Asia/Kolkata` |
| **`VITE_API_BASE_URL`** | `http://127.0.0.1:8000` | N/A | `https://api.scheduler.institution.edu` |

---

## 2. Production Database Deployment (PostgreSQL)

### Requirements:
- PostgreSQL 14+
- `pg_trgm` and `uuid-ossp` extensions available.

### Setup Steps:
1. **Provision Database**:
   ```sql
   CREATE DATABASE faculty_scheduler_db;
   CREATE USER faculty_admin WITH ENCRYPTED PASSWORD 'secure_production_password_here';
   GRANT ALL PRIVILEGES ON DATABASE faculty_scheduler_db TO faculty_admin;
   ```

2. **Execute Alembic Schema Migrations**:
   Never create tables manually outside of Alembic in production. Run:
   ```bash
   cd backend
   export DATABASE_URL="postgresql://faculty_admin:secure_production_password_here@postgres-host:5432/faculty_scheduler_db"
   alembic upgrade head
   ```

3. **Verify Migration State**:
   ```bash
   alembic current
   # Expected output: 7f3ffbb07770 (head)
   ```

---

## 3. Backend Deployment

### Option A: Direct Host Deployment (Gunicorn / Uvicorn)
1. **Create system user and clone repository**:
   ```bash
   useradd -m -s /bin/bash appuser
   ```
2. **Setup virtual environment**:
   ```bash
   python3 -m venv /opt/faculty-scheduler/backend/venv
   source /opt/faculty-scheduler/backend/venv/bin/activate
   pip install --no-cache-dir -r requirements.txt
   ```
3. **Configure Systemd Service** (`/etc/systemd/system/faculty-scheduler-api.service`):
   ```ini
   [Unit]
   Description=Faculty Availability Scheduler API
   After=network.target

   [Service]
   User=appuser
   WorkingDirectory=/opt/faculty-scheduler/backend
   EnvironmentFile=/opt/faculty-scheduler/backend/.env
   ExecStart=/opt/faculty-scheduler/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
4. **Start and enable**:
   ```bash
   systemctl daemon-reload
   systemctl enable --now faculty-scheduler-api
   ```

---

## 4. Frontend Deployment (Static Hosting / Nginx)

1. **Build Production Bundle**:
   ```bash
   cd frontend
   export VITE_API_BASE_URL="https://api.scheduler.institution.edu"
   npm install
   npm run build
   ```
   The compiled static assets are located in `frontend/dist/`.

2. **Nginx Reverse Proxy & Static Host Configuration**:
   ```nginx
   server {
       listen 80;
       server_name scheduler.institution.edu;
       return 301 https://$host$request_uri;
   }

   server {
       listen 443 ssl http2;
       server_name scheduler.institution.edu;

       ssl_certificate /etc/letsencrypt/live/scheduler.institution.edu/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/scheduler.institution.edu/privkey.pem;

       root /var/www/faculty-scheduler-frontend;
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }

       location /api/ {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

---

## 5. Health Monitoring & Observability

- **API Health**: `GET https://api.scheduler.institution.edu/health` $\rightarrow$ `HTTP 200 { "status": "healthy" }`
- **Database Health**: `GET https://api.scheduler.institution.edu/health/db` $\rightarrow$ `HTTP 200 { "status": "connected", "database": "operational" }` (returns `HTTP 503` if PostgreSQL is unreachable).
