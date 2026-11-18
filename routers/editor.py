# routers/editor.py
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db import getDB
from deps import require_editor

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 1. 編輯首頁：查看待審查清單 (需 JOIN users 取得作者名稱)
@router.get("/editor/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user = Depends(require_editor),
    conn = Depends(getDB)
):
    async with conn.cursor() as cur:
        await cur.execute(
            """SELECT s.id, s.category, s.title, s.updated_at, u.username AS author_name
               FROM submissions s
               JOIN users u ON s.author_id = u.id
               WHERE s.status = '審查中'
               ORDER BY s.updated_at ASC"""
        )
        submissions = await cur.fetchall()

    return templates.TemplateResponse(
        request=request,
        name="editor_dashboard.html",
        context={"user": user, "submissions": submissions}
    )

# 2. 查看稿件詳情
@router.get("/editor/detail/{sub_id}", response_class=HTMLResponse)
async def detail(
    sub_id: int,
    request: Request,
    user = Depends(require_editor),
    conn = Depends(getDB)
):
    async with conn.cursor() as cur:
        await cur.execute(
            """SELECT s.*, u.username AS author_name
               FROM submissions s
               JOIN users u ON s.author_id = u.id
               WHERE s.id = %s""",
            (sub_id,)
        )
        submission = await cur.fetchone()

    if not submission:
        raise HTTPException(status_code=404, detail="找不到該稿件")
        
    # 防呆：只能看審查中的稿件
    if submission["status"] != "審查中":
        return RedirectResponse(url="/editor/dashboard", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="editor_detail.html",
        context={"user": user, "submission": submission}
    )

# 3. 通過稿件 (審查中 -> 已通過)
@router.post("/editor/approve/{sub_id}")
async def approve(
    sub_id: int,
    user = Depends(require_editor),
    conn = Depends(getDB)
):
    async with conn.cursor() as cur:
        # 防呆：WHERE 條件包含 status = '審查中'
        await cur.execute(
            """UPDATE submissions 
               SET status = '已通過', updated_at = CURRENT_TIMESTAMP 
               WHERE id = %s AND status = '審查中'""",
            (sub_id,)
        )
    return RedirectResponse(url="/editor/dashboard", status_code=303)

# 4. 退回稿件 (審查中 -> 編輯中)
@router.post("/editor/reject/{sub_id}")
async def reject(
    sub_id: int,
    user = Depends(require_editor),
    conn = Depends(getDB)
):
    async with conn.cursor() as cur:
        # 防呆：WHERE 條件包含 status = '審查中'
        await cur.execute(
            """UPDATE submissions 
               SET status = '編輯中', updated_at = CURRENT_TIMESTAMP 
               WHERE id = %s AND status = '審查中'""",
            (sub_id,)
        )
    return RedirectResponse(url="/editor/dashboard", status_code=303)