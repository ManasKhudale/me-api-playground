from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class LinkOut(BaseModel):
    label: str
    url: str

class ProjectIn(BaseModel):
    title: str
    description: str
    links: List[LinkOut] = []
    skills: List[str] = []

class ProjectOut(ProjectIn):
    id: int

class WorkIn(BaseModel):
    company: str
    title: str
    start_date: str
    end_date: Optional[str] = None
    description: str = ""

class WorkOut(WorkIn):
    id: int

class ProfileIn(BaseModel):
    name: str
    email: EmailStr
    education: str = ""
    skills: List[str] = []
    projects: List[ProjectIn] = []
    work: List[WorkIn] = []
    links: dict = Field(default_factory=dict)  # {github, linkedin, portfolio}

class ProfileOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    education: str
    skills: List[str]
    projects: List[ProjectOut]
    work: List[WorkOut]
    links: dict
