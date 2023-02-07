import joblib  # for loading model pickle file
import numpy as np  # for array conversion

# FastAPI is a modern, fast (high-performance), web framework for building APIs with Python
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()  # instance of FastAPI class

# mount static folder files to /static route
app.mount("/static", StaticFiles(directory="static"), name="static")

# loads the ML model
model = joblib.load(open("models/model.pkl", "rb"))

# sets the templates folder for the app
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home_index(request: Request):
    """
    Function to render `base.html` at route '/' as a get request
    __Args__:
    - request (Request): request in path operation that will return a template
    __Returns__:
    - TemplateResponse: render `base.html`
    """
    return templates.TemplateResponse("base.html", {"request": request})


@app.post("/predict", response_class=HTMLResponse)
async def predict(
    request: Request,
    age: int = Form(...),
    restingBP: int = Form(...),
    oldpeak: float = Form(...),
    sex: str = Form(...),
    chestpaintype: str = Form(...),
    fastingBS: str = Form(...),
    exerciseAngina: str = Form(...),
    st_slope: str = Form(...),
):
    """
    Function to predict heart diasease classification
    and shows the result by rendering `base.html` at route `/predict`

    __Args__:
    - __request__: request in path operation that will return a template
    - __age__: age of the patient ,
    - __sex__: sex of the patient,
    - __chestpaintype__: chest pain type [_Typical Angina, Atypical Angina, Non-Anginal Pain, Asymptomatic_],
    - __restingBP__: resting blood pressure [_mm Hg_] ,
    - __fastingBS__: fasting blood sugar level,
    - __exerciseAngina__: exercise-induced angina,
    - __oldpeak__: oldpeak [Numeric value measured in depression],
    - __st_slope__: the slope of the peak exercise ST segment,

    __Returns:__
    - __TemplateResponse__: render `base.html`
    """
    sex = 1 if sex == "M" else 0
    fastingBS = 1 if fastingBS == "Yes" else 0
    exerciseAngina = 1 if exerciseAngina == "Yes" else 0

    if chestpaintype == "ASY":
        chestpaintype = 496
    elif chestpaintype == "NAP":
        chestpaintype = 203
    elif chestpaintype == "ATA":
        chestpaintype = 173
    else:
        chestpaintype = 46

    if st_slope == "Flat":
        st_slope = 460
    elif st_slope == "Up":
        st_slope = 395
    else:
        st_slope = 63

    input_list = [
        age,
        sex,
        chestpaintype,
        restingBP,
        fastingBS,
        exerciseAngina,
        oldpeak,
        st_slope,
    ]

    # list --> numpy array
    final_features = [np.array(input_list, dtype=float)]
    prediction = model.predict(final_features)  # prediction using ML model
    probability = np.max(model.predict_proba(final_features)) * 100
    return templates.TemplateResponse(
        "result.html",
        context={
            "prediction": prediction,
            "probability": probability,
            "request": request,
        },
    )
