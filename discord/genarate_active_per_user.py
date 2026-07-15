import json
import sys
from collections import Counter
from pathlib import Path


APPROVALS_FILE = Path(__file__).resolve().parents[1] / "approvals.json"
OUTPUT_FILE = Path(__file__).resolve().with_name("active_per_user.json")


def get_discord_id(item: dict) -> int | None:
	submitted_by = item.get("submittedby") or item.get("submittedBy") or {}
	discord_id = submitted_by.get("discordId")

	if discord_id is None:
		return None

	try:
		return int(discord_id)
	except (TypeError, ValueError):
		return None


def main() -> int:
	try:
		with APPROVALS_FILE.open("r", encoding="utf-8") as f:
			approvals = json.load(f)
	except FileNotFoundError:
		print(f"Could not find approvals file: {APPROVALS_FILE}", file=sys.stderr)
		return 1
	except json.JSONDecodeError as exc:
		print(f"Invalid JSON in {APPROVALS_FILE}: {exc}", file=sys.stderr)
		return 1

	counts = Counter()
	for item in approvals:
		if item.get("status") != "approved":
			continue

		discord_id = get_discord_id(item)
		if discord_id is None:
			continue

		counts[discord_id] += 1

	result = [
		{"user": user_id, "photos": photo_count}
		for user_id, photo_count in sorted(counts.items(), key=lambda pair: pair[1], reverse=True)
	]

	with OUTPUT_FILE.open("w", encoding="utf-8") as f:
		json.dump(result, f, indent=2)

	print(json.dumps(result, indent=2))
	print(f"\nSaved: {OUTPUT_FILE}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
