from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .db import Base

class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    education: Mapped[str] = mapped_column(Text, default="")

    github: Mapped[str | None] = mapped_column(String(255), nullable=True)
    linkedin: Mapped[str | None] = mapped_column(String(255), nullable=True)
    portfolio: Mapped[str | None] = mapped_column(String(255), nullable=True)

    skills = relationship("Skill", secondary="profile_skills", back_populates="profiles", lazy="joined")
    projects = relationship("Project", back_populates="profile", cascade="all, delete-orphan")
    work = relationship("Work", back_populates="profile", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    level: Mapped[int | None] = mapped_column(Integer, nullable=True)  # optional 1..5

    profiles = relationship("Profile", secondary="profile_skills", back_populates="skills")
    projects = relationship("Project", secondary="project_skills", back_populates="skills")


class ProfileSkill(Base):
    __tablename__ = "profile_skills"
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), primary_key=True)


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str] = mapped_column(Text)

    profile = relationship("Profile", back_populates="projects")
    links = relationship("ProjectLink", back_populates="project", cascade="all, delete-orphan")
    skills = relationship("Skill", secondary="project_skills", back_populates="projects")


class ProjectLink(Base):
    __tablename__ = "project_links"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    label: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(500))

    project = relationship("Project", back_populates="links")


class ProjectSkill(Base):
    __tablename__ = "project_skills"
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), primary_key=True)


class Work(Base):
    __tablename__ = "work"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), index=True)
    company: Mapped[str] = mapped_column(String(200))
    title: Mapped[str] = mapped_column(String(200))
    start_date: Mapped[str] = mapped_column(String(20))  # ISO date string for simplicity
    end_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")

    profile = relationship("Profile", back_populates="work")
