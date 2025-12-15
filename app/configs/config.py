from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    GOOGLE_API_KEY: str = Field(default=os.getenv("GOOGLE_API_KEY", ""))
    DATA_PATH: str = Field(default=os.getenv("DATA_PATH", "./app/data"))
    


settings = Settings()
# print(settings.GOOGLE_API_KEY)
