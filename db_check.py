import random
from sqlmodel import Session
from api_models import ReportCreate, TaskCreate, ToolCreate, WorkCreate, WorkInfo
from db_models import DbTask, DbTool, DbWork, DbReport
import db_base as db
from db_base import (
    DB_ITEM_NOT_FOUND,
    DB_ITEM_ALREADY_EXISTS,
    DB_ITEM_REFERENCED,
    DB_WRONG_STATUS,
)
from db_models import work_status
from db_access import ToolAccess, TaskAccess, WorkAccess, ArchiveAccess


class Sim:
    @staticmethod
    def sim_tool_id():
        letter1 = chr(random.randint(65, 90))
        letter2 = chr(random.randint(65, 90))
        n1 = random.randint(10, 99)
        n2 = random.randint(1000, 9999)
        return f"Tool-{letter1}{letter2}-{n2}"

    @staticmethod
    def sim_task_id():
        letter = chr(random.randint(65, 90))
        n1 = random.randint(10, 99)
        n2 = random.randint(1000, 9999)
        return f"Task-{n1}-{letter}-{n2}"

    @staticmethod
    def tool(tag: int = 1):
        return ToolCreate(
            tool_id=Sim.sim_tool_id(),
            tool_skills={"skill1": f"value-{tag}", "skill2": f"value-{tag}"},
        )

    @staticmethod
    def task(tag: int = 1):
        return TaskCreate(
            task_id=Sim.sim_task_id(),
            task_needs={"need1": f"value-{tag}", "need2": f"value-{tag}"},
        )


def handle_db_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DB_ITEM_NOT_FOUND as e:
            print(str(e))
        except DB_ITEM_ALREADY_EXISTS as e:
            print(str(e))
        except DB_ITEM_REFERENCED as e:
            print(str(e))
        except DB_WRONG_STATUS as e:
            print(str(e))

    return wrapper


class ToolOps:

    @handle_db_exceptions
    @staticmethod
    def add_sim_tools_to_db(n: int):
        with Session(db.engine) as session:
            for i in range(n):
                tool_create = Sim.tool(i)
                result = ToolAccess.create_tool(tool_create, session)
                print(result)

    @handle_db_exceptions
    @staticmethod
    def get_tool(tool_id: str) -> DbTool:
        with Session(db.engine) as session:
            tool = ToolAccess.get_tool(tool_id, session)
            print(f"Tool: {tool.tool_id}")
            return tool

    @handle_db_exceptions
    @staticmethod
    def get_all_tools() -> list[DbTool]:
        with Session(db.engine) as session:
            result = ToolAccess.get_all_tools(session)
            for tool in result:
                print(f"Tool: {tool.tool_id}")
            return result

    @handle_db_exceptions
    @staticmethod
    def get_work_for_tool(tool_id: str) -> DbWork:
        with Session(db.engine) as session:
            work = ToolAccess.get_work_for_tool(tool_id, session)
            print(
                f"Work: {work.work_id} - {work.status} - {work.tool.tool_id} - {work.task.task_id}"
            )
            return work

    @handle_db_exceptions
    @staticmethod
    def delete_all_tools():
        with Session(db.engine) as session:
            ToolAccess.delete_all_tools(session)

    @handle_db_exceptions
    @staticmethod
    def tools_ready():
        with Session(db.engine) as session:
            items = ToolAccess.get_all_tools(session)
            tools = [item.tool_id for item in items if item.ready_since is None]
            if not tools:
                print("No tools to mark as ready")
                return
            for tool_id in tools:
                ToolAccess.tool_ready(tool_id, session)
                print(f"Tool '{tool_id}' marked as ready")


class TaskOps:
    @handle_db_exceptions
    @staticmethod
    def add_sim_tasks_to_db(n: int):
        with Session(db.engine) as session:
            for i in range(n):
                task_create = Sim.task(i)
                result = TaskAccess.create_task(task_create, session)
                print(result)

    @handle_db_exceptions
    @staticmethod
    def delete_all_tasks():
        with Session(db.engine) as session:
            TaskAccess.delete_all_tasks(session)


class ReportOps:

    @handle_db_exceptions
    @staticmethod
    def create_work_reports():
        with Session(db.engine) as session:
            work_list = WorkOps._get_work_list(session, completed=False)
            if not work_list:
                return
            for item in work_list:
                work_id = item.work_id
                rpt1 = ReportCreate(
                    work_id=work_id,
                    status=work_status.PROCESSING,
                    details={"details": "Processing report"},
                )
                rpt2 = ReportCreate(
                    work_id=work_id,
                    status=work_status.SUCCEEDED,
                    details={"details": "Success report"},
                )
                WorkAccess.create_work_report(work_id, rpt1, session)
                WorkAccess.work_succeeded(work_id, rpt2, session)
                print(f"Reports created for work '{work_id}'")

    @handle_db_exceptions
    @staticmethod
    def delete_all_reports():
        with Session(db.engine) as session:
            WorkAccess.delete_all_reports(session)


class WorkOps:

    @handle_db_exceptions
    @staticmethod
    def create_work(n: int = 1):
        with Session(db.engine) as session:
            tools = ToolAccess.get_available_tools(session)
            tasks = TaskAccess.get_available_tasks(session)
            if not tools or not tasks:
                print("No viable work candidates found")
                return
            pairs_list = list(zip(tools, tasks))
            for tool, task in pairs_list[:n]:
                work_create = WorkCreate(tool_id=tool.tool_id, task_id=task.task_id)
                result = WorkAccess.create_work(work_create, session)
                print(result)

    @handle_db_exceptions
    @staticmethod
    def _get_work_list(session, completed: bool = True) -> list[DbWork]:
        if completed:
            work_list = WorkAccess.get_all_completed_work(session)
        else:
            work_list = WorkAccess.get_all_work(session)
        if not work_list:
            print("No work found")
            return []
        return work_list

    @handle_db_exceptions
    @staticmethod
    def get_all_work() -> list[DbWork]:
        with Session(db.engine) as session:
            result = WorkAccess.get_all_work(session)
            for work in result:
                print(
                    f"Work: {work.work_id} - {work.status} - {work.tool.tool_id} - {work.task.task_id}"
                )
            return result

    @handle_db_exceptions
    @staticmethod
    def get_work(work_id: int) -> DbWork:
        with Session(db.engine) as session:
            work = WorkAccess.get_work(work_id, session)
            print(
                f"Work: {work.work_id} - {work.status} - {work.tool.tool_id} - {work.task.task_id}"
            )
            return work

    @handle_db_exceptions
    @staticmethod
    def get_all_completed_work() -> list[DbWork]:
        with Session(db.engine) as session:
            result = WorkAccess.get_all_completed_work(session)
            for work in result:
                print(
                    f"Work: {work.work_id} - {work.status} - {work.tool.tool_id} - {work.task.task_id}"
                )
            return result

    @handle_db_exceptions
    @staticmethod
    def get_all_successful_work() -> list[DbWork]:
        with Session(db.engine) as session:
            result = WorkAccess.get_all_successful_work(session)
            for work in result:
                print(
                    f"Work: {work.work_id} - {work.status} - {work.tool.tool_id} - {work.task.task_id}"
                )
            return result

    @handle_db_exceptions
    @staticmethod
    def get_all_failed_work() -> list[DbWork]:
        with Session(db.engine) as session:
            result = WorkAccess.get_all_failed_work(session)
            for work in result:
                print(
                    f"Work: {work.work_id} - {work.status} - {work.tool.tool_id} - {work.task.task_id}"
                )
            return result

    @handle_db_exceptions
    @staticmethod
    def delete_work(n: int) -> None:
        with Session(db.engine) as session:
            work_list = WorkOps._get_work_list(session)
            if not work_list:
                return
            items = work_list[:n]
            for work in items:
                result = WorkAccess.delete_work(work.work_id, session)
                print(result)

    @handle_db_exceptions
    @staticmethod
    def delete_all_work():
        with Session(db.engine) as session:
            WorkAccess.delete_all_work(session)


class ArchiveOps:

    @handle_db_exceptions
    @staticmethod
    def delete_all_archive_items():
        with Session(db.engine) as session:
            ArchiveAccess.delete_all_archived_work(session)


def delete_all():
    ToolOps.delete_all_tools()
    TaskOps.delete_all_tasks()
    ReportOps.delete_all_reports()
    WorkOps.delete_all_work()
    ArchiveOps.delete_all_archive_items()


def main():
    # delete_all()
    # ToolOps.add_sim_tools_to_db(7)
    # TaskOps.add_sim_tasks_to_db(11)
    # ToolOps.tools_ready()
    # WorkOps.create_work(3)
    # ReportOps.create_work_reports()
    # WorkOps.delete_work(1)
    # tools = ToolOps.get_all_tools()
    # work = WorkOps.get_all_work()
    # candidates = WorkOps.get_candidates()
    # work_list = WorkOps.get_all_completed_work()
    # successful_work = WorkOps.get_all_successful_work()
    # work = WorkOps.get_work(22)
    # work_info = WorkInfo().from_work(work)
    print("Done")


if __name__ == "__main__":
    main()
