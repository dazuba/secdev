from typing import List, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_password_hash


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_feature(db: Session, feature: schemas.FeatureCreate, owner_id: int) -> models.Feature:
    db_feature = models.Feature(title=feature.title, desc=feature.desc, owner_id=owner_id)
    db.add(db_feature)
    db.commit()
    db.refresh(db_feature)
    return db_feature


def get_feature(db: Session, feature_id: int) -> Optional[models.Feature]:
    return db.query(models.Feature).filter(models.Feature.id == feature_id).first()


def get_features(db: Session, skip: int = 0, limit: int = 100) -> List[models.Feature]:
    features = db.query(models.Feature).offset(skip).limit(limit).all()
    return features


def update_feature(
    db: Session, feature_id: int, feature_update: schemas.FeatureUpdate, owner_id: int
) -> Optional[models.Feature]:
    db_feature = db.query(models.Feature).filter(models.Feature.id == feature_id).first()
    if not db_feature:
        return None
    if db_feature.owner_id != owner_id:
        return None
    if feature_update.title is not None:
        db_feature.title = feature_update.title
    if feature_update.desc is not None:
        db_feature.desc = feature_update.desc
    db.commit()
    db.refresh(db_feature)
    return db_feature


def delete_feature(db: Session, feature_id: int, owner_id: int) -> bool:
    db_feature = db.query(models.Feature).filter(models.Feature.id == feature_id).first()
    if not db_feature:
        return False
    if db_feature.owner_id != owner_id:
        return False
    db.delete(db_feature)
    db.commit()
    return True


def get_top_features(db: Session, limit: int = 10) -> List[models.Feature]:
    vote_count = func.coalesce(func.sum(models.Vote.value), 0).label("vote_count")
    features = (
        db.query(models.Feature, vote_count)
        .outerjoin(models.Vote)
        .group_by(models.Feature.id)
        .order_by(desc(vote_count))
        .limit(limit)
        .all()
    )
    return [feature[0] for feature in features]


def get_vote_count(db: Session, feature_id: int) -> int:
    result = (
        db.query(func.coalesce(func.sum(models.Vote.value), 0))
        .filter(models.Vote.feature_id == feature_id)
        .scalar()
    )
    return int(result) if result else 0


def create_vote(db: Session, feature_id: int, user_id: int, value: int) -> Optional[models.Vote]:
    existing_vote = (
        db.query(models.Vote)
        .filter(models.Vote.feature_id == feature_id, models.Vote.user_id == user_id)
        .first()
    )
    if existing_vote:
        existing_vote.value = value
        db.commit()
        db.refresh(existing_vote)
        return existing_vote

    db_vote = models.Vote(feature_id=feature_id, user_id=user_id, value=value)
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)
    return db_vote


def get_user_vote(db: Session, feature_id: int, user_id: int) -> Optional[models.Vote]:
    return (
        db.query(models.Vote)
        .filter(models.Vote.feature_id == feature_id, models.Vote.user_id == user_id)
        .first()
    )
