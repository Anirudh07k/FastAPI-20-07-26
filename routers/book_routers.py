from fastapi import APIRouter, HTTPException, status
from database import supabase
from models.book_models import(
    BookCreate,
    BookPatch,
    BookUpdate,
    BookResponse,
    BookActionResponse
)
from dependencies import CurrentAdmin

router = APIRouter(
    prefix="/books",
    tags=["Books"]
)

@router.get("",
            response_model=list[BookResponse],
            status_code=status.HTTP_200_OK
            )
def get_books():
    try:
        response = supabase.table("books").select("*").execute()
            
    except Exception as error:
        print("Get Request Error : ", error)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Unable to retrieve books data from database"
            )
    return response.data


@router.get("/{book_id}",
            response_model=BookResponse,
            status_code=status.HTTP_200_OK
            )
def get_book_by_id(book_id: int):
    try:
        response = supabase.table("books").select("*").eq("id",book_id).execute()
            
    except Exception as error:
        print("Get Request Error : ", error)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Unable to retrieve books data from database"
            )
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book Not Found"
        )
    return response.data[0]


@router.post("",
            response_model=BookActionResponse,
            status_code=status.HTTP_201_CREATED
            )
def add_new_book(book: BookCreate, current_admin : CurrentAdmin):
    try:
        response = supabase.table("books").insert(book.model_dump()).select("*").execute()
            
    except Exception as error:  
        print("Post Request Error : ", error)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Unable to Create book"
            )
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book was not Created"
        )
    return {
        "message": "Book created successfully",
        "book": response.data[0]
        }


@router.put("/{book_id}", response_model=BookActionResponse, status_code=status.HTTP_200_OK)
def update_book(book_id: int, book: BookUpdate, current_admin : CurrentAdmin):
    try:
        response = (
            supabase.table("books")
            .update(book.model_dump())
            .eq("id", book_id)
            .execute()
        )
    except Exception as error:
        print("Put Request Error : ", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update book"
        )

    if not response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    return {"message": "Book updated successfully", "book": response.data[0]}


@router.patch(
        "/{book_id}", 
        response_model=BookActionResponse, 
        status_code=status.HTTP_200_OK
        )
def patch_book(book_id: int, book: BookPatch, current_admin : CurrentAdmin):
    patch_book = book.model_dump(exclude_unset=True, exclude_none=True)
    if not patch_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one field to update"
        )

    try:
        response = supabase.table("books").update(patch_book).eq("id", book_id).select("*").execute()
    except Exception as error:
        print("Patch Request Error : ", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update book"
        )

    if not response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    return {"message": "Book updated successfully", "book": response.data[0]}


@router.delete(
        "/{book_id}", 
        response_model=BookActionResponse, 
        status_code=status.HTTP_200_OK
        )
def delete_book(book_id: int, current_admin : CurrentAdmin):
    try:
        response = (supabase.table("books").delete().eq("id", book_id).select("*").execute())
    except Exception as error:
        print("Delete Request Error : ", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete book"
        )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Book not found"
            )

    return {
        "message": "Book deleted successfully", 
        "book": response.data[0]
        }