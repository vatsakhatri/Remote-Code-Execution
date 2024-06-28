from sqlalchemy.orm import declarative_base
from sqlalchemy import Column,INTEGER,String,Enum,ForeignKey
import enum
Base=declarative_base()

class typeof(enum.Enum):
    Easy="Easy"
    Medium="Medium"
    Difficult="Difficult"




class Questions(Base):
    __tablename__='Questions'
    id=Column(INTEGER,primary_key=True,autoincrement=True)
    title=Column(String(100),unique=True)
    description=Column(String(200))
    type=Column(Enum(typeof))
    meta_data=Column(String(200),nullable=False)
    
    
class TestCase(Base):
    __tablename__='TestCase'
    id=Column(INTEGER,primary_key=True,autoincrement=True)
    question_id=Column(INTEGER,ForeignKey('Questions.id'),nullable=True)
    input=Column(String(200),nullable=False)
    expected_output=Column(String(200),nullable=False)
    
    
