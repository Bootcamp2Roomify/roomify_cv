FROM python:3.14.9-slim

# OpenCV (pulled in by ultralytics) needs these shared libraries at runtime.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt requirements.lock ./
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu \
        -r requirements.txt -c requirements.lock

COPY app ./app
# Bake the weights into the image so containers start without a network download.
RUN python -c "from ultralytics import YOLO; YOLO('yolo11n.pt')"

RUN useradd --create-home --uid 10001 roomify && chown -R roomify /app
USER roomify
ENV CV_HOST=0.0.0.0 CV_PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host ${CV_HOST} --port ${CV_PORT}"]
