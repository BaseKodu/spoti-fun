from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
import httpx
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static") # Mount a static files directory

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/api/token"
CLIENT_ID = "62728631c89e4c90a2d8eb8cd588f0b5"
CLIENT_SECRET = "c233c224853448a492ee5e064f182f41"
REDIRECT_URI = "localhost:8000"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Render a template file, passing any necessary data as context
    return templates.TemplateResponse("home.html", {"request": request, "title":"Home Page", "message": "Hello World"})


async def get_spotify_token(code: str, redirect_uri: str) -> str:
    """Exchange the authorization code for an access token."""
    auth = (CLIENT_ID, CLIENT_SECRET)
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(SPOTIFY_AUTH_URL, data=data, auth=auth)
    response.raise_for_status()  # Raises exception for 4XX/5XX responses
    return response.json()["access_token"]


@app.get("/spotify-auth")
async def spotify_auth(code: str = Depends(oauth2_scheme)):
    try:
        token = await get_spotify_token(code, REDIRECT_URI)
        return {"access_token": token}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to authenticate with Spotify",
        )
