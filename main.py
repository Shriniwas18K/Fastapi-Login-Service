from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
app = FastAPI()
# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
from datetime import datetime
from cryptography.fernet import Fernet
# Generate a key
# key = Fernet.generate_key()
key=b'your_env_variable'
cipher = Fernet(key)


'''********************************************************************
                    database connection and set up
'''
import psycopg2
try:
    connection = psycopg2.connect(
        user="postgres",
        password="WtDEHOANEnCJAiHBkBanzcIUzGCkplNb",
        host="monorail.proxy.rlwy.net",
        port=31171,
        database="railway"
    )
    print("database connected successfully")
    cur=connection.cursor()

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL:", error)
cur.execute(
    '''
    create table if not exists credentials(
        phone varchar(10),
        username varchar(20),
        password varchar(10),
        createdOn timestamp
    )
    '''
)
connection.commit()
'''*********************************************************************'''



'''request models are given below'''
from pydantic import BaseModel
class signinsignup(BaseModel):
    phone:str
    username:str
    password:str

'''*********************************************************
    below given are authentication and token generation 
        validation , signin signup routes
*********************************************************'''

def generate_token():
    '''This function generates a token from currenttimestamp
        which is sent to client frontend, and everytime client
        has to give this token to access any of the owner routes'''
    generationtimestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S").encode()
    return cipher.encrypt(generationtimestamp)

def validate_token(tokenvalue):
    ''' This function checks the validity of the token ,
        one client can use one token on
        one device only for 1 hour, else token will be expired 
        and session will be inactive'''
    try:
        generationtimestamp=cipher.decrypt(tokenvalue)
        generationtimestamp=datetime.strptime(
                                                generationtimestamp.decode(),
                                                "%Y-%m-%d %H:%M:%S"
                                             )
        currenttimestamp=datetime.now()
        diff=currenttimestamp-generationtimestamp
        if(diff.seconds>3600):
            return False
    except:
            return False
    return True

@app.post("/signup/")
async def signup(requ:signinsignup):
    cur.execute(f"select * from credentials where phone='{requ.phone}'")
    rows=cur.fetchall()
    if(len(rows)==1):
        return {
            "message":"user already exists try to signin"
        }
    else:
        cur.execute("insert into credentials values (%s,%s,%s,%s)",(requ.phone,requ.username,requ.password,datetime.now()))
        cur.execute("insert into transactions values(%s,%s,%s)",(datetime.now(),requ.phone,'signup'))
        connection.commit()
        return {
            "message":"user created"
        }
    
@app.post("/signin/")
async def signin(requ:signinsignup):
    '''function will check wheter username exists in database'''
    cur.execute("select * from credentials where phone=%s",(requ.phone,))
    rows=cur.fetchall()
    if(rows==[]):
        return { "message" : "user does not exists pls sign up"}
    else:
        cur.execute("insert into transactions values(%s,%s,%s)",(datetime.now(),requ.phone,'signin'))
        connection.commit()
        '''if exists then we return him token'''
        return{"token":generate_token()}
