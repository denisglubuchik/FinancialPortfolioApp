from typing import Annotated
from fastapi import Depends

from back.portfolio_service.utils.uow import IUnitOfWork, UnitOfWork

UOWDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]
