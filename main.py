from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routes import news, delivery, transport, auth, tram, cars, industrial_stores, delivers, pharmacy

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
app.include_router(industrial_stores.router)
app.include_router(delivers.router)
app.include_router(pharmacy.router)


@app.get("/")
async def root():
    return JSONResponse({
        "message": "Welcome to Kotlin Projects!"
    })


@app.post("/")
async def json_test(request: Request):
    request_body = await request.body()

    print({
        "message": "All worked!",
        "headers": request.headers,
        "data": request_body
    })

    return JSONResponse({
        "message": "All worked!",
    })
