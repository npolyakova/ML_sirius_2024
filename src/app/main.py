from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import psycopg2

app = FastAPI()

def get_categories():
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

def get_suggest(category1: str, category2: str):
    try:
        conn = psycopg2.connect('postgresql://ml_user:pgpass@localhost:5432/mldb')
    except:
        print('Can`t establish connection to database')

    cursor = conn.cursor()
    cursor.execute(f'SELECT next_category FROM mapping WHERE category_1 = {category1} AND category_2 = {category2}')
    next_cat = cursor.fetchone()
    cursor.close()
    conn.close()

    return {"id": next_cat[0], "name": next_cat[1]}

@app.get("/")
def read_root():
    return {"message" : "This is the api for education ML project"}

@app.get("/categories")
def get_all_categories():
    cat_dict = {"categories": get_categories()}
    json_compatible_item_data = jsonable_encoder(cat_dict)
    return JSONResponse(content=json_compatible_item_data)

@app.get("/suggest")
def get_model(category1, category2):
    json_compatible_item_data = jsonable_encoder(get_suggest(category1, category2))
    return JSONResponse(content=json_compatible_item_data)
