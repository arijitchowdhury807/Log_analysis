# Production Log Analyzer

## Run the Project

### 1. Create virtual environment

```powershell
python -m venv venv
```

### 2. Activate virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Start FastAPI server

```powershell
uvicorn app.main:app --reload
```

Server:

```text
http://127.0.0.1:8000
```

---

# Swagger

Open:

```text
http://127.0.0.1:8000/docs
```

Available endpoints:

```text
GET  /api/v1/health
POST /api/v1/jobs
GET  /api/v1/jobs/{job_id}
```

---

# Health Check

### Request

```http
GET /api/v1/health
```

### Response

```json
{
  "status": "healthy"
}
```

---

# Create Analysis Job

### Request

```http
POST /api/v1/jobs
```

Upload:

```text
sample_data/sample.log
```

The request uses:

```text
multipart/form-data
```

with the form field:

```text
file
```

### Response

```json
{
  "job_id": "618e19ea-7e86-498d-aedf-6a35a2762c76",
  "status": "PENDING"
}
```

---

# Get Analysis Result

Use the `job_id` returned from the previous request.

### Request

```http
GET /api/v1/jobs/618e19ea-7e86-498d-aedf-6a35a2762c76
```

### While Processing

```json
{
  "job_id": "618e19ea-7e86-498d-aedf-6a35a2762c76",
  "status": "PROCESSING",
  "filename": "sample.log",
  "result": null,
  "error": null
}
```

### Completed

```json
{
  "job_id": "618e19ea-7e86-498d-aedf-6a35a2762c76",
  "status": "COMPLETED",
  "filename": "sample.log",
  "result": {
    "lines_processed": 11,
    "unparseable_lines": 1,
    "error_counts": {
      "auth-service": 0,
      "payment-service": 2,
      "billing-service": 1,
      "inventory-service": 0,
      "database-service": 0
    },
    "top_offender": "payment-service",
    "processing_time_ms": 5.23
  },
  "error": null
}
```

`processing_time_ms` will vary depending on the machine and file size.

---

# CLI

Keep the FastAPI server running in one terminal.

Open a second terminal.

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Run:

```powershell
python client/cli.py sample_data/sample.log
```

Or run without specifying the file:

```powershell
python client/cli.py
```

Then enter:

```text
sample_data/sample.log
```

---

# CLI Expected Output

```text
Uploading: sample_data/sample.log

Job completed.

=================================================================
                    LOG ANALYSIS RESULT
=================================================================

Lines processed   : 11
Unparseable lines : 1

Service Name                         Error count
-----------------------------------------------------------------
auth-service                                  0
payment-service                               2
billing-service                               1
inventory-service                             0

-----------------------------------------------------------------

Top offender      : payment-service


Processing time   : 5.23 ms
=================================================================
```

The processing time will vary.

---

# Useful Commands

### Start server

```powershell
uvicorn app.main:app --reload
```

### Run CLI

```powershell
python client/cli.py sample_data/sample.log
```

### Check Git status

```powershell
git status
```

### Add files

```powershell
git add .
```

### Commit

```powershell
git commit -m "Build production log analyzer"
```

### Push

```powershell
git push -u origin main
```

### Deactivate virtual environment

```powershell
deactivate
```
