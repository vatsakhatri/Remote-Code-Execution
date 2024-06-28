# Remote Code Execution  
- Start Date: 2024-05-16
- Created by : Vatsa Khatri


## Introduction


In this documentation, we will understand the execution of a user code upon some pre-defined testcases.


## ***Backend Configuration***


### Install dependencies


#### Adding the packages into the requirements file:


```
📁 requirements.txt -----

FastAPI
SQLAlchemy
Jinja2
```


#### Executing the installation command again to install the modified libraries in the project


```pip3 install -r requirements.txt```
### Alembic setup (Migrations)
```
cd remote_code
alembic init alembic
```
- this will create a alembic folder and 📁 alembic.ini , below are the changes to be done   
- 
    ```
    📁 alembic.ini ----- 
    
    sqlalchemy.url =mysql+pymysql://root:<password>@localhost:3306
    /<dbname>
    
    
    📁 alembi/env.py ----- 
    
    from models import Base
    target_metadata = Base.metadata
    
    ```


```
alembic revision --autogenerate -m "creat table"
alembic upgrade head
```


### Commands to run
```
cd remote_code
uvicorn main:app --relaod
```



## Schemas


- File path: ```remote_code/schemas.py```

- ### Question schema




    ```
    📁 schemas.py

    class Mete_data(BaseModel):
        function_name:str
        return_type:str
        variables: Dict[str, str]

    class QuesSchema(BaseModel):
        title:str
        description:str
        type:str
        meta_data:Mete_data

    ```
    - ```QuesSchema``` :  The question will have a title, description,type and a metadata.
    - ```Meta_data``` :  the content to be displayed to user.
    - 

- ### TestCase schema

    ```
    class TestSchema(BaseModel):
        input_variables:Dict[str,Any] 
        output:str
    ```
    - `input_variables` : values against which the users code will be run
    - `output` : expected output for the above values


## Endpoints

- `GET /`: Home page.
- `GET /add_ques`: Form to add a new question.

- `POST /add_ques`: Endpoint to add a new question.
    ```
    (Question schema)
    
    {
      "title": "Find the frequency of element",
      "description": "Given an array nums and an element K find frequency of K in nums",
      "type": "Easy",
      "metadata": {
        "function_name": "Findfrequency",
        "return_type": "int",
        "variables": [
          {"name": "nums", "type": "List[int]"},
          {"name": "K", "type": "int"}
        ]
      }
    }
    ```
- `GET /ques/{id}`: Get details of a question by ID.
- `GET /create/testcase/{id}`: Form to create a new test case for a question.
- `POST /create/testcase/{id}`: Endpoint to create a new test case.

    ```
    (TestCase schema)
    
    {
        "input_variables": {"nums":[1,2,2,3],"k":2}
        "output": "2"
    }
    ```
- `POST /code/execute/{id}`: Endpoint to execute user code against a particular question.




## User code

### Dynamically creating module

```
def execute_user_code(user_code: str, function_name: str, inputs: dict, metadata: dict):
   
    module_name = 'user_module'
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    user_module = importlib.util.module_from_spec(spec)
    user_module.__dict__['List'] = List
 
    exec(user_code, user_module.__dict__)

    
    user_function = getattr(user_module, function_name, None)
    if user_function is None:
        raise AttributeError(f"Function '{function_name}' not found in user code.")

   
    args = [inputs[var] for var in metadata['variables']]


    result = user_function(*args)

    return result
```


- First we dynamically create modules using `importlib.util.module_from_spec` and add `Lists`(any other required) to modules global namespace
- We exceute the user_code in the module and retrieve the refernece to that function
- We call the fuction with our testcase arguments and return the result
- Compare this result with the expected result
