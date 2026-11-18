from fastapi import FastAPI, Request  # ⚠️ 確認有 import Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from db import lifespan
from routers import auth, author, editor  # ⚠️ 確認三個都有 import

app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key="你的亂碼")

app.mount("/static", StaticFiles(directory="static"), name="static")

# ⚠️ 確認三個路由都有掛載
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