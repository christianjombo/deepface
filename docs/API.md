# DeepFace API Reference

## Overview

The DeepFace API exposes face verification, analysis, representation, registration, and search via HTTP endpoints. It runs as a Flask app served by Gunicorn.

### Base URL and Ports

| Run method | Base URL | Port |
|------------|----------|------|
| Local script (`scripts/service.sh`) | `http://localhost:5005` | 5005 |
| Docker (`scripts/dockerize.sh`) | `http://localhost:5005` | 5005 (host) → 5000 (container) |
| Docker direct | `http://localhost:5000` | 5000 (container) |

### Running the API

**Via script (Gunicorn):**
```shell
cd scripts && ./service.sh
```

**Via Docker:**
```shell
cd scripts && ./dockerize.sh
```
Uses `deepface/api/.env` if present.

**Direct Docker run:**
```shell
docker build -t deepface .
docker run -p 5005:5000 --env-file deepface/api/.env deepface
```

---

## Authentication

Authentication is always enabled. All POST endpoints require a valid Bearer token stored in the SQLite token database (`TOKEN_DB_PATH`, default `/data/deepface.db`).

**Header:**
```
Authorization: Bearer <token>
```

**Example:**
```bash
curl -X POST http://localhost:5005/represent \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"img": "path/to/image.jpg"}'
```

**Token database:** Tokens are stored in the `api_tokens` table. Add tokens with:

```sql
INSERT INTO api_tokens (name, token, status) VALUES ('my-team', 'your-secret-token', 'active');
```

Configure the DB path with `TOKEN_DB_PATH` (e.g. `/data/deepface.db`). Mount the SQLite file into the container at `/data/deepface.db` in production.

---

## Endpoints

### GET /

| Field | Value |
|-------|-------|
| **Purpose** | Welcome page |
| **Auth required** | No |
| **Response** | HTML |

**Example:**
```bash
curl http://localhost:5005/
```

**Response (200):**
```html
<h1>Welcome to DeepFace API v0.0.XX!</h1>
```

---

### POST /represent

| Field | Value |
|-------|-------|
| **Purpose** | Extract face embedding vectors from an image |
| **Auth required** | Yes |
| **Request** | JSON or form-data; image via `img` (path, URL, base64) or multipart file |

**Request body (JSON):**

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| img | string | Yes | — | Image as path, URL, or base64 string |
| model_name | string | No | `VGG-Face` | Recognition model |
| detector_backend | string | No | `opencv` | Face detector |
| enforce_detection | boolean | No | `true` | Fail if no face detected |
| align | boolean | No | `true` | Align face |
| anti_spoofing | boolean | No | `false` | Enable anti-spoofing |
| max_faces | int | No | — | Max faces to process (null = all) |

**Example:**
```bash
curl -X POST http://localhost:5005/represent \
  -H "Content-Type: application/json" \
  -d '{"img": "path/to/image.jpg", "model_name": "Facenet"}'
```

**Response (200):**
```json
{
  "results": [
    {
      "embedding": [0.1, -0.2, ...],
      "face_region": {"x": 10, "y": 20, "w": 100, "h": 100},
      "facial_area": {...}
    }
  ]
}
```

**Errors:** 400 (missing/invalid img, processing error), 401 (auth failure)

---

### POST /verify

| Field | Value |
|-------|-------|
| **Purpose** | Compare two faces and return verification result |
| **Auth required** | Yes |
| **Request** | JSON or form-data; images via `img1` and `img2` |

**Request body (JSON):**

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| img1 | string | Yes | — | First image (path, URL, base64) |
| img2 | string | Yes | — | Second image |
| model_name | string | No | `VGG-Face` | Recognition model |
| detector_backend | string | No | `opencv` | Face detector |
| distance_metric | string | No | `cosine` | `cosine`, `euclidean`, etc. |
| enforce_detection | boolean | No | `true` | Fail if no face |
| align | boolean | No | `true` | Align faces |
| anti_spoofing | boolean | No | `false` | Anti-spoofing |

**Example:**
```bash
curl -X POST http://localhost:5005/verify \
  -H "Content-Type: application/json" \
  -d '{"img1": "person1.jpg", "img2": "person2.jpg"}'
```

**Response (200):**
```json
{
  "verified": true,
  "distance": 0.25,
  "threshold": 0.4,
  "model": "VGG-Face",
  "detector_backend": "opencv",
  "similarity_metric": "cosine"
}
```

**Errors:** 400 (missing/invalid images, processing error), 401 (auth failure)

---

### POST /analyze

| Field | Value |
|-------|-------|
| **Purpose** | Analyze facial attributes (age, gender, emotion, race) |
| **Auth required** | Yes |
| **Request** | JSON or form-data; image via `img` |

**Request body (JSON):**

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| img | string | Yes | — | Image (path, URL, base64) |
| actions | list/string | No | `["age","gender","emotion","race"]` | Attributes to analyze |
| detector_backend | string | No | `opencv` | Face detector |
| enforce_detection | boolean | No | `true` | Fail if no face |
| align | boolean | No | `true` | Align face |
| anti_spoofing | boolean | No | `false` | Anti-spoofing |

**Example:**
```bash
curl -X POST http://localhost:5005/analyze \
  -H "Content-Type: application/json" \
  -d '{"img": "photo.jpg", "actions": ["age", "gender"]}'
```

**Response (200):**
```json
{
  "results": [
    {
      "age": 32,
      "dominant_gender": "Man",
      "gender": {"Man": 0.98, "Woman": 0.02},
      "dominant_emotion": "neutral",
      "emotion": {...},
      "dominant_race": "white",
      "race": {...},
      "region": {"x": 10, "y": 20, "w": 100, "h": 100}
    }
  ]
}
```

**Errors:** 400 (missing/invalid img, processing error), 401 (auth failure)

---

### POST /register

| Field | Value |
|-------|-------|
| **Purpose** | Register a face embedding into the database |
| **Auth required** | Yes |
| **Request** | JSON or form-data; image via `img` |
| **Requires** | `DEEPFACE_CONNECTION_DETAILS` or type-specific connection env |

**Request body (JSON):**

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| img | string | Yes | — | Image (path, URL, base64) |
| img_name | string | No | — | Identifier for the registered face |
| model_name | string | No | `VGG-Face` | Recognition model |
| detector_backend | string | No | `opencv` | Face detector |
| enforce_detection | boolean | No | `true` | Fail if no face |
| align | boolean | No | `true` | Align face |
| l2_normalize | boolean | No | `false` | L2 normalize embedding |
| expand_percentage | int | No | `0` | Expand face region |
| normalization | string | No | `base` | Embedding normalization |
| anti_spoofing | boolean | No | `false` | Anti-spoofing |

**Example:**
```bash
curl -X POST http://localhost:5005/register \
  -H "Content-Type: application/json" \
  -d '{"img": "person.jpg", "img_name": "alice"}'
```

**Response (200):** Dict with registration confirmation (structure varies by database)

**Errors:** 400 (missing/invalid img), 401 (auth failure), 500 (missing `DEEPFACE_CONNECTION_DETAILS` or DB error)

---

### POST /search

| Field | Value |
|-------|-------|
| **Purpose** | Search for similar faces in the database |
| **Auth required** | Yes |
| **Request** | JSON or form-data; image via `img` |
| **Requires** | `DEEPFACE_CONNECTION_DETAILS` or type-specific connection env |

**Request body (JSON):**

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| img | string | Yes | — | Image (path, URL, base64) |
| model_name | string | No | `VGG-Face` | Recognition model |
| detector_backend | string | No | `opencv` | Face detector |
| enforce_detection | boolean | No | `true` | Fail if no face |
| align | boolean | No | `true` | Align face |
| distance_metric | string | No | `cosine` | Similarity metric |
| l2_normalize | boolean | No | `false` | L2 normalize |
| expand_percentage | int | No | `0` | Expand face region |
| normalization | string | No | `base` | Embedding normalization |
| anti_spoofing | boolean | No | `false` | Anti-spoofing |
| search_method | string | No | `exact` | `exact` or `ann` |
| similarity_search | boolean | No | `false` | Use similarity search |
| k | int | No | `5` | Number of results |

**Example:**
```bash
curl -X POST http://localhost:5005/search \
  -H "Content-Type: application/json" \
  -d '{"img": "query.jpg", "model_name": "Facenet", "k": 5}'
```

**Response (200):**
```json
{
  "results": [
    [
      {"img_name": "alice", "distance": 0.2, ...},
      {"img_name": "bob", "distance": 0.35, ...}
    ]
  ]
}
```

**Errors:** 400 (missing/invalid img), 401 (auth failure), 500 (missing connection details or DB error)

---

### POST /build/index

| Field | Value |
|-------|-------|
| **Purpose** | Build vector index for ANN search (postgres, mongo) |
| **Auth required** | Yes |
| **Request** | JSON or form-data |
| **Requires** | `DEEPFACE_CONNECTION_DETAILS` or type-specific connection env |

**Request body (JSON):**

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| model_name | string | No | `VGG-Face` | Recognition model |
| detector_backend | string | No | `opencv` | Face detector |
| align | boolean | No | `true` | Align face |
| l2_normalize | boolean | No | `false` | L2 normalize |

**Example:**
```bash
curl -X POST http://localhost:5005/build/index \
  -H "Content-Type: application/json" \
  -d '{"model_name": "Facenet"}'
```

**Response (200):**
```json
{
  "message": "Index built successfully"
}
```

**Errors:** 400 (processing error), 401 (auth failure), 500 (missing connection details or DB error)

---

## Error Responses

| Status | When | Body example |
|--------|------|--------------|
| 400 | Missing/invalid image, processing exception | `{"exception": "..."}` or `{"error": "..."}` |
| 401 | Missing or invalid Bearer token | `{"message": "Invalid or missing authentication token"}` |
| 500 | Missing `DEEPFACE_CONNECTION_DETAILS` for register/search/build_index | `{"error": "Database connection details must be provided in \`DEEPFACE_CONNECTION_DETAILS\` environment variables"}` |
