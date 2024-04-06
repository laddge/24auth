import os
import json
import time
import shortuuid
from dotenv import load_dotenv
import httpx
from typing import Union
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

app = FastAPI()

app.mount("/24auth/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/24auth/")
async def read_root(
    request: Request, code: Union[str, None] = None, response_class=HTMLResponse
):
    if not code:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "auth_url": (
                    f"{AUTHORIZATION_URL}?response_type=code&client_id={CLIENT_ID}&"
                    f"redirect_uri={REDIRECT_URI}&scope=openid&"
                    f"access_type=offline&prompt=consent&hd=gl.cc.uec.ac.jp"
                )
            },
        )
    else:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": REDIRECT_URI,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                },
            )
        token_response_json = token_response.json()
        if token_response.is_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=token_response_json,
            )
        codes = {}
        try:
            with open("codes.json") as f:
                codes = json.load(f)
        except Exception:
            pass
        code = shortuuid.uuid()
        codes[code] = time.time()
        with open("codes.json", "w") as f:
            json.dump(codes, f)
        return templates.TemplateResponse(
                request=request, name="callback.html", context={"code": code}
        )
