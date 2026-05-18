from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, oauth2
from ..database import get_db
from typing import Optional
from sqlalchemy import func

router = APIRouter(
    prefix = "/posts",
    tags = ["Posts"]
)

@router.get("/", response_model=List[schemas.PostVoteResponse])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip:int = 0, search: Optional[str] = ""):
    # cursor.execute("SELECT * FROM posts;")
    # all_posts = cursor.fetchall()
    # all_posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    result = []

    for post, vote in posts:
        result.append({
            "post": post,
            "votes": vote
        })
    return result

@router.get("/{id}", response_model=schemas.PostVoteResponse)
def get_post(id: int, response: Response, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # for post in my_posts:
    #     if post["id"] == id:
    #         return {"post": post}
    # response.status_code = status.HTTP_404_NOT_FOUND
    # return {"message": "Id does not exist"}
    # cursor.execute("SELECT * FROM posts WHERE id = %s;", (id,))
    # one_post = cursor.fetchone()

    one_post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    
    if not one_post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                        detail = f"Post with ID : {id} does not exist!")
    
    post, votes = one_post    
    return {"post": post, "votes": votes}
    

@router.post("/", status_code = status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # post_dict = post.model_dump()
    # post_dict["id"] = randrange(1, 10000000)
    # my_posts.append(post_dict)

        # cursor.execute("INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *", 
        #             (post.title, post.content, post.published))
        # new_post = cursor.fetchone()
        # conn.commit()

    # new_post = models.Post(title = post.title, content = post.content, published = post.published)
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.delete("/{id}")
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
        # for index, dict in enumerate(my_posts):
        #     if dict["id"] == id:
        #         my_posts.pop(index)
        #         return {"message": f"Successfully deleted post with ID : {id}"}
    
    # cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *;", (id,))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"Post with ID : {id} not found!")

    if post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action!")
    
    post.delete(synchronize_session=False)
    db.commit()

    return {"status" : "deletion_successful"}

@router.put("/{id}", status_code = status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostUpdate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # for current_post in my_posts:
    #     if current_post["id"] == id:
    #         current_post["title"] = post.title
    #         current_post["content"] = post.content
    #         return {"message": f"Successfully updated post with ID : {id}"}

    # cursor.execute("UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *;", 
    #                (post.title, post.content, post.published, id))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    new_post = post_query.first()

    if new_post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"Post with ID : {id} not found!")

    if new_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action!")    
    
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return post_query.first()