from fastapi import APIRouter, HTTPException, status
from database import supabase
from models.user_models import (
    UserResponse,
    UserActionResponse,
    UserLogin,
    UserRegister,
    TokenResponse
)
from security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(
    prefix = "/auth",
    tags = ["Auth"]
)

@router.post(
    "/register",
    response_model=UserActionResponse,
    status_code=status.HTTP_201_CREATED
    )
def register_user(user: UserRegister):
    normalized_email = str(user.email).strip().lower()

    try:
        existing_user_response = (supabase.table("users").select("id").eq("email",normalized_email).execute())
    except Exception as error:
        print("Registration Error: ",error)
        raise HTTPException (
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to register User."
        )
    if existing_user_response.data:
        raise HTTPException (
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already Exists"
        )
    
    try:
        hashed_password = hash_password(user.password)
    except Exception as error:
        print("Hashing Error: ",error)
        raise HTTPException (
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to register User"
        )
    
    user_data = {
        "full_name": user.full_name.strip(),
        "email": normalized_email,
        "password_hash": hashed_password,
        "role": "user",
        "is_active": True
        }

    try:
        created_user_response = (
            supabase
            .table("users")
            .insert(user_data)
            .select("id, full_name, email, role, is_active, created_at")
            .execute()
        )
    except Exception as error:
        print("Registration error: ",error)
        raise HTTPException (
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to register User"
        )
    if not created_user_response.data:
        raise HTTPException (
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create User"
        )
    return {
        "message": "Registration Successful :)",
        "user": created_user_response.data[0]
    }


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
    )
def login_user(user: UserLogin):
    normalized_email = str(user.email).strip().lower()

    try:
        user_response = supabase.table("users").select("*").eq("email",normalized_email).execute()

    except Exception as error:
        print("Login Error: ",error)
        raise HTTPException (
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to Fetch User."
        )
    
    if not user_response.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Email or Password"
        )
    
    stored_user = user_response.data[0]
    try:
        is_valid_password = verify_password(user.password,stored_user["password_hash"])
    except Exception as error:
        print("Password Not Verified: ",error)
        raise HTTPException (
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to login User"
        )
    if not is_valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Email or Password"
        )
    
    if not stored_user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is in Inactive State"
        )
    
    try: 
        access_token = create_access_token(user_id=str(stored_user["id"]))
    except Exception as error:
        print("Access token error: ",error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= "Unable to Complete login"
        )
    return {
        "access_token" : access_token,
        "token_type" : "bearer"
    }

    # safe_user = {
    #     "id": stored_user["id"],
    #     "full_name": stored_user["full_name"],
    #     "email": stored_user["email"],
    #     "role": stored_user["role"],    
    #     "is_active": stored_user["is_active"],
    #     "created_at": stored_user["created_at"],
    # }

    # return {
    #     "message": "Login Successful",
    #     "user": safe_user
    # }