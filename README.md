# Roomify Computer Vision Service

Computer-vision service for **Roomify**, an AI-powered room redesign and DIY planning application.

This service analyzes uploaded room images, detects visible furniture, and returns structured detection results for the Spring Boot backend REST API. It is maintained separately from the [Roomify Backend](https://github.com/Bootcamp2Roomify/roomify_backend) and [Roomify Frontend](https://github.com/Bootcamp2Roomify/roomify_frontend).

The current Sprint 1 prototype uses FastAPI with a pretrained YOLO11n object detector. It accepts one JPEG or PNG image and returns detected furniture labels, confidence scores, and pixel bounding boxes.

---

## Current Sprint 1 Implementation

The first computer-vision milestone has been implemented as a local prototype.

Current capabilities:

- 🖼️ Accept one JPEG or PNG room image through FastAPI
- 👁️ Analyze visible room content using pretrained YOLO11n
- 🪑 Detect a limited set of major furniture classes
- 🏷️ Normalize detected furniture labels for Roomify
- 📊 Return confidence scores
- 📦 Return pixel bounding boxes
- ⚠️ Handle images with no supported detections without crashing
- 🚫 Reject unsupported file types
- 🧪 Provide automated API tests
- 🖼️ Provide a development sample image for testing
- 📄 Provide Swagger API documentation

The prototype currently runs independently. Spring Boot backend integration, persistent image storage, and cloud deployment will be implemented in later stages.

---

## Planned MVP Features

The following capabilities are planned for the Roomify MVP and should not be treated as completed until they have been implemented, tested, and documented.

- 🖼️ Receive room images for analysis
- 👁️ Analyze visible room content
- 🪑 Detect common furniture items
- 🏷️ Return furniture labels
- 📦 Return approximate object locations or bounding boxes
- 🔗 Communicate with the Spring Boot backend
- ⚠️ Report failed or incomplete image analysis
- 🧪 Support an initial computer-vision prototype
- 📊 Return structured JSON results

Some of these capabilities are already included in the current Sprint 1 prototype, while backend integration and cloud infrastructure remain future work.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| Language | Python |
| Computer Vision | Ultralytics YOLO11n |
| Image Processing | Pillow |
| Testing | Pytest, FastAPI TestClient |
| Main Client | Roomify Spring Boot backend |
| Image Storage | AWS S3 or compatible cloud object storage — planned for later integration |
| Secret Management | AWS Secrets Manager — planned for deployment/integration |
| Deployment | Not yet decided |

The Sprint 1 prototype uses pretrained YOLO11n without custom training. Model fine-tuning, image-storage integration, and deployment architecture will be evaluated in later stages.

---

## System Architecture

Roomify uses separate repositories for its frontend, backend, and computer-vision service.

```text
Next.js Frontend
        |
        v
Spring Boot REST API
        |
        v
Python FastAPI CV Service
        |
        v
Furniture Detection Results
```

The frontend should communicate with the Spring Boot backend rather than calling this service directly.

The Spring Boot backend sends an authorized room-image analysis request to the computer-vision service. The service processes the image and returns structured detection results to the backend.

---

## Planned Project Structure

```text
app/
├── api/                 # FastAPI routes
├── core/                # Configuration and application settings
├── models/              # Computer-vision model integration
├── schemas/             # Request and response schemas
├── services/            # Image-analysis and detection logic
├── utils/               # Image and data utilities
└── main.py              # FastAPI application entry point

tests/                   # Automated tests
scripts/                 # Development and model scripts
models/                  # Local model files ignored by Git
.env.example
.gitignore
CONTRIBUTING.md
README.md
```

The exact structure may be updated when the first computer-vision prototype is initialized.

---

## Planned Detection Response

The service is expected to return structured data similar to:

```json
{
  "status": "completed",
  "detections": [
    {
      "label": "chair",
      "confidence": 0.91,
      "bounding_box": {
        "x": 120,
        "y": 80,
        "width": 240,
        "height": 360
      }
    }
  ]
}
```

This example documents the planned response format. It is not a guarantee that the endpoint or schema has already been implemented.

---

## Development Setup

### Clone the Repository

```bash
git clone https://github.com/Bootcamp2Roomify/roomify_cv.git
cd roomify_cv
```

### Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```text
.venv\Scripts\activate
```

### Configure the Environment

Create a local environment file:

```bash
cp .env.example .env
```

Replace placeholders with local development values. Never commit the completed `.env` file.

### Install and Run

Dependency installation and startup commands will be finalized after the FastAPI service and its dependency files are initialized.

The planned local service URL is:

```text
http://localhost:8000
```

The planned FastAPI documentation URL is:

```text
http://localhost:8000/docs
```

---

## Image and Model Files

Large or generated files should not be committed directly to GitHub.

The `.gitignore` file should exclude:

- Uploaded room images
- Generated redesign images
- Temporary processed images
- Trained model weights
- Local datasets
- Python cache files
- Virtual environments
- Completed `.env` files
- Logs and test coverage output

Small configuration files and documentation required to reproduce the project may be committed after review.

---

## Security and Privacy

The computer-vision service may process user-uploaded room images. These images may contain personal belongings or other private information.

Contributors must not commit:

- User-uploaded room images
- Personal user data
- Completed `.env` files
- OpenAI or Gemini API keys
- AWS access keys
- Cloud-storage credentials
- Private model credentials
- Database credentials
- JWT secrets
- Private keys or certificates

Production secrets should be stored securely using AWS Secrets Manager.

The service should return safe error messages and should not expose internal paths, credentials, stack traces, or private image-storage locations to users.

---

## Technical Limitations

The Roomify computer-vision MVP:

- May incorrectly identify or classify furniture
- May fail to detect partially hidden objects
- May produce lower-quality results for dark, blurry, crowded, or low-resolution images
- Cannot determine centimeter-perfect room dimensions from a single photograph
- Cannot guarantee the physical dimensions of detected furniture
- Cannot guarantee that recommended furniture will fit
- Does not create a complete three-dimensional room model
- Should present detection confidence as an estimate rather than a guarantee

Users must be allowed to review and correct detected furniture before a redesign is generated.

---

## Git Workflow

This project follows a feature-branch and Pull Request workflow.

```text
main
│
└── develop
      ├── feature/*
      ├── fix/*
      └── docs/*
```

- `main` — stable and production-ready code
- `develop` — integration branch for reviewed development work
- `feature/*` — new features
- `fix/*` — bug fixes
- `docs/*` — documentation changes

Team members should not push development work directly into `main` or `develop`.

---

## Commit Convention

Roomify uses Conventional Commits:

```text
feat: new feature
fix: bug fix
refactor: code restructuring without behavior changes
docs: documentation changes
test: adding or updating tests
chore: project setup or maintenance
```

Examples:

```text
feat(detection): add furniture detection endpoint
fix(image): reject unsupported image formats
docs: update computer vision setup instructions
test(detection): add furniture detection tests
chore: configure Python gitignore
```

---

## Create a Feature Branch

Create new work from the latest `develop` branch:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature
```

Examples:

```text
feature/image-analysis
feature/furniture-detection
fix/image-validation
docs/cv-setup
```

---

## Open a Pull Request

Create Pull Requests from working branches into `develop`:

```text
feature/* → develop
fix/* → develop
docs/* → develop
```

Stable releases are merged from:

```text
develop → main
```

Pull Request titles must include the related Jira issue key:

```text
[ROOM-###] <type>: Brief description
```

Example:

```text
[ROOM-7] docs: Set up computer vision repository and Git workflow
```

Each Pull Request must be reviewed by at least one teammate before it is merged.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the complete contribution guidelines.

---

## Related Repositories

- [Roomify Frontend](https://github.com/Bootcamp2Roomify/roomify_frontend) — Next.js, React, TypeScript, and Tailwind CSS
- [Roomify Backend](https://github.com/Bootcamp2Roomify/roomify_backend) — Java and Spring Boot REST API

---

## License

This project is licensed under the MIT License.
