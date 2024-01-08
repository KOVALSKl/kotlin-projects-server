from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routes import news, delivery, transport, auth, tram, cars

app = FastAPI(
    title="Kotlin Projects Server",
    description="",
    version="0.0.1"
)

allow_all = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_all,
    allow_credentials=True,
    allow_methods=allow_all,
    allow_headers=allow_all
)

app.include_router(news.router)
app.include_router(delivery.router)
app.include_router(transport.router)
app.include_router(auth.router)
app.include_router(tram.router)
app.include_router(cars.router)


@app.get("/")
async def root():
    return JSONResponse({
        "message": "Welcome to Kotlin Projects!"
    })
