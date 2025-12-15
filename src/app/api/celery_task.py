import time
from app.core.celery import celery


@celery.task(name="tasks.increment", bind=True)
def increment(self, value: int) -> int:
    self.update_state(state="STARTED")
    time.sleep(value)
    new_value = value + 1
    return new_value


# following is an example of calling async code from sync celery tasks
# async def get_hero(hero_id: UUID) -> Hero:
#     async with SessionLocal() as session:
#         await asyncio.sleep(5)  # Add a delay of 5 seconds
#         hero = await crud.hero.get(id=hero_id, db_session=session)
#         return hero
#
#
# @celery.task(name="tasks.print_hero")
# def print_hero(hero_id: UUID) -> None:
#     hero = asyncio.get_event_loop().run_until_complete(get_hero(hero_id=hero_id))
#     return hero.id
