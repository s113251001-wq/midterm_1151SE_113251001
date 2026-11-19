from fastapi import FastAPI, Request  
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from db import lifespan
from routers import auth, author, editor  

app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key="e8f4a2b7c9d1e5f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7")

app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(auth.router)
app.include_router(author.router)
app.include_router(editor.router)

@app.get("/")
async def root(request: Request): 
    from fastapi.responses import RedirectResponse
    if "user_id" in request.session:
        role = request.session.get("role")
        return RedirectResponse(url=f"/{role}/dashboard")
    return RedirectResponse(url="/login")