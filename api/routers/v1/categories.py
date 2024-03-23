from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from api.schemas import models, types
from api.deps import get_db, get_current_user, on_validate_admin
import cloudinary
import cloudinary.uploader
from cloudinary import uploader
import uuid

router = APIRouter()


@router.get('/get')
async def get_category(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    user = (
        db.query(models.User)
        .filter(models.User.email == current_user.get('sub'))
        .first()
    )

    on_validate_admin(user.role)

    categories = db.query(models.Category).all()

    return {
        'message': 'Get categoty in commerces',
        'db': categories,
        'status': status.HTTP_200_OK,
    }


@router.post('/create')
async def create_category(
    name: str = Form(),
    image: UploadFile = File(),
    description: str = Form(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = (
        db.query(models.User).filter(models.User.email == current_user['sub']).first()
    )

    on_validate_admin(user.role)

    public_id = str(uuid.uuid4())

    try:
        file_content = image.file.read()
        upload_result = cloudinary.uploader.upload(
            file_content,
            public_id=public_id,
            unique_filename=True,
            overwrite=False,
        )
        print(upload_result)
        image_url = upload_result['secure_url']

    except cloudinary.exceptions.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error uploading the image: {str(e)}',
        )

    db_user = models.Category(name=name, image=image_url, description=description)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {
        'message': 'new category was created',
        'status': status.HTTP_200_OK,
    }

@router.post("/delete")
async def delete_category(
    id: types.CategoryOptions,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = (
        db.query(models.User)
        .filter(models.User.email == current_user.get("sub"))
        .first()
    )

    on_validate_admin(user.role)

    category = db.query(models.Category).filter(models.Category.id == id.id).first()

    uploader.destroy(category.image_publi_id)

    db.query(models.Category).filter(models.Category.id == id.id).delete()

    db.commit()

    return {
        "message": "Delete categoty",
        "db": category,
        "status": status.HTTP_200_OK,
    }
