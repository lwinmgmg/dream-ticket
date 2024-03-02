from strawberry.extensions import SchemaExtension
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker


class DbSessionExtension(SchemaExtension):
    async def on_operation(self):  # pylint: disable=W0236
        db: AsyncEngine = self.execution_context.context["db"]
        ro_db: AsyncEngine = self.execution_context.context["ro_db"]
        async with async_sessionmaker(ro_db)() as ro_session:
            self.execution_context.context["ro_db_session"] = ro_session
            async with async_sessionmaker(db)() as session:
                self.execution_context.context["db_session"] = session
                yield
                if self.execution_context.errors:
                    await session.rollback()
                else:
                    await session.commit()
