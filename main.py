from fastapi import FastAPI
app=FastAPI()
import cryptocode
from datetime import datetime
secret_key="r9m330924mc2059m205052cm5205"
import sqlite3
db_name="auth.db"
conn=sqlite3.connect(db_name)
cur=conn.cursor()
cur.execute(
    "create table if not exists credentials(username,password)"
)
from pydantic import BaseModel
class loginsignup(BaseModel):
    username:str
    password:str

class Property(BaseModel):
    token:str
    address:str
    noOfPeopleToAccomodate:str
    rentPerPerson:str
    areaInSqft:float
    wifiFacility:str
    furnished:str
    description:str


def generate_token():
    '''This function generates a token from currenttimestamp
        which is sent to client frontend, and everytime client
        has to give this token to access any of the owner routes'''
    generationtimestamp=datetime.strftime(datetime.now(),'%d/%m/%Y, %H:%M:%S')
    return cryptocode.encrypt(generationtimestamp,secret_key)

def validate_token(token):
    '''This function checks the validity of the token , one client can use one token on
    one device only for 1 hour, else token will be expired and session will be inactive'''
    try:
        generationtimestamp=cryptocode.decrypt(token,secret_key)
        generationtimestamp=datetime.strptime(generationtimestamp,'%d/%m/%Y, %H:%M:%S')
        currenttimestamp=datetime.now()
        diff=currenttimestamp-generationtimestamp
        if(diff.seconds>3600):
            return False
    except:
            return False
    return True

@app.post("/signup/")
async def signup(requ:loginsignup):
    cur.execute(f"select * from credentials where username={requ.username}")
    rows=cur.fetchall()
    if(len(rows)==1):
        return {
            "message":"user already exists try to login"
        }
    else:
        cur.execute(f"insert into credentials values ({requ.username},{requ.password})")
        return {
            "message":"user created"
        }
    
@app.get("/login/")
async def login(requ:loginsignup):
    cur.execute(f"select * from credentials where username={requ.username}")
    rows=cur.fetchall()
    if(rows==[]):
        return { "message" : "user does not exists pls sign up"}
    else:
        return{"token":generate_token()}

@app.post("/postProperty/")
async def postProperty(req:Property):
    if((validate_token(req.token))==False):
        return {"error" : "forbidden action pls login "}
    return{"message":"post successful"}

