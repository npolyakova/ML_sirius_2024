from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import psycopg2

app = FastAPI()

def get_categories():
    conn = None
    try:
        conn = psycopg2.connect('postgresql://ml_user:pgpass@localhost:5432/mldb')
    except:
        print('Can`t establish connection to database')

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categories')
    all_cats = cursor.fetchall()
    cursor.close()
    conn.close()

    pre_json = []
    for item in all_cats:
        pre_json.append({"id": item[0], "name": item[1]})

    return pre_json

@app.get("/")
def read_root():
    return {"message" : "This is the api for education ML project"}

@app.get("/categories")
def get_all_categories():
    cat_dict = {"categories": get_categories()}
    json_compatible_item_data = jsonable_encoder(cat_dict)
    return JSONResponse(content=json_compatible_item_data)
