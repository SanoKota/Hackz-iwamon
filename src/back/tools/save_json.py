import os
import json
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4


def _ensure_dir(path: str) -> None:
	os.makedirs(path, exist_ok=True)


def _make_filename(prefix: Optional[str] = None) -> str:
	ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
	uid = uuid4().hex[:8]
	if prefix:
		safe = prefix.replace(" ", "_")
		return f"{safe}_{ts}_{uid}.json"
	return f"{ts}_{uid}.json"


def save_json(data: Any, folder: str = "data/json") -> str:
	"""Save `data` (dict or JSON-serializable object) to a .json file.

	- If `data` is a str, attempt to parse as JSON; otherwise wrap as {"response": data}.
	- Writes to `data/json/geminioutput.json` by default.
	- Ensures the folder exists and returns the written file path.
	"""
	_ensure_dir(folder)

	obj = data
	if isinstance(data, str):
		try:
			obj = json.loads(data)
		except Exception:
			obj = {"response": data}

	filename = 'geminioutput.json'
	path = os.path.join(folder, filename)
	with open(path, "w", encoding="utf-8") as f:
		# Use default=str to allow non-JSON-serializable objects to be stringified
		json.dump(obj, f, ensure_ascii=False, indent=2, default=str)

	return path


if __name__ == "__main__":
	# simple test
	sample = {"hello": "世界", "time": datetime.utcnow().isoformat()}
	out = save_json(sample, folder="data/json")
	print("Wrote:", out)

