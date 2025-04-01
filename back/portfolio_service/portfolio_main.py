from fastapi import FastAPI, Request

from back.portfolio_service.message_broker.rabbitmq import rabbit_broker
from back.portfolio_service.routers import all_routers
from back.portfolio_service.utils.uow import UnitOfWork

from back.portfolio_service.services.portfolio import PortfolioService

portfolio_app = FastAPI()

for router in all_routers:
    portfolio_app.include_router(router)


@portfolio_app.middleware("http")
async def update_portfolio_value_middleware(request: Request, call_next):
    if request.url.path in ["/docs", "/openapi.json"]:
        return await call_next(request)

    response = await call_next(request)

    user_id = request.headers.get("X-User-ID")

    if user_id:
        try:
            user_id = int(user_id)
            portfolio_id = await PortfolioService().get_portfolio(UnitOfWork(), user_id=user_id)
            if portfolio_id:
                await PortfolioService().update_portfolio_value(UnitOfWork(), portfolio_id.id)
        except ValueError:
            print(f"Некорректный user_id: {user_id}")

    return response


@portfolio_app.on_event("startup")
async def start_rabbit():
    try:
        await rabbit_broker.start()
    except Exception as e:
        print(e)


@portfolio_app.on_event("shutdown")
async def stop_rabbit():
    await rabbit_broker.stop()
