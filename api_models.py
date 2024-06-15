from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel
from sqlalchemy import JSON, Column
from sqlmodel import Field
from db_models import DbArchive, DbTool, DbTask, DbWork, DbReport


# ============================================================


class ToolCreate(BaseModel):
    tool_id: str
    tool_skills: Dict


class ToolUpdate(BaseModel):
    tool_skills: Dict


class BriefTool(BaseModel):
    work_id: int | None = None
    enabled: bool | None = None
    ready_since: datetime | None = None
    task_id: str | None = None
    tool_id: str | None = None
    status: str | None = None
    complete: bool | None = None

    def from_tool(self, tool: DbTool):
        self.tool_id = tool.tool_id
        self.work_id = tool.work_id if tool.work else None
        self.task_id = tool.work.task.task_id if tool.work else None
        self.complete = tool.work.completed if tool.work else None
        self.status = tool.work.status if tool.work else None
        self.enabled = tool.enabled
        self.ready_since = tool.ready_since
        return self


class BasicTool(BaseModel):
    tool_id: str | None = None
    tool_skills: Dict | None = None
    created_at: str | None = None

    def from_tool(self, tool: DbTool):
        self.tool_id = tool.tool_id
        self.tool_skills = tool.tool_skills
        self.created_at = tool.created_at.strftime("%Y-%m-%d %H:%M:%S")
        return self


# ============================================================
class TaskCreate(BaseModel):
    task_id: str = Field(default=None, primary_key=True)
    task_needs: Dict = Field(sa_column=Column(JSON))


class BriefTask(BaseModel):
    task_id: str | None = None
    work_id: int | None = None
    tool_id: str | None = None
    status: str | None = None
    complete: bool | None = None

    def from_task(self, task: DbTask):
        self.task_id = task.task_id
        self.work_id = task.work_id
        self.tool_id = task.work.tool.tool_id if task.work else None
        self.complete = task.work.completed if task.work else None
        self.status = task.work.status if task.work else None
        return self


class BasicTask(BaseModel):
    task_id: str | None = None
    task_needs: Dict | None = None
    created_at: str | None = None

    def from_task(self, task: DbTask):
        self.task_id = task.task_id
        self.task_needs = task.task_needs
        self.created_at = task.created_at.strftime("%Y-%m-%d %H:%M:%S")
        return self


# ============================================================


class WorkCreate(BaseModel):
    tool_id: str
    task_id: str


class BriefWork(BaseModel):
    work_id: int | None = None
    status: str | None = None
    completed: bool | None = None
    tool_id: str | None = None
    task_id: str | None = None

    def from_work(self, work: DbWork):
        self.work_id = work.work_id
        self.status = work.status
        self.completed = work.completed
        self.tool_id = work.tool.tool_id
        self.task_id = work.task.task_id
        return self


class WorkInfo(BriefWork):
    tool_skills: Dict | None = None
    task_needs: Dict | None = None

    def from_work(self, work: DbWork):
        super().from_work(work)
        self.tool_skills = work.tool.tool_skills
        self.task_needs = work.task.task_needs
        return self


# ============================================================


class ReportCreate(BaseModel):
    status: str
    details: Dict


class BriefReport(BaseModel):
    status: str | None = None
    details: Dict | None = None
    created_at: str | None = None

    def from_report(self, report: DbReport):
        self.status = report.status
        self.details = report.details
        self.created_at = report.created_at.strftime("%Y-%m-%d %H:%M:%S")
        return self


# ============================================================


class BriefArchive(BaseModel):
    work_id: int | None = None
    status: str | None = None
    tool_id: str | None = None
    task_id: str | None = None
    created_at: str | None = None
    archived_at: str | None = None

    def from_archive(self, archive: DbArchive):
        self.work_id = archive.work_id
        self.status = archive.status
        self.tool_id = archive.tool_id
        self.task_id = archive.task_id
        self.created_at = archive.created_at.strftime("%Y-%m-%d %H:%M:%S")
        self.archived_at = archive.archived_at.strftime("%Y-%m-%d %H:%M:%S")
        return self


class ArchiveInfo(BriefArchive):
    task_needs: Dict | None = None
    tool_skills: Dict | None = None
    reports: List[Dict] | None = None

    def from_archive(self, archive: DbArchive):
        super().from_archive(archive)
        self.task_needs = archive.task_needs
        self.tool_skills = archive.tool_skills
        self.reports = archive.reports
        return self


# ============================================================
class Outcome(BaseModel):
    message: str
    success: bool = True
