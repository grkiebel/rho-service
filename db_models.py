from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel
from sqlalchemy import JSON, Column, DateTime, func
from sqlmodel import Field, SQLModel
from sqlmodel import Relationship


class WorkStatusCodes(BaseModel):
    NEW: str = "new"
    PROCESSING: str = "processing"
    FAILED: str = "failed"
    SUCCEEDED: str = "succeeded"


work_status = WorkStatusCodes()


class DbTool(SQLModel, table=True):
    __tablename__ = "tools"
    tool_id: str = Field(primary_key=True)
    tool_skills: Dict = Field(sa_column=Column(JSON))
    created_at: datetime = Field(
        sa_column=Column(DateTime(), server_default=func.now())
    )
    enabled: bool = Field(default=True)
    ready_since: datetime | None = Field(default=None)
    work_id: Optional[int] = Field(foreign_key="work.work_id")
    work: Optional["DbWork"] = Relationship(back_populates="tool")


class DbTask(SQLModel, table=True):
    __tablename__ = "tasks"
    task_id: str = Field(primary_key=True)
    task_needs: Dict = Field(sa_column=Column(JSON))
    created_at: datetime = Field(
        sa_column=Column(DateTime(), server_default=func.now())
    )
    work_id: int | None = Field(foreign_key="work.work_id")
    work: Optional["DbWork"] = Relationship(back_populates="task")


class DbWork(SQLModel, table=True):
    __tablename__ = "work"
    work_id: int | None = Field(default=None, primary_key=True)
    status: str = Field(default=work_status.NEW)
    completed: bool = Field(default=False)
    created_at: datetime = Field(
        sa_column=Column(DateTime(), server_default=func.now())
    )
    task: Optional[DbTask] = Relationship(back_populates="work")
    tool: Optional[DbTool] = Relationship(back_populates="work")
    reports: List["DbReport"] = Relationship(back_populates="work")


class DbReport(SQLModel, table=True):
    __tablename__ = "work_reports"
    id: int | None = Field(default=None, primary_key=True)
    work_id: int | None = Field(foreign_key="work.work_id")
    status: str
    details: Dict = Field(sa_column=Column(JSON))
    created_at: datetime = Field(
        sa_column=Column(DateTime(), server_default=func.now())
    )
    work: Optional[DbWork] = Relationship(back_populates="reports")


class DbArchive(SQLModel, table=True):
    __tablename__ = "work_archive"
    work_id: int = Field(primary_key=True)
    status: str
    tool_id: str
    task_id: str
    task_needs: Dict = Field(sa_column=Column(JSON))
    tool_skills: Dict = Field(sa_column=Column(JSON))
    reports: Dict = Field(sa_column=Column(JSON))
    created_at: datetime
    archived_at: datetime = Field(
        sa_column=Column(DateTime(), server_default=func.now())
    )

    def from_work(self, work: DbWork):
        self.work_id = work.work_id
        self.status = work.status
        self.tool_id = work.tool.tool_id
        self.task_id = work.task.task_id
        self.task_needs = work.task.task_needs
        self.tool_skills = work.tool.tool_skills
        self.reports = {"reports": self._make_reports_list(work.reports)}
        self.created_at = work.created_at
        return self

    def _make_reports_list(self, reports: List[DbReport]) -> list[dict]:
        return [
            {
                "status": rpt.status,
                "details": rpt.details,
                "created_at": str(rpt.created_at),
            }
            for rpt in reports
        ]
