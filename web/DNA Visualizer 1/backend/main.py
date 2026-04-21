
from fastapi import FastAPI, HTTPException, Request, Response
from src.dna import generate_molecule
from src.tokens import decode_token, encode_token
from src.models import DNAProfile, DNAGeneration
from src.constants import *
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    redirect_slashes=False,
    middleware=[
        Middleware(CORSMiddleware, allow_origins=[f"http://{HOSTNAME}:{PORT}", "http://localhost"], allow_credentials=True, allow_headers=["*"], allow_methods=["*"]),
    ],
    docs_url=None, # Disable docs (Swagger UI)
    redoc_url=None, # Disable redoc
)

@app.get("")
@app.get("/")
async def root():
    return {"message": "Welcome to the DNA Molecule Generator!"}

@app.post("/set-mode")
@app.post("/set-mode/")
async def set_mode(profile: DNAProfile, response: Response):
    print("==========", profile.mode, profile.length)
    if not profile.mode or not profile.length:
        raise HTTPException(status_code=400)
    if profile.mode not in ALLOWED_MODES or profile.length not in ALLOWED_LENGTHS:
        raise HTTPException(status_code=400)
    token = encode_token({"mode": profile.mode, "length": profile.length})
    response.set_cookie("profile", token)
    response.status_code = 200

    return {"message": "Profile set successfully!"}

@app.post("/generate")
@app.post("/generate/")
async def generate_dna(gen: DNAGeneration, request: Request):
    # print("------ GENERATE DNA:", request.cookies)
    cookie = decode_token(request.cookies.get('profile'))
    # print("======= COOKIE:", cookie)
    if not cookie:
        raise HTTPException(400, "No profile cookie set!")
    source, rendering  = generate_molecule(gen, cookie)
    return {"source": f"{source}", "molecule": f"{rendering}"}


