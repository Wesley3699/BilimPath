from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import User, Institution, Group, StudentProfile, TeacherProfile, UserRole
from app.schemas import UserCreate, UserResponse, Token
from app.security import get_password_hash, verify_password, create_access_token
from app.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role
    )

    if user_data.role == UserRole.teacher:
        if not user_data.institution_code:
            raise HTTPException(status_code=400, detail="Преподаватель должен указать код учреждения (institution_code)")
        
        res = await db.execute(select(Institution).where(Institution.short_code == user_data.institution_code))
        institution = res.scalars().first()
        if not institution:
            raise HTTPException(status_code=404, detail="Учреждение не найдено")
        
        new_user.institution_id = institution.id
        db.add(new_user)
        await db.flush()
        
        db.add(TeacherProfile(user_id=new_user.id))

    elif user_data.role == UserRole.student:
        if not user_data.invite_code:
            raise HTTPException(status_code=400, detail="Студент должен указать код группы (invite_code)")
        
        res = await db.execute(select(Group).where(Group.invite_code == user_data.invite_code))
        group = res.scalars().first()
        if not group:
            raise HTTPException(status_code=404, detail="Группа не найдена")
        
        new_user.institution_id = group.institution_id
        db.add(new_user)
        await db.flush()

        db.add(StudentProfile(user_id=new_user.id, group_id=group.id))

    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")
    
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}