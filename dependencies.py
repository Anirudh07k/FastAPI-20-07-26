from typing import Annotated
from fastapi import (Depends, HTTPException, status)
from fastapi.security import (HTTPAuthorizationCredentials, HTTPBearer)
from database import supabase
from models.user_models import UserResponse
from security import decode_access_token

bearer_scheme = HTTPBearer(
    bearerFormat="JWT",
    scheme_name = "JWT Bearer"
)

def get_current_user(credentials : 
                     Annotated[HTTPAuthorizationCredentials, 
                               Depends(bearer_scheme)]) -> UserResponse:
    token =  credentials.credentials
    user_id = decode_access_token(token)

    try:
        user_response = (supabase
                         .table("users")
                         .select("id, full_name, email, role, is_active, created_at")
                         .eq("id", user_id)
                         .execute()
                         )

    except HTTPException as error:
        print("User Lookup error : ",error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrive current user"
        )
    
    if not user_response.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User Account not found",
            headers={
                "WWW-Authenticate" : "Bearer"
            }
        )
    
    user_data = user_response.data[0]

    if not user_data["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return UserResponse.model_validate(user_data)

CurrentUser = Annotated[UserResponse, Depends(get_current_user)]


def require_admin(current_user: CurrentUser) -> UserResponse:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required"
        )
    return current_user

CurrentAdmin = Annotated[UserResponse, Depends(require_admin)]