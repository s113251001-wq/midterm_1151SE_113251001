# routers/author.py
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db import getDB
from deps import require_author

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 1. 作者首頁：查看稿件清單
@router.get("/author/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user = Depends(require_author),
    conn = Depends(getDB)
):
    async with conn.cursor() as cur:
        await cur.execute(
            """SELECT id, category, title, status, updated_at 
               FROM submissions 
               WHERE author_id = %s 
               ORDER BY updated_at DESC""",
            (user["id"],)
        )
        submissions = await cur.fetchall()

    return templates.TemplateResponse(
        request=request,
        name="author_dashboard.html",
        context={"user": user, "submissions": submissions}
    )

# 2. 顯示「新增投稿」表單
@router.get("/author/new", response_class=HTMLResponse)
async def new_form(request: Request, user = Depends(require_author)):
    return templates.TemplateResponse(
        request=request,
        name="author_form.html",
        context={"user": user, "submission": None}
    )

# 3. 處理「新增投稿」送出
@router.post("/author/new")
async def create(
    request: Request,
    user = Depends(require_author),
    conn = Depends(getDB),
    category: str = Form(...),
    title: str = Form(...),
    content: str = Form(...)
):
    async with conn.cursor() as cur:
        await cur.execute(
            """INSERT INTO submissions (author_id, category, title, content, status) 
               VALUES (%s, %s, %s, %s, '編輯中')""",
            (user["id"], category, title, content)
        )
    return RedirectResponse(url="/author/dashboard", status_code=303)

# 4. 顯示「編輯投稿」表單
@router.get("/author/edit/{sub_id}", response_class=HTMLResponse)
async def edit_form(
    sub_id: int,
    request: Request,
    user = Depends(require_author),
    conn = Depends(getDB)
):
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT * FROM submissions WHERE id = %s AND author_id = %s",
            (sub_id, user["id"])
        )
        submission = await cur.fetchone()

    if not submission:
        raise HTTPException(status_code=404, detail="找不到稿件或無權限")
    
    # 防呆：只有編輯中才能修改
    if submission["status"] != "編輯中":
        return RedirectResponse(url="/author/dashboard", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="author_form.html",
        context={"user": user, "submission": submission}
    )

# 5. 處理「編輯投稿」送出
@router.post("/author/edit/{sub_id}")
async def update(
    sub_id: int,
    request: Request,
    user = Depends(require_author),
    conn = Depends(getDB),
    category: str = Form(...),
    title: str = Form(...),
    content: str = Form(...)
):
    async with conn.cursor() as cur:
        # 防呆：WHERE 條件包含 author_id 與 status，確保不會改到別人的或已送出的
        await cur.execute(
            """UPDATE submissions 
               SET category = %s, title = %s, content = %s, updated_at = CURRENT_TIMESTAMP 
               WHERE id = %s AND author_id = %s AND status = '編輯中'""",
            (category, title, content, sub_id, user["id"])
        )
    return RedirectResponse(url="/author/dashboard", status_code=303)

# 6. 處理「刪除稿件」
@router.post("/author/delete/{sub_id}")
async def delete(
    sub_id: int,
    user = Depends(require_author),
    conn = Depends(getDB)
):
    async with conn.cursor() as cur:
        # 防呆：只能刪自己的，且只有編輯中能刪
        await cur.execute(
            "DELETE FROM submissions WHERE id = %s AND author_id = %s AND status = '編輯中'",
            (sub_id, user["id"])
        )
    return RedirectResponse(url="/author/dashboard", status_code=303)

# 7. 處理「送出投稿」
@router.post("/author/submit/{sub_id}")
async def submit(
    sub_id: int,
    user = Depends(require_author),
    conn = Depends(getDB)
):
    async with conn.cursor() as cur:
        # 防呆：確認是編輯中，才能轉為審查中
        await cur.execute(
            """UPDATE submissions 
               SET status = '審查中', updated_at = CURRENT_TIMESTAMP 
               WHERE id = %s AND author_id = %s AND status = '編輯中'""",
            (sub_id, user["id"])
        )
    return RedirectResponse(url="/author/dashboard", status_code=303)