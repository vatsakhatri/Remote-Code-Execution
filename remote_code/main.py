import importlib
import json
import textwrap
from typing import List
from fastapi import FastAPI, Form,HTTPException,Depends, Request
from database import engine
from starlette import status
from sqlalchemy.orm import Session
from models import Questions,TestCase,typeof
from schemas import QuesSchema,type,TestSchema,usercode
import models
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import local_session,engine
app=FastAPI()

def get_db():
    db=local_session()
    try:
        yield db
    finally:
        db.close()


templates = Jinja2Templates(directory="templates")

class QuesService():
    def __init__(self,db:Session):
        self.db=db
        
        
    def show_all_quest(self):
        all_ques=self.db.query(Questions).all()
        return all_ques
        
    def get_ques_by_title(self,title:str):
        ques=self.db.query(Questions).filter(Questions.title==title).all()
        if ques:
            return True
        return False
        
        
    def get_ques_by_id(self,id:int):
        ques=self.db.query(Questions).filter(Questions.id==id).first()
        if not ques:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="no ques with such id")
        return ques
    
    
    def create_new_ques(self,ques:QuesSchema):
        title=ques.title
        desc=ques.description
        type=ques.type
        dictt={}
        dictt["function_name"]=ques.meta_data.function_name
        dictt["return_type"]=ques.meta_data.return_type
        dictt["variables"]=ques.meta_data.variables
        meta_data=json.dumps(dictt)
        new_ques=Questions(title=title,description=desc,type=type,meta_data=meta_data)
        self.db.add(new_ques)
        self.db.commit()
        self.db.refresh(new_ques)
        # raise HTTPException(status_code=status.HTTP_201_CREATED,detail="new ques created")
        return new_ques




class TestCaseService():
    
    def __init__(self,db:Session):
        self.db=db
    

      
    def create_new_test(self,test:TestSchema,id:int):
        input=test.input_variables
        str_input=json.dumps(input)
        output=test.output
        id1=id
        newtest=TestCase(question_id=id1,input=str_input,expected_output=output)
        self.db.add(newtest)
        self.db.commit()
        self.db.refresh(newtest)

    def get_testcase(self,id:int):
        testcase=self.db.query(TestCase).filter(TestCase.id==id).first()
        if not testcase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="no testcase found")
        return testcase

    def get_testcase_by_question_id(self,id:int):
        testcase=self.db.query(TestCase).filter(TestCase.question_id==id).all()
        if not testcase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="no testcase found")
        return testcase

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


#===============================QUSETION================================
@app.get("/add_ques")
async def add_ques(request: Request):
    
    return templates.TemplateResponse("ques.html",{"request": request})


@app.post('/add_ques',tags=["Questions"])
def add_ques(request: Request, ques: QuesSchema ,db:Session=Depends(get_db)):
    ques_obj=QuesService(db)
    title=ques.title
    if ques_obj.get_ques_by_title(title):
        return {"exist":"ques alredy exits"}
    new_ques=ques_obj.create_new_ques(ques)
    return RedirectResponse(url=f"/create/testcase/{new_ques.id}", status_code=303) 
    

@app.get('/ques/{id}',tags=["Questions"])
def get_ques(id:int,db:Session=Depends(get_db)):
    ques_obj=QuesService(db)
    ques=ques_obj.get_ques_by_id(id)
    variabless=json.loads(ques.meta_data)
    for names in variabless["variables"]:
        print(variabless["variables"][names],names)
    return {
        "title":ques.title,
        "description":ques.description,
        "difficutly":ques.type,
        "variabeles":variabless["variables"],
        "return_type":variabless["return_type"]
    }
    
    
    
# =========================TestCase===================================

@app.get('/create/testcase/{id}',tags=["TestCase"])
def get_testcase(request:Request,id:int,db:Session=Depends(get_db)):
    ques_obj=QuesService(db)
    ques=ques_obj.get_ques_by_id(id)
    meta_dataa=json.loads(ques.meta_data)
    variables=meta_dataa["variables"]
    return templates.TemplateResponse("testcase.html",{"variables":variables,"request":request,"id":id})

@app.post('/create/testcase/{id}',tags=["TestCase"])
def new_testcase(request:Request,test:TestSchema,id:int,db:Session=Depends(get_db)):
    testcase_obj=TestCaseService(db)
    testcase_obj.create_new_test(test,id)
    
    
    
    
# ======================code=========
def execute_user_code(user_code: str, function_name: str, inputs: dict, metadata: dict):
    # Define a module name and create a module specification
    module_name = 'user_module'
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    user_module = importlib.util.module_from_spec(spec)
    user_module.__dict__['List'] = List
    # Execute the user code within the module
    exec(user_code, user_module.__dict__)

    # Get the function reference from the module
    user_function = getattr(user_module, function_name, None)
    if user_function is None:
        raise AttributeError(f"Function '{function_name}' not found in user code.")

    # Prepare function arguments based on inputs
    args = [inputs[var] for var in metadata['variables']]

    # Execute the user function with provided inputs
    result = user_function(*args)

    return result


@app.post('/code/execute/{id}',tags=["code"])
def execute_code(code:usercode,id:int,db:Session=Depends(get_db)):
    ques_obj = QuesService(db)
    test_obj = TestCaseService(db)
    tests = test_obj.get_testcase_by_question_id(id)
    ques = ques_obj.get_ques_by_id(id)
    user_code=code.code
    user_code=textwrap.dedent(user_code)
    print(user_code)
    # user_code = textwrap.dedent("""
    # from typing import List

    # def findfreq(nums: List[int], K: int) -> int:
    #     freq = 0
    #     for num in nums:
    #         if num == K:
    #             freq = freq + 1
    #     return freq
    # """)

    # Example metadata and test case
    # metadata = {
    #     'function_name': 'find_frequency',
    #     'return_type': 'int',
    #     'variables': {'nums': 'List[int]', 'K': 'int'}
    # }
    str_metadata=ques.meta_data
    metadata=json.loads(str_metadata)
    type_mapping = {
    'int': int,
    'float': float,
    'str': str,
    # Add more types as needed
    }

    # Example usage
    return_type = metadata["return_type"]
    expected_output_type = type_mapping.get(return_type, str)  
    print("retur typeeee===",return_type)
    for test in tests:
        test_case_input = json.loads(test.input)     #{"nums": [1, 2, 3, 3], "K": 3}     
        expected_output = expected_output_type(test.expected_output)
        print("test case input====",test_case_input)
        print("test case output====",expected_output)
        # Execute the user code against the test case
        try:
            actual_output = execute_user_code(user_code, metadata['function_name'], test_case_input, metadata)
            print(f"Actual Output: {actual_output}")

            # Compare actual output with expected output
            if actual_output == expected_output:
                continue
            else:
                return{"test case failed with ans":actual_output}
        except Exception as e:
            return{"error":f"Error occurred during execution: {e}"}
    return{"all test case passed":"ok"}
    
