# Roomify Computer Vision Service

FastAPI service that finds the main furniture in a room photo for **Roomify**. The Spring backend
([roomify_backend](https://github.com/Bootcamp2Roomify/roomify_backend)) uploads each project photo
here and stores the results; people then review, correct and decide on every item
([roomify_frontend](https://github.com/Bootcamp2Roomify/roomify_frontend)).

> **Release v1.0.1 — live** as a Vercel Function behind <https://roomify-rooms.vercel.app> (YOLO11n on
> ONNX Runtime; see "Live deployment" below). This service is fully tested and involves no AI provider.
> The wider app's AI features run in demo mode in the live build and are not verified against the live
> OpenAI API.

## Model

[Ultralytics YOLO11n](https://docs.ultralytics.com/models/yolo11/) (COCO-pretrained, CPU-friendly,
~5 MB). Six COCO classes are returned, renamed for people: bed, chair, sofa (couch), table (dining
table), tv, plant (potted plant) — see `TARGET_CLASSES` in `app/detector.py`. COCO has no desk,
wardrobe, shelf or lamp class, so those are never detected; people add them by hand during review.
Detections below `CONFIDENCE_THRESHOLD` are dropped. The model is not fine-tuned for interiors; measured accuracy and
failure cases are in the submission package (`roomify_backend/docs/submission/`).

## API

| Method | Path | Body | Returns |
|---|---|---|---|
| GET | `/health` | – | `{"status":"ok"}` |
| POST | `/v1/analyze` | multipart `file` (JPG/PNG) **or** form `image_url` (public http(s) only) | `{modelVersion, processingTimeMs, objects:[{label, confidence, bbox:{x,y,w,h}}]}` with boxes normalized to 0–1 |
| POST | `/detect` | multipart `file` | debug output with pixel boxes |

`image_url` is only fetched when it resolves to a public address and redirects are not followed
(SSRF protection). With `CV_API_TOKEN` set, `/v1/analyze` and `/detect` require
`Authorization: Bearer <token>` (the backend sends `VISION_SERVICE_API_TOKEN`); `/health` stays open.
Without it the service has no authentication, so **run it on a private network** reachable only by
the backend.

## Run locally

Python 3.14:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -c requirements.lock -r requirements-dev.txt
cp .env.example .env   # optional; defaults work
uvicorn app.main:app --host 127.0.0.1 --port 8000
curl -F file=@samples/room.jpeg localhost:8000/v1/analyze
```

The weights download on first start if `yolo11n.pt` is not present.

Container (CPU-only torch, weights baked in, non-root):

```bash
docker build -t roomify-cv .
docker run --rm -p 127.0.0.1:8000:8000 roomify-cv
```

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `CONFIDENCE_THRESHOLD` | `0.25` | Minimum confidence returned |
| `MODEL_PATH` | `yolo11n.pt` | Weights file or model name; a `.onnx` file runs on ONNX Runtime without torch |
| `CV_API_TOKEN` | – | Bearer token required on detection endpoints when set |
| `CV_HOST`, `CV_PORT` | `0.0.0.0`, `8000` | Container bind address |

### Live deployment (Vercel)

The public instance runs as a Vercel Python Function at `https://roomify-cv.vercel.app`, on ONNX
Runtime instead of torch (`app/onnx_yolo.py`): about 175 MB of memory instead of about 510 MB and a
bundle far below Vercel's 500 MB limit. On the 60-image COCO evaluation set it matches the torch
pipeline (precision 0.706 vs 0.702, recall 0.635 vs 0.623; the small gap comes from square instead of
rectangular letterboxing).

```bash
deploy/vercel/build.sh /tmp/roomify-cv-vercel     # exports yolo11n.onnx once, assembles the bundle
cd /tmp/roomify-cv-vercel && vercel link --project roomify-cv && vercel deploy --prod
```

Project environment: `MODEL_PATH=yolo11n.onnx`, `CV_API_TOKEN=<random 32-byte hex>`.

## Test

```bash
python -m pytest -q
```

CI installs the pinned tree (`requirements.lock`) with CPU-only torch, runs the tests on torch and
again on the exported ONNX model, and builds the image.

## Contributing

[CONTRIBUTING.md](CONTRIBUTING.md)

## License

**AGPL-3.0** ([LICENSE](LICENSE)), matching [Ultralytics YOLO](https://github.com/ultralytics/ultralytics),
which this service uses for inference. If you run a modified version as a network service, AGPL
requires offering its source to that service's users. Code contributed before 2026-10-24 was MIT;
its notice is kept in [NOTICE](NOTICE).
