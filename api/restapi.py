from fastapi import FastAPI


class RestAPI:
    @classmethod
    def create_app(cls) -> FastAPI:
        app = FastAPI()
        app.include_router()
        return app
