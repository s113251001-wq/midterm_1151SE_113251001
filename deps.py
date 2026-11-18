# deps.py
from fastapi import Depends, Request, HTTPException
from db import getDB

async def get_current_user(request: Request, conn=Depends(getDB)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT id, username, role FROM users WHERE id = %s", 
            (user_id,)
        )
        user = await cur.fetchone()
        
    if not user:
        request.session.clear()
        raise HTTPException(status_code=303, headers={"Location": "/login"})
        
    return user

async def require_author(user=Depends(get_current_user)):
    if user["role"] != "author":
        raise HTTPException(status_code=403, detail="只有作者能執行此操作")
    return user

async def require_editor(user=Depends(get_current_user)):
    if user["role"] != "editor":
        raise HTTPException(status_code=403, detail="只有編輯能執行此操作")
    return user