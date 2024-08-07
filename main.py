from fastapi import FastAPI
from api_endpts import (
    tool_router,
    task_router,
    work_router,
    archive_router,
    report_router,
    general_router,
)


app = FastAPI()


app.include_router(general_router)
app.include_router(tool_router)
app.include_router(task_router)
app.include_router(work_router)
app.include_router(archive_router)
app.include_router(report_router)
