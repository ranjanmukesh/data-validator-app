"""Simple app that loads the validated users dataset."""
import json
from pathlib import Path

DATA_PATH = Path("/app/data/users.json")


def main():
    if not DATA_PATH.exists():
        raise SystemExit(f"Dataset not found at {DATA_PATH}")

    users = json.loads(DATA_PATH.read_text())
    print(f"Loaded {len(users)} users from validated dataset:")
    for user in users:
        print(f"  - {user['name']} ({user['email']}), age {user['age']}")


if __name__ == "__main__":
    main()
