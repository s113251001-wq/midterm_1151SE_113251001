# routers/editor.py
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db import getDB
from deps import require_editor

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 1. 編輯首頁：查看待審查清單 & 已通過清單
@router.get("/editor/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user = Depends(require_editor),
    conn = Depends(getDB)
):
    async with conn.cursor() as cur:
        # 查詢 1：待審查清單 (審查中)
        await cur.execute(
            """SELECT s.id, s.category, s.title, s.updated_at, u.username AS author_name
               FROM submissions s
               JOIN users u ON s.author_id = u.id
               WHERE s.status = '審查中'
               ORDER BY s.updated_at ASC"""
        )
        pending_submissions = await cur.fetchall()

        # 查詢 2：已處理清單 (已通過)
        await cur.execute(
            """SELECT s.id, s.category, s.title, s.updated_at, u.username AS author_name
               FROM submissions s
               JOIN users u ON s.author_id = u.id
               WHERE s.status = '已通過'
               ORDER BY s.updated_at DESC"""
        )
        approved_submissions = await cur.fetchall()

    return templates.TemplateResponse(
        request=request,
        name="editor_dashboard.html",
        context={
            "user": user, 
            "pending_submissions": pending_submissions,
            "approved_submissions": approved_submissions
        }
    )

# 2. 查看稿件詳情 (移除了狀態防呆，讓編輯可以看歷史紀錄)
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
        await cur.execute(
            """UPDATE submissions 
               SET status = '編輯中', updated_at = CURRENT_TIMESTAMP 
               WHERE id = %s AND status = '審查中'""",
            (sub_id,)
        )
    return RedirectResponse(url="/editor/dashboard", status_code=303)