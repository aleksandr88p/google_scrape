from file_for_api import *



app = FastAPI()
my_api = MyAPI()

@app.get("/")
async def root():
    return {"message": "Hello to google scraper"}


@app.get("/process_string/{keyword}/{country}")
async def process_string(keyword: str, country: str):
    global successful_requests

    while True:
        content = await my_api.make_request(keyword, country)
        result_json = await my_api.make_json(content)

        if result_json['params']:
            successful_requests += 1
            return result_json

        await asyncio.sleep(0.1)

@app.on_event("startup")
async def startup_event():
    app.state.executor = ThreadPoolExecutor(10)


@app.get("/stats")
async def stats():
    global successful_requests
    return {"successful_requests": successful_requests}