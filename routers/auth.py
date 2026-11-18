# routers/auth.py
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db import getDB
import bcrypt

# 👇 這兩行非常重要，絕對不能刪掉！
router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if "user_id" in request.session:
        role = request.session.get("role")
        return RedirectResponse(url=f"/{role}/dashboard", status_code=303)
    return templates.TemplateResponse(request=request, name="login.html")

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),  # 👈 接收前端傳來的角色
    conn = Depends(getDB)
):
    # 查詢時加入 role 條件
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT id, username, password_hash, role FROM users WHERE username = %s AND role = %s",
            (username, role)
        )
        user = await cur.fetchone()

    is_valid = False
    if user:
        try:
            is_valid = bcrypt.checkpw(
                password.encode('utf-8'),
                user["password_hash"].encode('utf-8')
            )
        except Exception:
            is_valid = False

    if not is_valid:
        return templates.TemplateResponse(
            request=request, 
            name="login.html", 
            context={"error": "身分、帳號或密碼錯誤"} 
        )

    # 登入成功，寫入 session
    request.session["user_id"] = user["id"]
    request.session["role"] = user["role"]
    request.session["username"] = user["username"]

    # 根據角色跳轉
    if user["role"] == "editor":
        return RedirectResponse(url="/editor/dashboard", status_code=303)
    else:
        return RedirectResponse(url="/author/dashboard", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)