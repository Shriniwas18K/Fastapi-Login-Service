This is backend repository
____________________________________________

        Owners special instructions 
____________________________________________

1) sign up with phone,username and password

    POST request to
            http://127.0.0.1:8000/signup/
    request body will be json
     {   
          "phone" : 8954868665,
          "username": "bergbvetv",
          "password": "9056954690"
    }
    response returned will be 
    {
        "message": "user created"
    }

    Signup occurs only once , if tried again then 
    response returned will be
    {
        "message": "user already exists try to login"
    }

2) login with that phone,username and password

    GET request to
            http://127.0.0.1:8000/login/
    request body will be json
        {   
          "phone" : 8954868665,
          "username": "bergbvetv",
          "password": "9056954690"
        }
    
    response returned will be
    {
         "token": "Uuxt6MjEFEL2VYqK0T8YybZiIWU=*hl+75Qq/xtAaUktrCXtA3Q==*6DJ4ExTU/  c0J6EeH/xyEMA==*LvXtk0D8jealdGc3NU2oGg=="
    }
    this is authentication token which will be valid for 1 hour only
    this will be stored at frontend , and will be sent for routes
    which involves posting,editing,removing properties

    By default it is assumed that we have stored username at frontend
    which will be useful for all further routes involving posting,
    editing,removing properties



------------------------------------------------------------------
developed till 11 march 2023
currently owners can signup and login only 
------------------------------------------------------------------




3)post a property as owner when logged in and has valid access token

    frontend code for this :
    --------------------------------------------------------------
    // Define the token
    const tokenvalue = "Uuxt6MjEFEL2VYqK0T8YybZiIWU=*hl+75Qq/xtAaUktrCXtA3Q==*6DJ4ExTU/  c0J6EeH/xyEMA==*LvXtk0D8jealdGc3NU2oGg==";
    // Construct the request URL with the token as a URL parameter
    const url = `/postProperty/?token=${encodeURIComponent(tokenvalue)}`;
    --------------------------------------------------------------

    POST request to
        http://127.0.0.1:8000/postProperty/?token=${tokenvalue}

    request body is:
    {   
        "phone" : "8954868665"
        "username": "bergbvetv",
        "address": "123 Main St",
        "pincode": 412434,
        "noOfPeopleToAccomodate": 4,
        "rentPerPerson": 500,
        "areaInSqft": 1000.0,
        "wifiFacility": "Yes",
        "furnished": "Yes",
        "description": "Spacious apartment with modern amenities"
    }
    response will be
    {
     "message": "post successful"
    }


-----------------------------------------------------------------------
developed till 12 march 2023

currently tokens are not getting properly validated , even though
they are valid but control flow does not reach the try block of validation function
it directly goes to except block

also sqlite queires are causing insertion , and retrieval issues due
to them being weakly typed
-----------------------------------------------------------------------
