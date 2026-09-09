"""Seed script: creates a few sample notes."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from notes.models import Note


def seed():
    db = SessionLocal()
    try:
        if db.query(Note).count() == 0:
            notes = [
                Note(title="Welcome!", content="This is a sample note. Edit or delete it to get started.", is_pinned=True),
                Note(title="Markdown works fine", content="Notes are plain text — render it as Markdown on the frontend if you like."),
                Note(title="Archived example", content="This note starts archived to show the /notes?archived=true filter.", is_archived=True),
            ]
            db.add_all(notes)
            db.commit()
            print("Created sample notes")
        print("Seed complete!")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
