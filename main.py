from fastapi import FastAPI, Depends, status, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from models import SkillCreate, SkillResponse, SkillLevel, SkillCategory, SkillUpdate, UserCreate, UserResponse, UserLogin
from sqlalchemy.orm import Session
from db import get_db, Skill, User
from typing import List
from tokens import create_access, create_refresh, verify_user, verify_token

app = FastAPI()

@app.get("/", tags=["General"])
def root():
    """Головна сторінка API з інформацією про доступні endpoints"""

    return {
        "message": "Ласкаво просимо до SkillSwap API!",
        "description": "Платформа для обміну навичками",
        "version": "1.0.0",
        "endpoints": {
            "documentation": "/docs",
            "skills": "/skills",
        }
    }

 
@app.post('/skills', response_model=SkillResponse, status_code=status.HTTP_201_CREATED, tags=['Skills'])
def add_skill(skill: SkillCreate, db: Session = Depends(get_db)):
    """
    Створити нову навичку.


    - **title**: назва навички (3-100 символів)
    - **description**: опис навички (10-500 символів)
    - **category**: категорія навички
    - **level**: рівень володіння
    - **can_teach**: чи можете навчати
    - **want_learn**: чи хочете вивчити
    """
    new_skill = Skill(**skill.model_dump())

    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    
    return new_skill 
    

@app.get('/skills', response_model=List[SkillResponse], tags=['Skills'], status_code=status.HTTP_200_OK)
def get_skills(
    category: SkillCategory = Query(None, description='Skill category'),
    level: SkillLevel = Query(None, description='Skill level'),
    can_teach: bool = Query(None, description='Can teach'),
    want_learn: bool = Query(None, description='Want learn'),
    db: Session = Depends(get_db)      
    ):
    """
        Фільтри:
    - **category**: фільтр за категорією
    - **level**: фільтр за рівнем
    - **can_teach**: показати тільки тих, хто може навчати
    - **want_learn**: показати тільки тих, хто хоче вчитися
    """
    query_skills = db.query(Skill)

    if category:
        query_skills = query_skills.filter_by(category=category)

    if level:
        query_skills = query_skills.filter_by(level=level)

    if can_teach:
        query_skills = query_skills.filter_by(can_teach=can_teach)

    if want_learn:
        query_skills = query_skills.filter_by(want_learn=want_learn)

    skills = query_skills.all()

    return skills


@app.get('/skills{id}', response_model=SkillResponse, status_code=status.HTTP_200_OK, tags=['Skills'])
def get_skill_by_id(id: int, db: Session = Depends(get_db)):
    """Отримати детальну інформацію про навичку за ID"""
    skill = db.query(Skill).filter_by(id=id).first()

    if skill:
        return skill
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Навичка з ID {id} не знайдена")
    

@app.patch('/skills/{id}', response_model=SkillResponse, tags=['Skills'])
def update_skill(id: int, updated_skill: SkillUpdate, db: Session = Depends(get_db)):
    """Оновити існуючу навичку. Всі поля опціональні."""

    skill = db.query(Skill).filter_by(id=id).first()

    if skill:
        update_skill = updated_skill.model_dump(exclude_unset=True)

        for k, v in update_skill.items():
            setattr(skill, k, v)

        db.commit()
        db.refresh(skill)

        return skill

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Навичка з ID {id} не знайдена")
    

@app.delete('/skills/{id}', response_model=SkillResponse, tags=['Skills'])
def del_skill(id: int, db: Session = Depends(get_db)):
    """Видалити навичку."""
    skill = db.query(Skill).filter_by(id=id).first()

    if skill:
        db.delete(skill)
        db.commit()

        return skill
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Навичка з ID {id} не знайдена")


@app.get('/users', response_model=UserResponse, tags=['Users'])
def get_users(db: Session = Depends(get_db)):
    """Отримати всіх користовачів"""
    users = db.query(User).all()

    if users:
        return users
    else:
        return "Не знайдено жодного користовача"
    

@app.get('/users/{id}', response_model=UserResponse, tags=['Users'])
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    """Отримати юзера за ID"""
    user = db.query(User).filter_by(id=id)

    if user:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Юзера з ID {id} не знайдена")


@app.post('/register', response_model=UserResponse, tags=['Users'])
def register(data: UserCreate, db: Session = Depends(get_db)):
    user = data.model_dump()

    new_user = User(**user)

    new_user.set_password(user['password'])

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    user.pop('password')

    access = create_access(user)
    refresh = create_refresh(user)

    
    if access and refresh:
        res = JSONResponse({'message': 'successfuly created', 'user': user}, status_code=status.HTTP_201_CREATED)

        res.set_cookie(
            key="access_token",
            value=access,
            max_age=900,
            httponly=True,
            samesite="lax"
        )

        res.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60 * 60 * 24 * 7
        )

        return res    


@app.post('/login', response_model=UserResponse, tags=['Users'])
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = data.model_dump()

    db_user = db.query(User).filter_by(username=user.get('username')).first()

    if db_user.check_password(user.get('password')):
        access = create_access(user)
        refresh = create_refresh(user)

    
        if access and refresh:
            res = JSONResponse({'message': 'successfuly logined'}, status_code=status.HTTP_201_CREATED)

            res.set_cookie(
                key="access_token",
                value=access,
                max_age=900,
                httponly=True,
                samesite="lax"
            )

            res.set_cookie(
                key="refresh_token",
                value=refresh,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=60 * 60 * 24 * 7
            )

            return res    
    else:
        raise HTTPException(detail='Unauthorized', status_code=status.HTTP_401_UNAUTHORIZED)
    
    
@app.post('/refresh', tags=['Tokens'])
def refresh(req: Request):
    refresh = req.cookies.get('refresh_token')

    if refresh:
        payload = verify_token(refresh)

        token = create_access(payload)

        res = JSONResponse({'message': 'token was gived'}, status_code=status.HTTP_201_CREATED)


        res.set_cookie(
            key="access_token",
            value=token,
            max_age=900,
            httponly=True,
            samesite="lax"
        )
        
        return res
    else:
        raise HTTPException(detail='Bad request', status_code=status.HTTP_400_BAD_REQUEST)

