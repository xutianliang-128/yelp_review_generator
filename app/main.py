import os
import pathlib
from typing import Optional
from fastapi import FastAPI, Form, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from keytotext import trainer
from cassandra.query import SimpleStatement
from cassandra.cqlengine.management import sync_table


#
# from . import (
#     config,
#     db,
#     models,
#     ml,
#     schema
# )

app = FastAPI()
#settings = config.get_settings()

BASE_DIR = pathlib.Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR.parent / "static"
MODEL_DIR = BASE_DIR.parent / "models"

template = Jinja2Templates(directory=f"{STATIC_DIR}")
# SMS_SPAM_MODEL_DIR = MODEL_DIR / "spam-sms"
# MODEL_PATH = SMS_SPAM_MODEL_DIR / "spam-model.h5"
# TOKENIZER_PATH = SMS_SPAM_MODEL_DIR / "spam-classifer-tokenizer.json"
# METADATA_PATH = SMS_SPAM_MODEL_DIR / "spam-classifer-metadata.json"

AI_MODEL = None
#TOKENIZER = None
# DB_SESSION = None
#SMSInference = models.SMSInference


# @app.on_event("startup")
# def on_startup():
#     global AI_MODEL, DB_SESSION
#     AI_MODEL = ml.AIModel(
#         model_path=MODEL_PATH,
#         tokenizer_path=TOKENIZER_PATH,
#         metadata_path=METADATA_PATH
#     )
#     DB_SESSION = db.get_session()
#     sync_table(SMSInference)

@app.on_event("startup")
def on_startup():
    global AI_MODEL, MODEL_DIR
    AI_MODEL = trainer()
    print(MODEL_DIR)
    AI_MODEL.load_model(f"{MODEL_DIR}", use_gpu=False)

    # DB_SESSION = db.get_session()
    # sync_table(SMSInference)



@app.get("/")
async def read_index(q: Optional[str] = None):
    return {"hello": "world"}


async def predict(a, b, c):
    global AI_MODEL

    string = AI_MODEL.predict([a, b, c], use_gpu=False)
    return string

@app.get("/form")
async def create_form(request: Request):
    return template.TemplateResponse("form.html", context={"request": request})

@app.post("/submitform")
async def handle_form(request: Request, food1: str = Form(), food2: str = Form(), food3: str = Form(),
                      service: str = Form(), atmosphere: str = Form(),
                      waiting_time: str = Form(), hospitality: str = Form()):

    global AI_MODEL
    l = [food1, food2, food3, service, atmosphere, waiting_time, hospitality]
    s = ""
    for item in l:
        words = item.split()
        length = len(words)
        if len(words) == 0:
            continue
        elif len(words) == 1:
            a, b, c = words[0], "", ""
        elif len(words) == 2:
            a, b, c = words[0], words[1], ""
        else:
            a, b, c = words[0], words[1], words[2]
        string = AI_MODEL.predict([a, b, c], use_gpu=False)
        s += string + ". "

    return template.TemplateResponse("output.html", context={"request": request, 'output': s})


# @app.post("/")
# def create_inference(query: schema.Query):
#     global AI_MODEL
#     preds_dict = AI_MODEL.predict_text(query.q)
#     top = preds_dict.get('top')  # {label: , conf}
#     data = {"query": query.q, **top}
#     obj = SMSInference.objects.create(**data)
#     # NoSQL -> cassandra -> DataStax AstraDB
#     return obj
#
#
# @app.get("/inferences")  # /?q=this is awesome
# def list_inference():
#     q = SMSInference.objects.all()
#     print(q)
#     return list(q)
#
#
# @app.get("/inferences/{my_uuid}")  # /?q=this is awesome
# def read_inference(my_uuid):
#     obj = SMSInference.objects.get(uuid=my_uuid)
#     return obj
#
#
# def fetch_rows(
#         stmt: SimpleStatement,
#         fetch_size: int = 25,
#         session=None):
#     stmt.fetch_size = fetch_size
#     result_set = session.execute(stmt)
#     has_pages = result_set.has_more_pages
#     yield "uuid,label,confidence,query,version\n"
#     while has_pages:
#         for row in result_set.current_rows:
#             yield f"{row['uuid']},{row['label']},{row['confidence']},{row['query']},{row['model_version']}\n"
#         has_pages = result_set.has_more_pages
#         result_set = session.execute(stmt, paging_state=result_set.paging_state)
#
#
# @app.get("/dataset")  # /?q=this is awesome
# def export_inferences():
#     global DB_SESSION
#     cql_query = "SELECT * FROM spam_inferences.smsinference LIMIT 10000"
#     statement = SimpleStatement(cql_query)
#     # rows = DB_SESSION.execute(cql_query)
#     return StreamingResponse(fetch_rows(statement, 25, DB_SESSION))

if __name__ == "__main__":
    os.system("uvicorn main: app")


# docker run --expose 8000 -it test_docker
# docker run -p 0.0.0.0:2022:8000/tcp -it test_docker
# ps to find the running process
# kill -9 PID
