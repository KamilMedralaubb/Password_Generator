from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, conint
import secrets
import string
import datetime

from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Password Generator",
    description="Aplikacja do generowania haseł w Python FastAPI",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Prosta "baza danych" w pamięci na potrzeby przykładu:
password_history = []

# Model danych do generowania hasła:
class PasswordRequest(BaseModel):
    length: conint(gt=0, lt=129)  # ograniczenie długości: 1-128
    use_digits: bool = True
    use_uppercase: bool = True
    use_symbols: bool = True

# Model danych przechowujący hasło i metadane:
class PasswordData(BaseModel):
    password: str
    created_at: datetime.datetime


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Endpoint zwracający prostą stronę HTML z formularzem do generowania haseł.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate", response_class=JSONResponse)
async def generate_password(password_req: PasswordRequest):
    """
    Endpoint do generowania bezpiecznych haseł na podstawie zadanych parametrów.
    """
    # Zbuduj zestaw znaków na podstawie parametrów:
    characters = string.ascii_lowercase  # zawsze używamy liter małych
    if password_req.use_uppercase:
        characters += string.ascii_uppercase
    if password_req.use_digits:
        characters += string.digits
    if password_req.use_symbols:
        # Można ograniczyć się do bezpiecznych znaków specjalnych:
        characters += "!@#$%^&*()-_=+[]{}<>?/"
    
    # Gdyby zestaw znaków okazał się pusty:
    if not characters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Zestaw znaków do generowania haseł jest pusty."
        )

    # Generowanie hasła z biblioteki secrets (kryptograficznie bezpieczna losowość):
    generated_password = "".join(secrets.choice(characters) for _ in range(password_req.length))

    # Zapisz historię:
    record = PasswordData(
        password=generated_password,
        created_at=datetime.datetime.utcnow()
    )
    password_history.append(record.dict())

    return {"generated_password": generated_password}


@app.get("/history", response_class=JSONResponse)
async def get_password_history():
    """
    Endpoint zwracający historię wygenerowanych haseł (w celach demonstracyjnych).
    W produkcyjnej aplikacji należy rozważyć lepsze zabezpieczenia i przechowywanie (np. hashowanie).
    """
    return {"history": password_history}


@app.delete("/history/clear", response_class=JSONResponse)
async def clear_history():
    """
    Endpoint do czyszczenia historii wygenerowanych haseł.
    """
    password_history.clear()
    return {"message": "Historia haseł została wyczyszczona."}


# Przykład obsługi błędów globalnie (opcjonalne):
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Wystąpił nieoczekiwany błąd serwera."}
    )
