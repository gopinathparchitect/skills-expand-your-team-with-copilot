from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, constr
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer

# Dummy user DB for demonstration
users_db = {}

router = APIRouter(prefix="/api/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Pydantic models
class UserBase(BaseModel):
    name: constr(min_length=1, max_length=50)
    email: EmailStr
    role: constr(min_length=1, max_length=20)

class UserCreate(UserBase):
    password: constr(min_length=6, max_length=128)

class UserUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=50)]
    email: Optional[EmailStr]
    role: Optional[constr(min_length=1, max_length=20)]

class UserOut(UserBase):
    id: int

# Dependency for authentication (dummy)
def get_current_user(token: str = Depends(oauth2_scheme)):
    # TODO: Implement JWT validation
    if token != "valid-token":
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return {"id": 1, "role": "admin"}

def admin_required(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

# Endpoints
@router.get("/", response_model=List[UserOut])
def list_users(current_user=Depends(get_current_user)):
    return list(users_db.values())

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, current_user=Depends(get_current_user)):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, current_user=Depends(admin_required)):
    user_id = len(users_db) + 1
    user_data = user.dict()
    user_data.pop("password")  # Don't store password in plain text
    user_out = {"id": user_id, **user_data}
    users_db[user_id] = user_out
    return user_out

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user: UserUpdate, current_user=Depends(admin_required)):
    existing = users_db.get(user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = user.dict(exclude_unset=True)
    existing.update(update_data)
    users_db[user_id] = existing
    return existing

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, current_user=Depends(admin_required)):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del users_db[user_id]
    return None
