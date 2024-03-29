from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from cryptography.fernet import Fernet
from pydantic import BaseModel
import random
import aiosqlite

app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Generate a key
key = b'B8rPRkgG8ZuBIEIX5z-Auu9qB59jvFdVkJOIXbdlZ6I='
cipher = Fernet(key)


# Request models
class SigninSignup(BaseModel):
    phone: str
    username: str
    password: str


class Property(BaseModel):
    username: str
    phone: str
    address: str
    pincode: int
    city: str
    gender: str
    noOfPeopleToAccommodate: int
    rentPerPerson: int
    areaInSqft: float
    wifiFacility: str
    furnished: str
    url1: str
    url2: str
    url3: str
    description: str


# Authentication and token generation/validation functions
def generate_token():
    generation_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S").encode()
    return cipher.encrypt(generation_timestamp)


def validate_token(token_value):
    try:
        generation_timestamp = cipher.decrypt(token_value)
        generation_timestamp = datetime.strptime(generation_timestamp.decode(), "%Y-%m-%d %H:%M:%S")
        current_timestamp = datetime.now()
        diff = current_timestamp - generation_timestamp
        if diff.seconds > 3600:
            return False
    except:
        return False
    return True


# Endpoints

async def get_cursor():
    async with aiosqlite.connect('example.db') as connection:
        async with connection.cursor() as cursor:
            yield cursor


@app.post("/signup/")
async def signup(req: SigninSignup, cursor: aiosqlite.Cursor = Depends(get_cursor)):
    await cursor.execute(f"SELECT * FROM credentials WHERE phone = '{req.phone}'")
    rows = await cursor.fetchall()
    if len(rows) == 1:
        return {"message": "User already exists. Please sign in."}
    else:
        await cursor.execute(f"INSERT INTO credentials (phone, username, password, createdOn) "
                              f"VALUES ('{req.phone}', '{req.username}', '{req.password}', '{str(datetime.now())}')")
        await cursor.execute(f"INSERT INTO transactions (atTime, phone, description) "
                              f"VALUES ('{str(datetime.now())}', '{req.phone}', 'signup')")
        await cursor.connection.commit()
        return {"message": "User created successfully"}


@app.post("/signin/")
async def signin(req: SigninSignup, cursor: aiosqlite.Cursor = Depends(get_cursor)):
    await cursor.execute(f"SELECT * FROM credentials WHERE phone='{req.phone}'")
    rows = await cursor.fetchall()
    if not rows:
        return {"message": "User does not exist. Please sign up."}
    else:
        await cursor.execute(f"INSERT INTO transactions VALUES ('{str(datetime.now())}', '{req.phone}', 'signin')")
        await cursor.connection.commit()
        token = generate_token()
        return {"token": token}


@app.post("/postProperty/")
async def postProperty(token, req: Property, cursor: aiosqlite.Cursor = Depends(get_cursor)):
    if not validate_token(token):
        return {"error": "Forbidden action. Please sign in."}

    await cursor.execute(f"SELECT COUNT(*), username FROM properties WHERE username='{req.username}' GROUP BY username")
    rows = await cursor.fetchall()

    try:
        if rows[0][0] == 5:
            return {"message": "Limit reached"}
    except IndexError:
        pass

    propertypid = int(random.random() * 100000)
    await cursor.execute(f"INSERT INTO properties VALUES "
                         f"('{propertypid}', '{req.phone}', '{req.username}', '{req.address}', '{req.pincode}', '{req.city}', '{req.gender}',"
                         f"'{req.noOfPeopleToAccommodate}', '{req.rentPerPerson}', '{req.areaInSqft}', "
                         f"'{req.wifiFacility}', '{req.furnished}', '{req.url1}', '{req.url2}', '{req.url3}', "
                         f"'{req.description}', '{str(datetime.now())}')")
    await cursor.execute(f"INSERT INTO transactions VALUES ('{str(datetime.now())}', '{req.phone}', 'new property posted')")
    await cursor.connection.commit()
    return {"message": "Post successful"}


@app.get("/retrieveProperties/")
async def retrieve_properties(city: str, gender: str = None, min_price: int = None, max_price: int = None, cursor: aiosqlite.Cursor = Depends(get_cursor)):
    try:
        query = f"SELECT * FROM properties WHERE city='{city}'"

        if gender is not None:
            query += f" AND gender='{gender}'"

        if min_price is not None:
            query += f" AND rentPerPerson >= {min_price}"

        if max_price is not None:
            query += f" AND rentPerPerson <= {max_price}"

        await cursor.execute(query)
        rows = await cursor.fetchall()

        return rows
    finally:
        await cursor.close()

