from fastapi import FastAPI
from src.auth import auth_routes
from src.admin import admin_routes
from src.bookings import booking_routes
from src.coaches import coach_routes
from src.journals import journal_routes
from src.psych_tests import psych_routes
from src.users import user_routes
from src.database import engine
from src.auth import auth_models
from src.logging import configure_logging, LogLevels
import logging

configure_logging(LogLevels.debug)

logger = logging.getLogger(__name__)


# logger.debug("Debug info for devs")
# logger.info("Operation successful")
# logger.warning("This is a warning")
# logger.error("Something went wrong")


app = FastAPI(title="MindCare")



auth_models.Base.metadata.create_all(bind=engine)



# Include Routers
app.include_router(auth_routes.router)
app.include_router(admin_routes.router)
app.include_router(booking_routes.router)
app.include_router(coach_routes.router)
app.include_router(journal_routes.router)
app.include_router(psych_routes.router)
app.include_router(user_routes.router)





@app.get('/')
async def test():
   return {"url": "https://mindcare-416e.onrender.com/docs"}