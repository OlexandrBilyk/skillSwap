from fastapi import FastAPI, Depends, status, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from models import SkillCreate, SkillResponse, SkillLevel, SkillCategory, SkillUpdate
from sqlalchemy.orm import Session
from db import get_db, Skill, User
from typing import List

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
            "health": "/health"
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
