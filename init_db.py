from database import engine, SessionLocal
from models import Base, User

def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    author = db.query(User).filter(User.username == "author1").first()
    if not author:
        db.add(User(username="author1", password="1234", role="author"))

    editor = db.query(User).filter(User.username == "editor1").first()
    if not editor:
        db.add(User(username="editor1", password="1234", role="editor"))

    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
    print("資料庫初始化完成")