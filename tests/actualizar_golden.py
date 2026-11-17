"""Regenera tests/golden a partir del código actual. Úsalo SOLO tras un cambio intencional."""
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from caat.config import Config  # noqa: E402
from caat.main import ejecutar  # noqa: E402

GOLDEN = Path(__file__).parent / "golden"

with tempfile.TemporaryDirectory() as tmp:
    salida = Path(tmp)
    ejecutar(Config(), salida, con_figuras=False)
    shutil.copy(salida / "results.json", GOLDEN / "results.json")
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((salida / "data").glob("*.csv"))}
    (GOLDEN / "csv_sha256.json").write_text(json.dumps(hashes, indent=1))
print("Golden actualizado en", GOLDEN)
