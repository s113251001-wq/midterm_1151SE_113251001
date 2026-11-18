from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from database import SessionLocal
from models import User, Article

app = FastAPI()

# 設定 templates 資料夾路徑
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# 首頁：顯示登入頁
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


# 登入處理
@app.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...)
):
    db = SessionLocal()
    user = db.query(User).filter(
        User.username == username,
        User.password == password
    ).first()
    db.close()

    if user:
        if user.role == "author":
            return RedirectResponse(url=f"/author/{user.id}", status_code=303)
        elif user.role == "editor":
            return RedirectResponse(url=f"/editor/{user.id}", status_code=303)

    return HTMLResponse("<h3>登入失敗，帳號或密碼錯誤</h3><a href='/'>返回登入</a>")


# 作者首頁：查看自己的稿件清單
@app.get("/author/{user_id}", response_class=HTMLResponse)
def author_dashboard(request: Request, user_id: int):
    db = SessionLocal()

    user = db.query(User).filter(
        User.id == user_id,
        User.role == "author"
    ).first()

    if not user:
        db.close()
        return HTMLResponse("<h3>作者不存在</h3>")

    articles = db.query(Article).filter(
        Article.author_id == user_id
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="author_dashboard.html",
        context={
            "user": user,
            "articles": articles
        }
    )


# 顯示新增投稿表單
@app.get("/author/{user_id}/create", response_class=HTMLResponse)
def create_article_form(request: Request, user_id: int):
    db = SessionLocal()

    user = db.query(User).filter(
        User.id == user_id,
        User.role == "author"
    ).first()

    db.close()

    if not user:
        return HTMLResponse("<h3>作者不存在</h3>")

    return templates.TemplateResponse(
        request=request,
        name="article_form.html",
        context={
            "user": user,
            "article": None,
            "action": f"/author/{user_id}/create"
        }
    )


# 處理新增投稿
@app.post("/author/{user_id}/create")
def create_article(
    user_id: int,
    category: str = Form(...),
    title: str = Form(...),
    content: str = Form(...)
):
    db = SessionLocal()

    user = db.query(User).filter(
        User.id == user_id,
        User.role == "author"
    ).first()

    if not user:
        db.close()
        return HTMLResponse("<h3>作者不存在</h3>")

    article = Article(
        author_id=user_id,
        category=category,
        title=title,
        content=content,
        status="編輯中"
    )

    db.add(article)
    db.commit()
    db.close()

    return RedirectResponse(url=f"/author/{user_id}", status_code=303)


# 暫時先做一個編輯首頁占位用，避免 editor 登入後出錯
@app.get("/editor/{user_id}", response_class=HTMLResponse)
def editor_dashboard_placeholder(user_id: int):
    return HTMLResponse(f"<h2>編輯首頁（尚未完成）</h2><p>Editor ID: {user_id}</p><a href='/'>返回登入</a>")