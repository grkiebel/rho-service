from datetime import datetime
from sqlmodel import Session, select
import db_base as db
from db_models import (
    DbTool,
    DbTask,
    DbWork,
    DbReport,
    DbArchive,
    work_status,
)
from api_models import (
    Outcome,
    ToolCreate,
    TaskCreate,
    WorkCreate,
    ReportCreate,
)

# ----------------- Tool functions -----------------


class ToolAccess:
    @staticmethod
    def create_tool(tool_create: ToolCreate, session: Session) -> Outcome:
        result = session.exec(
            select(DbTool).where(DbTool.tool_id == tool_create.tool_id)
        )
        exsisting_tool = result.one_or_none()
        if exsisting_tool:
            raise db.DB_ITEM_ALREADY_EXISTS(
                f"Tool '{exsisting_tool.tool_id}' already exists"
            )
        tool = DbTool(**tool_create.model_dump())
        session.add(tool)
        session.commit()
        return Outcome(message=f"Tool {tool.tool_id} created successfully")

    @staticmethod
    def tool_ready(tool_id: str, session: Session) -> Outcome:
        tool = ToolAccess.get_tool(tool_id, session)
        if tool.work and tool.work.status != work_status.NEW:
            return Outcome(
                message=f"Tool '{tool_id}' is assigned to active work item '{tool.work_id}'",
                success=False,
            )
        tool.ready_since = datetime.now()
        session.commit()
        return Outcome(message=f"Tool {tool.tool_id} is set as ready")

    @staticmethod
    def delete_tool(tool_id: str, session: Session) -> Outcome:
        tool = session.exec(
            select(DbTool).where(DbTool.tool_id == tool_id)
        ).one_or_none()
        if not tool:
            raise db.DB_ITEM_NOT_FOUND(f"Tool '{tool_id}' does not exist")
        return Outcome(message=f"Tool {tool.tool_id} deleted successfully")

    @staticmethod
    def delete_all_tools(session: Session) -> Outcome:
        items = session.exec(select(DbTool)).all()
        for item in items:
            session.delete(item)
        session.commit()
        return Outcome(message=f"{len(items)} tools were deleted")

    @staticmethod
    def get_all_tools(session: Session) -> list[DbTool]:
        result = session.exec(select(DbTool))
        return result.all()

    @staticmethod
    def get_tool(tool_id: str, session: Session) -> DbTool:
        result = session.exec(select(DbTool).where(DbTool.tool_id == tool_id))
        tool = result.one_or_none()
        if not tool:
            raise db.DB_ITEM_NOT_FOUND(f"Tool '{tool_id}' does not exist")
        return tool

    @staticmethod
    def get_work_for_tool(tool_id: str, session: Session) -> DbWork:
        tool = ToolAccess.get_tool(tool_id, session)
        if not tool:
            return None
        if not tool.work:
            return None
        return tool.work

    @staticmethod
    def get_available_tools(session: Session) -> list[DbTool]:
        tools_stmt = select(DbTool).where(
            DbTool.work_id == None, DbTool.ready_since != None
        )
        tools = session.exec(tools_stmt).all()
        if not tools:
            return []
        return tools


# ----------------- Task functions -----------------


class TaskAccess:
    @staticmethod
    def create_task(task_create: TaskCreate, session: Session) -> Outcome:
        result = session.exec(
            select(DbTask).where(DbTask.task_id == task_create.task_id)
        )
        exsisting_task = result.one_or_none()
        if exsisting_task:
            raise db.DB_ITEM_ALREADY_EXISTS(
                f"Task '{exsisting_task.task_id}' already exists"
            )
        task = DbTask(**task_create.model_dump())
        session.add(task)
        session.commit()
        return Outcome(message=f"Task {task.task_id} created successfully")

    @staticmethod
    def delete_task(task_id: str, session: Session) -> Outcome:
        task = session.exec(
            select(DbTask).where(DbTask.task_id == task_id)
        ).one_or_none()
        if not task:
            raise db.DB_ITEM_NOT_FOUND(f"Task '{task_id}' does not exist")
        session.delete(task)
        session.commit()
        return Outcome(message=f"Task {task.task_id} deleted successfully")

    @staticmethod
    def delete_all_tasks(session: Session) -> Outcome:
        items = session.exec(select(DbTask)).all()
        for item in items:
            session.delete(item)
        session.commit()
        return Outcome(message=f"{len(items)} tasks were deleted")

    @staticmethod
    def get_all_tasks(session: Session) -> list[DbTask]:
        result = session.exec(select(DbTask))
        return result.all()

    @staticmethod
    def get_task(task_id: str, session: Session) -> DbTask:
        result = session.exec(select(DbTask).where(DbTask.task_id == task_id))
        task = result.one_or_none()
        if not task:
            raise db.DB_ITEM_NOT_FOUND(f"Task '{task_id}' does not exist")
        return task

    @staticmethod
    def get_available_tasks(session: Session) -> list[DbTask]:
        tasks_stmt = select(DbTask).where(DbTask.work_id == None)
        tasks = session.exec(tasks_stmt).all()
        if not tasks:
            return []
        return tasks


# ----------------- Work functions -----------------


class WorkAccess:

    @staticmethod
    def create_work(work_create: WorkCreate, session: Session) -> Outcome:
        tool = session.exec(
            select(DbTool).where(DbTool.tool_id == work_create.tool_id)
        ).one_or_none()
        if not tool:
            raise db.DB_ITEM_NOT_FOUND(f"Tool '{work_create.tool_id}' does not exist")
        task = session.exec(
            select(DbTask).where(DbTask.task_id == work_create.task_id)
        ).one_or_none()
        if not task:
            raise db.DB_ITEM_NOT_FOUND(f"Task '{work_create.task_id}' does not exist")

        work: DbWork = DbWork()
        work.tool = tool
        work.task = task
        session.add(work)
        session.commit()
        return Outcome(
            message=f"Work item {work.work_id} for tool {work_create.tool_id} and task {work_create.task_id} created successfully"
        )

    @staticmethod
    def delete_work(work_id: int, session: Session) -> Outcome:
        return Outcome(message=f"Not implemented yet", success=False)

    @staticmethod
    def get_all_work(session: Session) -> list[DbWork]:
        raw = session.exec(select(DbWork)).all()
        return [DbWork.model_validate(item) for item in raw]

    @staticmethod
    def get_all_completed_work(session: Session) -> list[DbWork]:
        raw = session.exec(select(DbWork).where(DbWork.completed == True)).all()
        return [DbWork.model_validate(item) for item in raw]

    @staticmethod
    def get_all_successful_work(session: Session) -> list[DbWork]:
        raw = session.exec(
            select(DbWork).where(DbWork.status == work_status.SUCCEEDED)
        ).all()
        return [DbWork.model_validate(item) for item in raw]

    @staticmethod
    def get_all_failed_work(session: Session) -> list[DbWork]:
        raw = session.exec(
            select(DbWork).where(DbWork.status == work_status.FAILED)
        ).all()
        return [DbWork.model_validate(item) for item in raw]

    @staticmethod
    def get_work(work_id: int, session: Session) -> DbWork:
        result = session.exec(select(DbWork).where(DbWork.work_id == work_id))
        work = result.one_or_none()
        if not work:
            raise db.DB_ITEM_NOT_FOUND(f"Work '{work_id}' does not exist")
        return work

    @staticmethod
    def work_succeeded(
        work_id: int, report_create: ReportCreate, session: Session
    ) -> Outcome:
        report = DbReport(
            work_id=work_id, status=work_status.SUCCEEDED, details=report_create.details
        )
        outcome = WorkAccess._set_work_completed(work_id, True, report, session)
        return outcome

    @staticmethod
    def work_failed(
        work_id: int, report_create: ReportCreate, session: Session
    ) -> Outcome:
        report = DbReport(
            work_id=work_id, status=work_status.FAILED, details=report_create.details
        )
        outcome = WorkAccess._set_work_completed(work_id, False, report, session)
        return outcome

    @staticmethod
    def _set_work_completed(
        work_id: int, success: bool, report: DbReport, session: Session
    ) -> Outcome:
        work = session.exec(
            select(DbWork).where(DbWork.work_id == work_id)
        ).one_or_none()
        if not work:
            raise db.DB_ITEM_NOT_FOUND(f"Work '{work_id}' does not exist")

        work.status = work_status.SUCCEEDED if success else work_status.FAILED
        work.completed = True

        session.add(report)
        session.commit()
        session.refresh(work)

        work.tool.work_id = None
        work.tool.ready_since = None

        work.task.work_id = None
        if work.status == work_status.SUCCEEDED:
            session.delete(work.task)

        work_archive = DbArchive().from_work(work)
        session.add(work_archive)
        for report in work.reports:
            session.delete(report)

        session.delete(work)
        session.commit()
        return Outcome(
            message=f"Work item {work_id} completed and archived successfully"
        )

    @staticmethod
    def create_work_report(
        work_id: int, report_create: ReportCreate, session: Session
    ) -> Outcome:
        status = report_create.status
        details = report_create.details
        work = session.exec(
            select(DbWork).where(DbWork.work_id == work_id)
        ).one_or_none()
        if not work:
            raise db.DB_ITEM_NOT_FOUND(f"Work '{work_id}' does not exist")
        report = DbReport(work_id=work_id, status=status, details=details)
        work.status = status
        if work.status == work_status.SUCCEEDED or work.status == work_status.FAILED:
            work.completed = True
        session.add(report)
        session.commit()
        return Outcome(
            message=f"Report {report.id} created successfully for work {work_id}"
        )

    @staticmethod
    def get_work_reports(work_id: int, session: Session) -> list[DbReport]:
        result = session.exec(select(DbReport).where(DbReport.work_id == work_id)).all()
        return result

    #
    @staticmethod
    def delete_all_work(session: Session) -> Outcome:
        items = session.exec(select(DbWork)).all()
        if items:
            for item in items:
                session.delete(item)
            session.commit()
            return Outcome(message=f"{len(items)} work items were deleted")
        else:
            return Outcome(message="No work items found", success=False)

    @staticmethod
    def delete_all_reports(session: Session) -> Outcome:
        items = session.exec(select(DbReport)).all()
        if items:
            for item in items:
                session.delete(item)
            session.commit()
            return Outcome(message=f"{len(items)} reports were deleted")
        else:
            return Outcome(message="No reports found", success=False)


# ----------------- Work Archive functions -----------------
class ArchiveAccess:
    @staticmethod
    def get_all_archived_work(session: Session) -> list[DbArchive]:
        return session.exec(select(DbArchive)).all()

    def delete_all_archived_work(session: Session):
        items = session.exec(select(DbArchive)).all()
        if items:
            for item in items:
                session.delete(item)
            session.commit()
            return Outcome(message=f"{len(items)} archived work items were deleted")
        else:
            return Outcome(message="No archived work items found")

    @staticmethod
    def get_archived_work(work_id: int, session: Session) -> DbArchive:
        return session.exec(
            select(DbArchive).where(DbArchive.work_id == work_id)
        ).one_or_none()

    @staticmethod
    def delete_archived_work(work_id: int, session: Session) -> Outcome:
        archive = session.exec(
            select(DbArchive).where(DbArchive.work_id == work_id)
        ).one_or_none()
        if not archive:
            raise db.DB_ITEM_NOT_FOUND(f"Work '{work_id}' does not exist")
        session.delete(archive)
        session.commit()
        return Outcome(message=f"Archived work {work_id} deleted successfully")
