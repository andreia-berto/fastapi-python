from pydantic import BaseModel, ConfigDict


class UserPostin(BaseModel):
    body: str


class UserPost(UserPostin):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CommentIn(BaseModel):
    body: str
    post_id: int


class Comment(CommentIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class UserPostWithComments(BaseModel):
    post: UserPost
    comments: list[Comment]
