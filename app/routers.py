from datetime import timedelta

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from app.database import get_db
from app.errors import ApiError

router = APIRouter()
auth_router = APIRouter(prefix="/auth", tags=["auth"])
features_router = APIRouter(prefix="/features", tags=["features"])


@auth_router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise ApiError(
            code="user_exists",
            message="Username already registered",
            status=status.HTTP_400_BAD_REQUEST,
        )
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise ApiError(
            code="email_exists",
            message="Email already registered",
            status=status.HTTP_400_BAD_REQUEST,
        )
    return crud.create_user(db=db, user=user)


@auth_router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise ApiError(
            code="invalid_credentials",
            message="Incorrect username or password",
            status=status.HTTP_401_UNAUTHORIZED,
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@features_router.post(
    "", response_model=schemas.FeatureResponse, status_code=status.HTTP_201_CREATED
)
def create_feature(
    feature: schemas.FeatureCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_feature = crud.create_feature(db=db, feature=feature, owner_id=current_user.id)
    vote_count = crud.get_vote_count(db, db_feature.id)
    response = schemas.FeatureResponse(
        id=db_feature.id,
        title=db_feature.title,
        desc=db_feature.desc,
        owner_id=db_feature.owner_id,
        created_at=db_feature.created_at,
        vote_count=vote_count,
    )
    return response


@features_router.get("", response_model=list[schemas.FeatureResponse])
def read_features(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    features = crud.get_features(db, skip=skip, limit=limit)
    result = []
    for feature in features:
        vote_count = crud.get_vote_count(db, feature.id)
        result.append(
            schemas.FeatureResponse(
                id=feature.id,
                title=feature.title,
                desc=feature.desc,
                owner_id=feature.owner_id,
                created_at=feature.created_at,
                vote_count=vote_count,
            )
        )
    return result


@features_router.get("/top", response_model=list[schemas.FeatureResponse])
def get_top_features(limit: int = 10, db: Session = Depends(get_db)):
    features = crud.get_top_features(db, limit=limit)
    result = []
    for feature in features:
        vote_count = crud.get_vote_count(db, feature.id)
        result.append(
            schemas.FeatureResponse(
                id=feature.id,
                title=feature.title,
                desc=feature.desc,
                owner_id=feature.owner_id,
                created_at=feature.created_at,
                vote_count=vote_count,
            )
        )
    return result


@features_router.get("/{feature_id}", response_model=schemas.FeatureResponse)
def read_feature(feature_id: int, db: Session = Depends(get_db)):
    db_feature = crud.get_feature(db, feature_id=feature_id)
    if db_feature is None:
        raise ApiError(
            code="not_found",
            message="Feature not found",
            status=status.HTTP_404_NOT_FOUND,
        )
    vote_count = crud.get_vote_count(db, feature_id)
    return schemas.FeatureResponse(
        id=db_feature.id,
        title=db_feature.title,
        desc=db_feature.desc,
        owner_id=db_feature.owner_id,
        created_at=db_feature.created_at,
        vote_count=vote_count,
    )


@features_router.put("/{feature_id}", response_model=schemas.FeatureResponse)
def update_feature(
    feature_id: int,
    feature_update: schemas.FeatureUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_feature = crud.update_feature(
        db,
        feature_id=feature_id,
        feature_update=feature_update,
        owner_id=current_user.id,
    )
    if db_feature is None:
        raise ApiError(
            code="not_found_or_forbidden",
            message="Feature not found or you don't have permission to update it",
            status=status.HTTP_404_NOT_FOUND,
        )
    vote_count = crud.get_vote_count(db, feature_id)
    return schemas.FeatureResponse(
        id=db_feature.id,
        title=db_feature.title,
        desc=db_feature.desc,
        owner_id=db_feature.owner_id,
        created_at=db_feature.created_at,
        vote_count=vote_count,
    )


@features_router.delete("/{feature_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feature(
    feature_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    success = crud.delete_feature(db, feature_id=feature_id, owner_id=current_user.id)
    if not success:
        raise ApiError(
            code="not_found_or_forbidden",
            message="Feature not found or you don't have permission to delete it",
            status=status.HTTP_404_NOT_FOUND,
        )
    return None


@features_router.post("/{feature_id}/vote", response_model=schemas.VoteResponse)
def vote_feature(
    feature_id: int,
    vote: schemas.VoteCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_feature = crud.get_feature(db, feature_id=feature_id)
    if db_feature is None:
        raise ApiError(
            code="not_found",
            message="Feature not found",
            status=status.HTTP_404_NOT_FOUND,
        )

    if vote.value not in [1, -1]:
        raise ApiError(
            code="validation_error",
            message="Vote value must be 1 (upvote) or -1 (downvote)",
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    db_vote = crud.create_vote(db, feature_id=feature_id, user_id=current_user.id, value=vote.value)
    return db_vote
