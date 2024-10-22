from fastapi import APIRouter

from back.portfolio_service.dependencies import UOWDep
from back.portfolio_service.schemas.users import SUserCreate
from back.portfolio_service.services.users import UsersService

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/")
async def add_user(new_user: SUserCreate, uow: UOWDep) -> int:
    user_id = await UsersService().add_user(uow, new_user)
    return user_id