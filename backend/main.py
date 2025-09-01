import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional

from .db import Base, engine, SessionLocal
from .models import Profile, Skill, ProfileSkill, Project, ProjectLink, ProjectSkill, Work
from .schemas import ProfileIn, ProfileOut, ProjectOut
from .auth import require_basic_auth
from .rate_limit import rate_limit

app = FastAPI(title="Me-API Playground", version="1.0.0")

# 🔹 Auto-seed database if empty
@app.on_event("startup")
def seed_if_empty():
    db = SessionLocal()
    profile = db.query(models.Profile).first()
    if not profile:
        # Load your profile.json file
        with open("sample_profile.json", "r") as f:
            data = json.load(f)

        # Insert profile into DB
        new_profile = models.Profile(
            name=data["name"],
            email=data["email"],
            education=data["education"],
            skills=json.dumps(data["skills"]),      # store array as JSON string
            projects=json.dumps(data["projects"]),  # store array as JSON string
            work=json.dumps(data["work"]),
            links=json.dumps(data["links"])
        )
        db.add(new_profile)
        db.commit()
    db.close()

allowed_origins = os.getenv("ALLOWED_ORIGINS", "*") #setting up CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allowed_origins == "*" else [o.strip() for o in allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/profile", response_model=ProfileOut)
def get_profile(db: Session = Depends(get_db)):
    profile = db.execute(select(Profile)).scalars().first()
    if not profile:
        raise HTTPException(404, "Profile not found. Seed the database.")
    return serialize_profile(profile)


@app.post("/profile", response_model=ProfileOut, dependencies=[Depends(require_basic_auth)])
def create_profile(data: ProfileIn, db: Session = Depends(get_db)):
    existing = db.execute(select(Profile)).scalars().first()
    if existing:
        raise HTTPException(400, "Profile already exists. Use PUT /profile to update.")
    profile = Profile(
        name=data.name,
        email=str(data.email),
        education=data.education,
        github=data.links.get("github"),
        linkedin=data.links.get("linkedin"),
        portfolio=data.links.get("portfolio"),
    )
    db.add(profile)
    db.flush() 

    skill_objs = [get_or_create_skill(db, s) for s in data.skills]
    for s in skill_objs:
        db.add(ProfileSkill(profile_id=profile.id, skill_id=s.id))

    for p in data.projects:
        proj = Project(profile_id=profile.id, title=p.title, description=p.description)
        db.add(proj)
        db.flush()
        for l in p.links:
            db.add(ProjectLink(project_id=proj.id, label=l.label, url=l.url))
        for sname in p.skills:
            s = get_or_create_skill(db, sname)
            db.add(ProjectSkill(project_id=proj.id, skill_id=s.id))

    for w in data.work:
        db.add(
            Work(
                profile_id=profile.id,
                company=w.company,
                title=w.title,
                start_date=w.start_date,
                end_date=w.end_date,
                description=w.description,
            )
        )

    db.commit()
    db.refresh(profile)
    return serialize_profile(profile)


@app.put("/profile", response_model=ProfileOut, dependencies=[Depends(require_basic_auth)])
def update_profile(data: ProfileIn, db: Session = Depends(get_db)):
    profile = db.execute(select(Profile)).scalars().first()
    if not profile:
        raise HTTPException(404, "Profile not found. Create it first.")

    profile.name = data.name
    profile.email = str(data.email)
    profile.education = data.education
    profile.github = data.links.get("github")
    profile.linkedin = data.links.get("linkedin")
    profile.portfolio = data.links.get("portfolio")

    db.query(ProfileSkill).filter(ProfileSkill.profile_id == profile.id).delete()
    for sname in data.skills:
        s = get_or_create_skill(db, sname)
        db.add(ProfileSkill(profile_id=profile.id, skill_id=s.id))

    db.query(ProjectLink).filter(
        ProjectLink.project_id.in_(db.query(Project.id).filter(Project.profile_id == profile.id))
    ).delete(synchronize_session=False)
    db.query(ProjectSkill).filter(
        ProjectSkill.project_id.in_(db.query(Project.id).filter(Project.profile_id == profile.id))
    ).delete(synchronize_session=False)
    db.query(Project).filter(Project.profile_id == profile.id).delete()
    db.flush()

    for p in data.projects:
        proj = Project(profile_id=profile.id, title=p.title, description=p.description)
        db.add(proj)
        db.flush()
        for l in p.links:
            db.add(ProjectLink(project_id=proj.id, label=l.label, url=l.url))
        for sname in p.skills:
            s = get_or_create_skill(db, sname)
            db.add(ProjectSkill(project_id=proj.id, skill_id=s.id))

    db.query(Work).filter(Work.profile_id == profile.id).delete()
    for w in data.work:
        db.add(
            Work(
                profile_id=profile.id,
                company=w.company,
                title=w.title,
                start_date=w.start_date,
                end_date=w.end_date,
                description=w.description,
            )
        )

    db.commit()
    db.refresh(profile)
    return serialize_profile(profile)


def get_or_create_skill(db: Session, name: str) -> Skill:
    name_clean = name.strip()
    s = db.execute(select(Skill).where(Skill.name.ilike(name_clean))).scalars().first()
    if s:
        return s
    s = Skill(name=name_clean)
    db.add(s)
    db.flush()
    return s


def serialize_profile(profile: Profile) -> ProfileOut:
    skills = sorted({s.name for s in profile.skills}, key=str.lower)
    projects = []
    for p in profile.projects:
        projects.append(
            {
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "links": [{"label": l.label, "url": l.url} for l in p.links],
                "skills": [s.name for s in p.skills],
            }
        )
    work = [
        {
            "id": w.id,
            "company": w.company,
            "title": w.title,
            "start_date": w.start_date,
            "end_date": w.end_date,
            "description": w.description,
        }
        for w in profile.work
    ]
    links = {
        "github": profile.github,
        "linkedin": profile.linkedin,
        "portfolio": profile.portfolio,
    }
    return {
        "id": profile.id,
        "name": profile.name,
        "email": profile.email,
        "education": profile.education,
        "skills": skills,
        "projects": projects,
        "work": work,
        "links": links,
    }


@app.get("/projects", response_model=list[ProjectOut])
def list_projects(
    skill: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    stmt = select(Project).order_by(Project.id.desc())
    if skill:
        stmt = stmt.join(Project.skills).where(Skill.name.ilike(skill))
    if q:
        like = f"%{q}%"
        stmt = stmt.where((Project.title.ilike(like)) | (Project.description.ilike(like)))
    stmt = stmt.limit(limit).offset(offset)
    rows = db.execute(stmt).scalars().unique().all()
    return [serialize_project(p) for p in rows]


@app.get("/skills/top")
def top_skills(limit: int = 5, db: Session = Depends(get_db)):
    stmt = (
        select(Skill.name, func.count(ProjectSkill.project_id).label("count"))
        .join(ProjectSkill, ProjectSkill.skill_id == Skill.id, isouter=True)
        .group_by(Skill.id)
        .order_by(func.count(ProjectSkill.project_id).desc(), Skill.name)
        .limit(limit)
    )
    rows = db.execute(stmt).all()
    return [{"skill": r[0], "count": int(r[1])} for r in rows]


@app.get("/search")
def search(q: str, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    like = f"%{q}%"
    proj_stmt = (
        select(Project)
        .where((Project.title.ilike(like)) | (Project.description.ilike(like)))
        .limit(limit)
        .offset(offset)
    )
    projects = db.execute(proj_stmt).scalars().all()
    skills = (
        db.execute(select(Skill).where(Skill.name.ilike(like)).limit(limit).offset(offset))
        .scalars()
        .all()
    )
    return {
        "projects": [serialize_project(p) for p in projects],
        "skills": [s.name for s in skills],
    }


def serialize_project(p: Project) -> dict:
    return {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "links": [{"label": l.label, "url": l.url} for l in p.links],
        "skills": [s.name for s in p.skills],
    }


frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


@app.middleware("http")
async def add_rate_limit_and_logging(request: Request, call_next):
    if request.url.path != "/health":
        rate_limit(request)
    response = await call_next(request)
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )
