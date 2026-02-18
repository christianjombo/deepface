# Environment Variables

Environment variables control database connections, authentication, model loading, and other runtime behavior. The API loads variables from a `.env` file via `python-dotenv` in `deepface/api/src/app.py` (called on startup before the Flask app is created).

**Loading order:** Environment variables are read from the process environment and optionally from a `.env` file in the current working directory when the app starts. Place `.env` in `deepface/api/` when running the API, or configure it via your process manager (e.g. `docker run --env-file .env`).

---

## Reference Table

| Env Var | Required | Default | Example | Used In | Description | Secret? |
|---------|----------|---------|---------|---------|--------------|---------|
| `DEEPFACE_DATABASE_TYPE` | No | `postgres` | `postgres`, `mongo`, `weaviate`, `neo4j`, `pgvector`, `pinecone` | deepface/api/src/dependencies/variables.py:11 | Database backend for register/search/build_index | No |
| `DEEPFACE_CONNECTION_DETAILS` | Yes* | — | `postgresql://user:pass@host:5432/db` | deepface/api/src/dependencies/variables.py:18 | Connection string/URI. Overrides type-specific vars. Required for register, search, build/index | No** |
| `DEEPFACE_POSTGRES_URI` | No | — | `postgresql://user:pass@localhost:5432/deepface` | deepface/api/src/dependencies/variables.py:17-18, deepface/modules/database/postgres.py:76, pgvector.py:55, inventory.py:23 | Postgres connection string (when `DEEPFACE_CONNECTION_DETAILS` not set) | No** |
| `DEEPFACE_MONGO_URI` | No | — | `mongodb://localhost:27017/deepface` | deepface/api (via inventory), deepface/modules/database/mongo.py:49, inventory.py:28 | MongoDB connection string | No** |
| `DEEPFACE_WEAVIATE_URI` | No | — | `http://localhost:8080` | deepface/api (via inventory), inventory.py:33 | Weaviate URL (used by API/inventory) | No |
| `DEEPFACE_WEAVIATE_URL` | No | — | `http://localhost:8080` | deepface/modules/database/weaviate.py:47 | Weaviate URL fallback when client gets no connection_details | No |
| `DEEPFACE_NEO4J_URI` | No | — | `bolt://localhost:7687` | deepface/api (via inventory), deepface/modules/database/neo4j.py:41, inventory.py:38 | Neo4j bolt URI | No** |
| `DEEPFACE_PINECONE_API_KEY` | No | — | `<api-key>` | deepface/api (via inventory), deepface/modules/database/pinecone.py:40, inventory.py:48 | Pinecone API key | Yes |
| `TOKEN_DB_PATH` | No | `/data/deepface.db` | `/data/deepface.db` | deepface/api/src/dependencies/variables.py:25, container.py:10 | Path to SQLite database storing API tokens. Add tokens with `INSERT INTO api_tokens (name, token, status) VALUES ('name','token','active')` | No |
| `DEEPFACE_FACE_RECOGNITION_MODELS` | No | — | `VGG-Face,Facenet` | deepface/api/src/dependencies/variables.py:20, app.py:44-48 | Comma-separated models to load at startup | No |
| `DEEPFACE_FACE_DETECTION_MODELS` | No | — | `mtcnn` | deepface/api/src/dependencies/variables.py:21, app.py:50-54 | Comma-separated detector models to load at startup | No |
| `DEEPFACE_HOME` | No | `~` (user home) | `~/.deepface` | deepface/commons/folder_utils.py:34 | Base directory for model weights | No |
| `DEEPFACE_LOG_LEVEL` | No | `20` (INFO) | `10`, `20`, `30` | deepface/commons/logger.py:27 | Python logging level (10=DEBUG, 20=INFO, 30=WARNING) | No |
| `WEAVIATE_API_KEY` | No | — | `<key>` | deepface/modules/database/weaviate.py:50,53 | Weaviate API key when Weaviate has auth enabled | Yes |
| `WEAVIATE_HNSW_M` | No | `16` | `16` | deepface/modules/database/weaviate.py:99 | Weaviate HNSW M parameter for vector index | No |
| `DEEPFACE_PINECONE_CLOUD` | No | `aws` | `aws`, `gcp` | deepface/modules/database/pinecone.py:75 | Pinecone cloud provider | No |
| `DEEPFACE_PINECONE_REGION` | No | `us-east-1` | `us-east-1` | deepface/modules/database/pinecone.py:76 | Pinecone region | No |
| `yunet_score_threshold` | No | `0.9` | `0.9` | deepface/models/face_detection/YuNet.py:72 | YuNet detector score threshold | No |
| `YOLO_MIN_DETECTION_CONFIDENCE` | No | `0.25` | `0.25` | deepface/models/face_detection/Yolo.py:120 | YOLO minimum detection confidence | No |
| `MEDIAPIPE_MIN_DETECTION_CONFIDENCE` | No | `0.7` | `0.7` | deepface/models/face_detection/MediaPipe.py:37 | MediaPipe min detection confidence | No |
| `MEDIAPIPE_MODEL_SELECTION` | No | `0` | `0`, `1` | deepface/models/face_detection/MediaPipe.py:38 | MediaPipe model selection | No |
| `CENTERFACE_THRESHOLD` | No | `0.35` | `0.35` | deepface/models/face_detection/CenterFace.py:50 | CenterFace detection threshold | No |

\* Required for `/register`, `/search`, and `/build/index` endpoints. Other endpoints work without it.

\** May contain credentials; treat as secret in production.
