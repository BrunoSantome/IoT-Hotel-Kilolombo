import mysql.connector, json,os,sys
from datetime import datetime, date
from flask import Flask, request
from flask_cors import CORS

def connect_database():
    mydb = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password = os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')

    )
    return mydb
def get_device_states():
    mydb = connect_database()
    aux_dict = {}
    return_list = []
    with mydb.cursor() as mycursor:
        mycursor.execute("select p1.* from device_state p1 inner join ( select room,type,value,max(date) maxdate  from device_state group by room,type ) p2 on p1.room = p2.room and p1.date = p2.maxdate order by p1.date desc;")
        for(id_room, room, type_parameter, value, date) in mycursor:
            aux_dict["room"] = room
            aux_dict["type"] = type_parameter
            aux_dict["value"] = value
            
            return_list.append(aux_dict)
            aux_dict = {}
    json_dump = json.dumps(return_list)
    return json_dump



def insert_device_state(params):
    mydb = connect_database()
    print("params_data: ",params, flush = True)
    with mydb.cursor() as mycursor:
        sql = "INSERT INTO device_state (room, type, value, date) VALUES (%s,%s,%s,%s)"
        print(sql,file=sys.stderr)
        values = (
            params["room"],
            params["type"], 
            params["value"],
            datetime.now()
        )
        mycursor.execute(sql, values)
        mydb.commit()
        return mycursor

app = Flask("name")
CORS(app)


@app.route('/device_state', methods=['GET','POST'])
def device_state():
    print("request: ",request, flush = True)
    print("method: ", request.method, flush = True)
    
    if request.method == 'POST':
        params = request.get_json()
        if len(params)!= 3:
            return {"response":"Incorrect parameters"}, 401
        mycursor = insert_device_state(params)
        return {"response":f"{mycursor.rowcount}records inserted."}, 200
    if request.method == 'GET':
        return get_device_states()

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
app.run(host = HOST, port= PORT, debug= True)
