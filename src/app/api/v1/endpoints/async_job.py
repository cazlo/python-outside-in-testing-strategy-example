from fastapi import APIRouter
from app.api.celery_task import increment
from celery.result import AsyncResult
from celery.states import REVOKED
from pydantic import BaseModel

router = APIRouter()


class TaskInput(BaseModel):
    delay: int  # how much time the task sleeps for before doing the increment
    countdown: int = 0  # delay before the task can be started


class TaskResponse(BaseModel):
    task_id: str
    status: str
    ready: bool
    result: int | None


@router.post("/increment_task", response_model=TaskResponse, status_code=201)
async def queue_increment_task(input_data: TaskInput):
    task_result = increment.apply_async(
        args=(input_data.delay,), countdown=input_data.countdown
    )
    ready = task_result.ready()
    return TaskResponse(
        task_id=task_result.id,
        status="QUEUED",
        ready=ready,
        result=task_result.result if ready else None,
    )


@router.get("/increment_task/{task_id}", response_model=TaskResponse)
async def get_increment_task_result(task_id: str):
    task_result = AsyncResult(task_id)
    ready = task_result.ready()
    return TaskResponse(
        task_id=task_result.id,
        status=task_result.status,
        ready=ready,
        result=(
            task_result.result if ready and not task_result.status == REVOKED else None
        ),
    )


@router.delete("/increment_task/{task_id}", response_model=TaskResponse)
async def delete_increment_task(task_id: str):
    task_result = AsyncResult(task_id)
    task_result.revoke()  # this will remove it from queue but not stop the job from processing if it has already started
    task_result = AsyncResult(task_id)
    ready = task_result.ready()
    return TaskResponse(
        task_id=task_result.id,
        status=task_result.status,
        ready=task_result.ready(),
        result=(
            task_result.result if ready and not task_result.status == REVOKED else None
        ),
    )


# todo below isn't working as expected blowing up on celery_session.commit()
# this might be a matter of swapping to the newer https://github.com/farahats9/sqlalchemy-celery-beat
# class IntervalScheduleInput(BaseModel):
#     every: int
#     period: Literal[IntervalSchedule.DAYS, IntervalSchedule.HOURS, IntervalSchedule.MINUTES, IntervalSchedule.SECONDS, IntervalSchedule.MICROSECONDS]
#
# class ScheduledTaskIntervalInput(TaskInput):
#     interval: IntervalScheduleInput
#
# class CronTabScheduleInput(BaseModel):
#     minute: str # * or int value
#     hour: str # * or int value
#     day_of_week: str # * or int value
#     day_of_month: str # * or int value
#     month_of_year: str # * or int value
#
# class ScheduledTaskCronInput(TaskInput):
#     cron: CronTabScheduleInput
#
# @router.post("/scheduled_increment_task", response_model=TaskResponse, status_code=201)
# async def schedule_increment_task(input_data: ScheduledTaskIntervalInput | ScheduledTaskCronInput, celery_session=Depends(get_job_db)):
#     task_id = uuid.uuid4().hex
#     if type(input_data) == ScheduledTaskIntervalInput:
#         periodic_task = PeriodicTask(
#             interval=IntervalSchedule(every=input_data.interval.every, period=input_data.interval.period),
#             name=task_id,
#             args=f"[{input_data.delay}, {input_data.countdown}]",
#             task="tasks.increment",
#         )
#         celery_session.add(periodic_task)
#         celery_session.commit()
#     elif type(input_data) == ScheduledTaskCronInput:
#         periodic_task = PeriodicTask(
#             crontab=CrontabSchedule(
#                 hour=input_data.cron.hour,
#                 minute=input_data.cron.minute,
#                 day_of_month=input_data.cron.day_of_month,
#                 month_of_year=input_data.cron.month_of_year,
#                 timezone="UTC"
#             ),
#             name=task_id,
#             args=f"[{input_data.delay}, {input_data.countdown}]",
#             task="tasks.increment",
#             one_off=False,
#         )
#         celery_session.add(periodic_task)
#         celery_session.commit()
#     return TaskResponse(task_id=task_id, status="SCHEDULED", ready=False, result=None)
#
#
# @router.get("/scheduled_increment_task/{task_id}", response_model=TaskResponse)
# async def get_scheduled_increment_task_result(task_id: str):
#     task_result = AsyncResult(task_id)
#     ready = task_result.ready()
#     return TaskResponse(
#         task_id=task_result.id,
#         status=task_result.status,
#         ready=ready,
#         result=task_result.result if ready and not task_result.status == REVOKED else None,
#     )
#
# @router.delete("/scheduled_increment_task/{task_id}", response_model=TaskResponse)
# async def get_increment_task_result(task_id: str):
#     task_result = AsyncResult(task_id)
#     task_result.revoke() # this will remove it from queue but not stop the job from processing if it has already started
#     task_result = AsyncResult(task_id)
#     ready = task_result.ready()
#     return TaskResponse(
#         task_id=task_result.id,
#         status=task_result.status,
#         ready=task_result.ready(),
#         result=task_result.result if ready and not task_result.status == REVOKED else None,
#     )
