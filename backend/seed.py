import json
from pathlib import Path

from .db import Base, engine, SessionLocal
from .models import Profile, Skill, ProfileSkill, Project, ProjectLink, ProjectSkill, Work


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Clear existing data
        db.query(ProjectLink).delete()
        db.query(ProjectSkill).delete()
        db.query(Project).delete()
        db.query(ProfileSkill).delete()
        db.query(Work).delete()
        db.query(Skill).delete()
        db.query(Profile).delete()
        db.commit()

        # Load JSON
        json_path = Path(__file__).resolve().parent.parent / "sample_profile.json"
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # --- Profile ---
        profile = Profile(
            name=data["name"],
            email=data["email"],
            education=data["education"],
            github=data["links"].get("github"),
            linkedin=data["links"].get("linkedin"),
            portfolio=data["links"].get("resume"),  # using "resume" since JSON has it
        )
        db.add(profile)
        db.flush()

        # --- Skills ---
        skills = {}
        for s in data.get("skills", []):
            sk = Skill(name=s)
            db.add(sk)
            db.flush()
            skills[s] = sk
            db.add(ProfileSkill(profile_id=profile.id, skill_id=sk.id))

        # --- Projects ---
        for proj in data.get("projects", []):
            p = Project(
                profile_id=profile.id,
                title=proj["title"],
                description=proj["description"],
            )
            db.add(p)
            db.flush()

            # Project links
            for link in proj.get("links", []):
                db.add(ProjectLink(project_id=p.id, label=link["label"], url=link["url"]))

            # Project skills
            for s in proj.get("skills", []):
                if s in skills:
                    db.add(ProjectSkill(project_id=p.id, skill_id=skills[s].id))
                else:
                    # If skill wasn’t in top-level "skills", add it now
                    sk = Skill(name=s)
                    db.add(sk)
                    db.flush()
                    skills[s] = sk
                    db.add(ProjectSkill(project_id=p.id, skill_id=sk.id))

        # --- Work ---
        for job in data.get("work", []):
            db.add(
                Work(
                    profile_id=profile.id,
                    company=job["company"],
                    title=job["title"],
                    start_date=job["start_date"],
                    end_date=job.get("end_date"),
                    description=job.get("description", ""),
                )
            )

        db.commit()
        print("✅ Seed complete with sample_profile.json")

    finally:
        db.close()


if __name__ == "__main__":
    main()
