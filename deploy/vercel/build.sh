#!/usr/bin/env bash
# Assembles the Vercel deployment of the CV service (ONNX Runtime, no torch) into <out-dir>.
# Needs the dev environment (ultralytics) once, to export yolo11n.onnx from yolo11n.pt.
# usage: deploy/vercel/build.sh <out-dir>   then: cd <out-dir> && vercel deploy --prod
set -euo pipefail
root=$(cd "$(dirname "$0")/../.." && pwd)
out=${1:?usage: build.sh <out-dir>}
python=${PYTHON:-python}

if [ ! -f "$root/yolo11n.onnx" ]; then
  (cd "$root" && "$python" -c "from ultralytics import YOLO; YOLO('yolo11n.pt').export(format='onnx', imgsz=640, simplify=True, opset=17)")
fi

rm -rf "$out" && mkdir -p "$out"
cp -R "$root/app" "$out/app"
find "$out/app" -name __pycache__ -prune -exec rm -rf {} +
cp "$root/yolo11n.onnx" "$root/deploy/vercel/requirements.txt" "$root/deploy/vercel/vercel.json" "$out/"
echo 3.14 > "$out/.python-version"
echo "Bundle ready in $out (MODEL_PATH=yolo11n.onnx, set CV_API_TOKEN in the Vercel project)."
