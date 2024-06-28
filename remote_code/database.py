from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

url=""
engine=create_engine(url)
local_session=sessionmaker(bind=engine,autoflush=False,autocommit=False)
