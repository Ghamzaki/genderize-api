# Genderize API — Name Classifier

A FastAPI endpoint that calls [Genderize.io](https://genderize.io), processes the response, and returns a structured result. Deployed on Vercel.

## Endpoint

### `GET /api/classify?name={name}`

**Success Response (200)**
```json
{
  "status": "success",
  "data": {
    "name": "john",
    "gender": "male",
    "probability": 0.99,
    "sample_size": 1234,
    "is_confident": true,
    "processed_at": "2026-04-01T12:00:00Z"
  }
}
```

**Error Responses**

| Status | Reason |
|--------|--------|
| 400 | Missing or empty `name` parameter |
| 422 | No prediction available for the name |
| 500/502 | Server or upstream failure |

All errors follow:
```json
{ "status": "error", "message": "<error message>" }
```

## Logic

- `sample_size` = renamed from `count` in the Genderize response
- `is_confident` = `true` only when `probability >= 0.7` **AND** `sample_size >= 100`
- `processed_at` = UTC timestamp generated fresh on every request (ISO 8601)
- If Genderize returns `gender: null` or `count: 0` → 422 error

## Project Structure

```
.
├── main.py           # FastAPI app + Mangum handler
├── requirements.txt  # Dependencies
├── vercel.json       # Vercel routing config
└── README.md         # Instructions
```

## Deploy to Vercel

### Option 1 — Vercel CLI (recommended)
```bash
npm i -g vercel
vercel        # follow prompts, links your GitHub repo
vercel --prod # promote to production
```

### Option 2 — Vercel Dashboard
1. Push this repo to GitHub
2. Go to [vercel.com](https://vercel.com) → New Project → Import your repo
3. Leave all settings as default — `vercel.json` handles everything
4. Click **Deploy**

Your live URL will be: `https://your-project.vercel.app`

## Run Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# API: http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

## Test Cases

```bash
BASE=https://your-project.vercel.app

# Success
curl "$BASE/api/classify?name=james"

# Missing name → 400
curl "$BASE/api/classify"

# Empty name → 400
curl "$BASE/api/classify?name="

# Unknown name (may trigger 422 edge case)
curl "$BASE/api/classify?name=xyzzyabc123"
```