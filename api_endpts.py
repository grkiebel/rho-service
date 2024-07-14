from typing import List
from fastapi import APIRouter, Depends, Request
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
general_router = APIRouter(prefix="/general")


# ============================================================
""" summary descriptions for each endpoint """
doc = {
    "create_report": "Create a new report for a specific work item",
    "create_task": "Create a new task",
    "create_tool": "Create a new tool",
    "create_work": "Create a new work item",
    #
    "clear_tools": "Clear (delete all) tools",
    "clear_tasks": "Clear (delete all) tasks",
    "clear_reports": "Clear (delete all) reports",
    "clear_work": "Clear (delete all) work items",
    "clear_archive": "Clear (delete all) archived work items",
    #
    "delete_task": "Delete the specified task",
    "delete_tool": "Delete the specified tool",
    "delete_work": "Delete the spcified work item and move it to archive (delete task if work succeeded)",
    "delete_archive": "Delete a specific archived work item",
    #
    "mark_tool_disabled": "Update tool as disabled",
    "mark_tool_enabled": "Update tool as enabled",
    "tool_ready": "Update tool as ready for work",
    #
    "get_tools": "List of all tools",
    "get_tasks": "List of all tasks",
    "get_all_work": "List of all work",
    "get_archives": "List of all archived work items",
    "available_tools": "List of all available tools",
    "available_tasks": "List of all available tasks",
    "get_completed_work": "List of all completed work",
    "get_failed_work": "List of all failed work",
    "get_successful_work": "List of all successful work",
    "get_reports": "List of all reports for a specific work item",
    #
    "get_tool": "Details for a specific tool",
    "get_task": "Details for a specific task",
    "get_work": "Details for  a specific work item",
    "get_archive": "Details for a specific archived work item",
    #
    "get_work_for_tool": "Details for assigned work for the specified tool",
    #
    "mark_work_failed": "Update work as failed",
    "mark_work_succeeded": "Update work as successful",
}

# ============================================================


@general_router.get("/status", response_model=dict, summary="API status")
def server_status():
    return {"message": "API is running"}


# ============================================================


@tool_router.post("/create/", response_model=Outcome, summary=doc["create_tool"])
async def create_tool(
    req: Request, new_tool: ToolCreate, db: Session = Depends(get_db)
):
    return db_ex(ToolAc.create_tool)(new_tool, db)


@task_router.post("/create/", response_model=Outcome, summary=doc["create_task"])
async def create_task(
    req: Request, task_create: TaskCreate, db: Session = Depends(get_db)
):
    return db_ex(TaskAc.create_task)(task_create, db)


@work_router.post("/create/", response_model=Outcome, summary=doc["create_work"])
async def create_work(
    req: Request, work_create: WorkCreate, db: Session = Depends(get_db)
):
    return db_ex(WorkAc.create_work)(work_create, db)


@report_router.post(
    "/create/{work_id}", response_model=Outcome, summary=doc["create_report"]
)
async def create_work_report(
    req: Request,
    work_id: int,
    report_create: ReportCreate,
    db: Session = Depends(get_db),
):
    return db_ex(WorkAc.create_work_report)(work_id, report_create, db)


# ============================================================


@tool_router.put(
    "/update/ready/{tool_id}", response_model=Outcome, summary=doc["tool_ready"]
)
async def tool_ready(req: Request, tool_id: str, db: Session = Depends(get_db)):
    return db_ex(ToolAc.tool_ready)(tool_id, db)


@tool_router.put(
    "/update/enable/{tool_id}", response_model=Outcome, summary=doc["mark_tool_enabled"]
)
async def mark_tool_enabled(req: Request, tool_id: str, db: Session = Depends(get_db)):
    return db_ex(ToolAc.tool_enable)(tool_id, True, db)


@tool_router.put(
    "/update/disable/{tool_id}",
    response_model=Outcome,
    summary=doc["mark_tool_disabled"],
)
async def mark_tool_disabled(req: Request, tool_id: str, db: Session = Depends(get_db)):
    return db_ex(ToolAc.tool_enable)(tool_id, False, db)


@work_router.put(
    "/update/successful/{work_id}",
    response_model=Outcome,
    summary=doc["mark_work_succeeded"],
)
async def mark_work_succeeded(
    req: Request,
    work_id: int,
    db: Session = Depends(get_db),
):
    return db_ex(WorkAc.work_succeeded)(work_id, db)


@work_router.put(
    "/update/failed/{work_id}", response_model=Outcome, summary=doc["mark_work_failed"]
)
async def mark_work_failed(
    req: Request,
    work_id: int,
    db: Session = Depends(get_db),
):
    return db_ex(WorkAc.work_failed)(work_id, db)


# ============================================================


@tool_router.delete("/clear", response_model=Outcome, summary=doc["clear_tools"])
async def clear_tools(db: Session = Depends(get_db)):
    return db_ex(ToolAc.delete_all_tools)(db)


@task_router.delete("/clear", response_model=Outcome, summary=doc["clear_tasks"])
async def clear_tasks(db: Session = Depends(get_db)):
    return db_ex(TaskAc.delete_all_tasks)(db)


@archive_router.delete("/clear", response_model=Outcome, summary=doc["clear_archive"])
async def clear_archive(db: Session = Depends(get_db)):
    return db_ex(ArchiveAc.delete_all_archived_work)(db)


@report_router.delete("/clear", response_model=Outcome, summary=doc["clear_reports"])
async def clear_reports(db: Session = Depends(get_db)):
    return db_ex(WorkAc.delete_all_reports)(db)


@work_router.delete("/clear", response_model=Outcome, summary=doc["clear_work"])
async def clear_work(db: Session = Depends(get_db)):
    return db_ex(WorkAc.delete_all_work)(db)


@tool_router.delete(
    "/delete/{tool_id}", response_model=Outcome, summary=doc["delete_tool"]
)
async def delete_tool(req: Request, tool_id: str, db: Session = Depends(get_db)):
    return db_ex(ToolAc.delete_tool)(tool_id, db)


@task_router.delete(
    "/delete/{task_id}", response_model=Outcome, summary=doc["delete_task"]
)
async def delete_task(req: Request, task_id: str, db: Session = Depends(get_db)):
    return db_ex(TaskAc.delete_task)(task_id, db)


@work_router.delete(
    "/delete/{work_id}", response_model=Outcome, summary=doc["delete_work"]
)
async def delete_work(req: Request, work_id: int, db: Session = Depends(get_db)):
    return db_ex(WorkAc.delete_work)(work_id, db)


@archive_router.delete(
    "/delete/{work_id}", response_model=Outcome, summary=doc["delete_archive"]
)
async def delete_archived_work(
    req: Request, work_id: int, db: Session = Depends(get_db)
):
    return db_ex(ArchiveAc.delete_archived_work)(work_id, db)


# ============================================================


@tool_router.get("/list/", response_model=List[BriefTool], summary=doc["get_tools"])
async def get_all_tools(req: Request, db: Session = Depends(get_db)):
    tools_list = db_ex(ToolAc.get_all_tools)(db)
    return [BriefTool().from_tool(tool) for tool in tools_list]


@tool_router.get(
    "/details/work/assignment/{tool_id}",
    response_model=WorkInfo,
    summary=doc["get_work_for_tool"],
)
async def get_work_for_tool(req: Request, tool_id: str, db: Session = Depends(get_db)):
    work = db_ex(ToolAc.get_work_for_tool)(tool_id, db)
    if not work:
        return WorkInfo()
    return WorkInfo().from_work(work)


@tool_router.get(
    "/list/available", response_model=List[BasicTool], summary=doc["available_tools"]
)
async def get_available_tools(req: Request, db: Session = Depends(get_db)):
    items = db_ex(ToolAc.get_available_tools)(db)
    if not items:
        return []
    return [BasicTool().from_tool(tool) for tool in items]


@tool_router.get(
    "/details/{tool_id}", response_model=BriefTool, summary=doc["get_tool"]
)
async def get_tool(req: Request, tool_id: str, db: Session = Depends(get_db)):
    tool: DbTool = db_ex(ToolAc.get_tool)(tool_id, db)
    return BriefTool().from_tool(tool)


@task_router.get(
    "/list/available", response_model=List[BasicTask], summary=doc["available_tasks"]
)
async def get_available_tasks(req: Request, db: Session = Depends(get_db)):
    items = db_ex(TaskAc.get_available_tasks)(db)
    if not items:
        return []
    return [BasicTask().from_task(task) for task in items]


@task_router.get("/list/", response_model=list[BriefTask], summary=doc["get_tasks"])
async def get_all_tasks(req: Request, db: Session = Depends(get_db)):
    task_list = db_ex(TaskAc.get_all_tasks)(db)
    return [BriefTask().from_task(task) for task in task_list]


@task_router.get(
    "/details/{task_id}", response_model=BriefTask, summary=doc["get_task"]
)
async def get_task(req: Request, task_id: str, db: Session = Depends(get_db)):
    task: DbTask = db_ex(TaskAc.get_task)(task_id, db)
    return BriefTask().from_task(task)


@work_router.get("/list/", response_model=List[BriefWork], summary=doc["get_all_work"])
async def get_all_work(req: Request, db: Session = Depends(get_db)):
    work_list = db_ex(WorkAc.get_all_work)(db)
    return [BriefWork().from_work(work) for work in work_list]


@work_router.get(
    "/list/completed", response_model=List[BriefWork], summary=doc["get_completed_work"]
)
async def get_all_completed_work(req: Request, db: Session = Depends(get_db)):
    work_list = db_ex(WorkAc.get_all_completed_work)(db)
    return [BriefWork().from_work(work) for work in work_list]


@work_router.get(
    "/list/succeeded",
    response_model=List[BriefWork],
    summary=doc["get_successful_work"],
)
async def get_all_successful_work(req: Request, db: Session = Depends(get_db)):
    work_list = db_ex(WorkAc.get_all_successful_work)(db)
    return [BriefWork().from_work(work) for work in work_list]


@work_router.get(
    "/list/failed", response_model=List[BriefWork], summary=doc["get_failed_work"]
)
async def get_all_failed_work(req: Request, db: Session = Depends(get_db)):
    work_list = db_ex(WorkAc.get_all_failed_work)(db)
    return [BriefWork().from_work(work) for work in work_list]


@work_router.get("/details/{work_id}", response_model=WorkInfo, summary=doc["get_work"])
async def get_work(req: Request, work_id: int, db: Session = Depends(get_db)):
    work = db_ex(WorkAc.get_work)(work_id, db)
    return WorkInfo().from_work(work)


@report_router.get(
    "/list/{work_id}", response_model=List[BriefReport], summary=doc["get_reports"]
)
async def get_reports(req: Request, work_id: int, db: Session = Depends(get_db)):
    reports = db_ex(WorkAc.get_work_reports)(work_id, db)
    return [BriefReport().from_report(report) for report in reports]


@archive_router.get(
    "/details/{work_id}", response_model=ArchiveInfo, summary=doc["get_archive"]
)
async def get_archived_work(req: Request, work_id: int, db: Session = Depends(get_db)):
    return db_ex(ArchiveAc.get_archived_work)(work_id, db)


@archive_router.get(
    "/list/", response_model=List[BriefArchive], summary=doc["get_archives"]
)
async def get_all_archived_work(req: Request, db: Session = Depends(get_db)):
    items = db_ex(ArchiveAc.get_all_archived_work)(db)
    return [BriefArchive().from_archive(item) for item in items]
