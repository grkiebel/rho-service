from typing import List
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlmodel import Session
from api_base import handle_db_exceptions as db_ex
from db_base import get_db
from db_access import (
    ToolAccess as ToolAc,
    TaskAccess as TaskAc,
    WorkAccess as WorkAc,
    ArchiveAccess as ArchiveAc,
)
from db_models import DbTool, DbTask
from api_models import (
    ArchiveInfo,
    BasicTask,
    BasicTool,
    BriefArchive,
    BriefReport,
    BriefTask,
    BriefTool,
    BriefWork,
    Outcome,
    ReportCreate,
    TaskCreate,
    ToolCreate,
    WorkCreate,
    WorkInfo,
)


tool_router = APIRouter(prefix="/tool")
task_router = APIRouter(prefix="/task")
work_router = APIRouter(prefix="/work")
archive_router = APIRouter(prefix="/archive")
report_router = APIRouter(prefix="/report")


# ============================================================
""" summary descriptions for each endpoint """
doc = {
    "create_report": "Add a report to a work item",
    "create_task": "Create a new task",
    "create_tool": "Create a new tool",
    "create_work": "Create a new work item",
    "delete_all_tools": "Delete all tools",
    "delete_all_tasks": "Delete all tasks",
    "delete_all_reports": "Delete all reports",
    "delete_all_work": "Delete all work items",
    "delete_all_archived_work": "Delete all archived work items",
    "delete_archive": "Delete a specific archived work item",
    "delete_task": "Delete the specified task",
    "delete_tool": "Delete the specified tool",
    "delete_work": "Copy work item to archive and delete it (delete tool and delete task if work succeeded).",
    "get_all_work": "Get all work",
    "get_archive": "Get a specific archived work item",
    "get_archives": "Get all archived work items",
    "available_tools": "Get all available tools",
    "available_tasks": "Get all available tasks",
    "get_completed_work": "Get all completed work (successful or failed)",
    "get_failed_work": "Get all failed work",
    "get_successful_work": "Get all successful work",
    "get_task": "Get a specific task",
    "get_tasks": "Get all tasks",
    "get_tool": "Get a specific tool",
    "get_tools": "Get all tools",
    "get_work_for_tool": "Get work assigned to the specified tool",
    "get_work": "Get a specific work item",
    "tool_ready": "Mark tool as ready for work",
    "work_failed": "Mark work as completed and failed",
    "work_succeeded": "Mark work as completed and successful",
}

# ============================================================


@tool_router.post("/", response_model=Outcome, summary=doc["create_tool"])
async def create_tool(
    req: Request, new_tool: ToolCreate, db: Session = Depends(get_db)
):
    return db_ex(ToolAc.create_tool)(new_tool, db)


@task_router.post("/", response_model=Outcome, summary=doc["create_task"])
async def create_task(
    req: Request, task_create: TaskCreate, db: Session = Depends(get_db)
):
    return db_ex(TaskAc.create_task)(task_create, db)


@work_router.post("/", response_model=Outcome, summary=doc["create_work"])
async def create_work(
    req: Request, work_create: WorkCreate, db: Session = Depends(get_db)
):
    return db_ex(WorkAc.create_work)(work_create, db)


@report_router.post("/{work_id}", response_model=Outcome, summary=doc["create_report"])
async def create_work_report(
    req: Request,
    work_id: int,
    report_create: ReportCreate,
    db: Session = Depends(get_db),
):
    return db_ex(WorkAc.create_work_report)(work_id, report_create, db)


# ============================================================


@tool_router.put("/{tool_id}", response_model=Outcome, summary=doc["tool_ready"])
async def tool_ready(req: Request, tool_id: str, db: Session = Depends(get_db)):
    return db_ex(ToolAc.tool_ready)(tool_id, db)


@work_router.put(
    "/succeeded/{work_id}", response_model=Outcome, summary=doc["work_succeeded"]
)
async def work_succeeded(
    req: Request,
    work_id: int,
    work_create: ReportCreate,
    db: Session = Depends(get_db),
):
    return db_ex(WorkAc.work_succeeded)(work_id, work_create, db)


@work_router.put(
    "/failed/{work_id}", response_model=Outcome, summary=doc["work_failed"]
)
async def work_failed(
    req: Request,
    work_id: int,
    work_create: ReportCreate,
    db: Session = Depends(get_db),
):
    return db_ex(WorkAc.work_failed)(work_id, work_create, db)


# ============================================================


@tool_router.delete("/all", response_model=Outcome, summary=doc["delete_all_tools"])
async def delete_all_tools(db: Session = Depends(get_db)):
    return db_ex(ToolAc.delete_all_tools)(db)


@task_router.delete("/all", response_model=Outcome, summary=doc["delete_all_tasks"])
async def delete_all_tasks(db: Session = Depends(get_db)):
    return db_ex(TaskAc.delete_all_tasks)(db)


@archive_router.delete(
    "/all", response_model=Outcome, summary=doc["delete_all_archived_work"]
)
async def delete_all_archived_work(db: Session = Depends(get_db)):
    return db_ex(ArchiveAc.delete_all_archived_work)(db)


# delete_all_reports - db_access.py
@report_router.delete("/all", response_model=Outcome, summary=doc["delete_all_reports"])
async def delete_all_reports(db: Session = Depends(get_db)):
    return db_ex(WorkAc.delete_all_reports)(db)


# delete_all_work - db_access.py
@work_router.delete("/all", response_model=Outcome, summary=doc["delete_all_work"])
async def delete_all_work(db: Session = Depends(get_db)):
    return db_ex(WorkAc.delete_all_work)(db)


@tool_router.delete("/{tool_id}", response_model=Outcome, summary=doc["delete_tool"])
async def delete_tool(req: Request, tool_id: str, db: Session = Depends(get_db)):
    return db_ex(ToolAc.delete_tool)(tool_id, db)


@task_router.delete("/{task_id}", response_model=Outcome, summary=doc["delete_task"])
async def delete_task(req: Request, task_id: str, db: Session = Depends(get_db)):
    return db_ex(TaskAc.delete_task)(task_id, db)


@work_router.delete("/{work_id}", response_model=Outcome, summary=doc["delete_work"])
async def delete_work(req: Request, work_id: int, db: Session = Depends(get_db)):
    return db_ex(WorkAc.delete_work)(work_id, db)


@archive_router.delete(
    "/{work_id}", response_model=Outcome, summary=doc["delete_archive"]
)
async def delete_archived_work(
    req: Request, work_id: int, db: Session = Depends(get_db)
):
    return db_ex(ArchiveAc.delete_archived_work)(work_id, db)


# ============================================================


@tool_router.get("/", response_model=List[BriefTool], summary=doc["get_tools"])
async def get_all_tools(req: Request, db: Session = Depends(get_db)):
    tools_list = db_ex(ToolAc.get_all_tools)(db)
    return [BriefTool().from_tool(tool) for tool in tools_list]


@tool_router.get(
    "/work/{tool_id}", response_model=WorkInfo, summary=doc["get_work_for_tool"]
)
async def get_work_for_tool(req: Request, tool_id: str, db: Session = Depends(get_db)):
    work = db_ex(ToolAc.get_work_for_tool)(tool_id, db)
    if not work:
        return WorkInfo()
    return WorkInfo().from_work(work)


@tool_router.get(
    "/available", response_model=List[BasicTool], summary=doc["available_tools"]
)
async def get_available_tools(req: Request, db: Session = Depends(get_db)):
    items = db_ex(ToolAc.get_available_tools)(db)
    if not items:
        return []
    return [BasicTool().from_tool(tool) for tool in items]


@tool_router.get("/{tool_id}", response_model=BriefTool, summary=doc["get_tool"])
async def get_tool(req: Request, tool_id: str, db: Session = Depends(get_db)):
    tool: DbTool = db_ex(ToolAc.get_tool)(tool_id, db)
    return BriefTool().from_tool(tool)


@task_router.get(
    "/available", response_model=List[BasicTask], summary=doc["available_tasks"]
)
async def get_available_tasks(req: Request, db: Session = Depends(get_db)):
    items = db_ex(TaskAc.get_available_tasks)(db)
    if not items:
        return []
    return [BasicTask().from_task(task) for task in items]


@task_router.get("/", response_model=list[BriefTask], summary=doc["get_tasks"])
async def get_all_tasks(req: Request, db: Session = Depends(get_db)):
    task_list = db_ex(TaskAc.get_all_tasks)(db)
    return [BriefTask().from_task(task) for task in task_list]


@task_router.get("/{task_id}", response_model=BriefTask, summary=doc["get_task"])
async def get_task(req: Request, task_id: str, db: Session = Depends(get_db)):
    task: DbTask = db_ex(TaskAc.get_task)(task_id, db)
    return BriefTask().from_task(task)


@work_router.get("/", response_model=List[BriefWork], summary=doc["get_all_work"])
async def get_all_work(req: Request, db: Session = Depends(get_db)):
    work_list = db_ex(WorkAc.get_all_work)(db)
    return [BriefWork().from_work(work) for work in work_list]


@work_router.get(
    "/completed", response_model=List[BriefWork], summary=doc["get_completed_work"]
)
async def get_all_completed_work(req: Request, db: Session = Depends(get_db)):
    work_list = db_ex(WorkAc.get_all_completed_work)(db)
    return [BriefWork().from_work(work) for work in work_list]


@work_router.get(
    "/succeeded", response_model=List[BriefWork], summary=doc["get_successful_work"]
)
async def get_all_successful_work(req: Request, db: Session = Depends(get_db)):
    work_list = db_ex(WorkAc.get_all_successful_work)(db)
    return [BriefWork().from_work(work) for work in work_list]


@work_router.get(
    "/failed", response_model=List[BriefWork], summary=doc["get_failed_work"]
)
async def get_all_failed_work(req: Request, db: Session = Depends(get_db)):
    work_list = db_ex(WorkAc.get_all_failed_work)(db)
    return [BriefWork().from_work(work) for work in work_list]


@work_router.get("/{work_id}", response_model=WorkInfo, summary=doc["get_work"])
async def get_work(req: Request, work_id: int, db: Session = Depends(get_db)):
    work = db_ex(WorkAc.get_work)(work_id, db)
    return WorkInfo().from_work(work)


@report_router.get("/{work_id}", response_model=List[BriefReport])
async def get_reports(req: Request, work_id: int, db: Session = Depends(get_db)):
    reports = db_ex(WorkAc.get_work_reports)(work_id, db)
    return [BriefReport().from_report(report) for report in reports]


@archive_router.get(
    "/{work_id}", response_model=ArchiveInfo, summary=doc["get_archive"]
)
async def get_archived_work(req: Request, work_id: int, db: Session = Depends(get_db)):
    return db_ex(ArchiveAc.get_archived_work)(work_id, db)


@archive_router.get("/", response_model=List[BriefArchive], summary=doc["get_archives"])
async def get_all_archived_work(req: Request, db: Session = Depends(get_db)):
    items = db_ex(ArchiveAc.get_all_archived_work)(db)
    return [BriefArchive().from_archive(item) for item in items]
