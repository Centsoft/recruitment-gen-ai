from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from openai import AsyncAzureOpenAI
from app.core.config import settings
from app.api.endpoints import query
from qdrant_client import AsyncQdrantClient

load_dotenv()


def initialize_async_openai_deployment(deployment_name: str):
    api_key = settings.AZURE_OPENAI_API_KEY.get_secret_value()
    azure_endpoint = settings.AZURE_OPENAI_ENDPOINT
    api_version = settings.AZURE_API_VERSION

    client = AsyncAzureOpenAI(
        azure_deployment=deployment_name,
        api_version=api_version,
        api_key=api_key,
        azure_endpoint=azure_endpoint,
    )
    return client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Set up sync Qdrant client and vector store
    qdrant_client = AsyncQdrantClient(
        url=settings.QDRANT_URL if settings.QDRANT_URL else None,
        port=int(settings.QDRANT_PORT) if settings.QDRANT_PORT is not None else None,
        timeout=30,
        api_key=settings.QDRANT_API_KEY.get_secret_value()
        if settings.QDRANT_API_KEY
        else None,
    )

    # Store these in the app state
    app.state.qdrant_client = qdrant_client
    app.state.openai_async_client = initialize_async_openai_deployment(
        deployment_name="gpt-4o-copilot"
    )
    app.state.openai_async_embedder = initialize_async_openai_deployment(
        deployment_name="text-embedding-3-large"
    )

    yield
    # ... cleanup code ...
    # The code after yield runs during application shutdown
    qdrant_client.close()


def create_app():
    print("\n\n")
    print("███╗   ███╗██╗███╗   ██╗██████╗  ██████╗██████╗  █████╗ ███████╗████████╗")
    print("████╗ ████║██║████╗  ██║██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝")
    print("██╔████╔██║██║██╔██╗ ██║██║  ██║██║     ██████╔╝███████║█████╗     ██║   ")
    print("██║╚██╔╝██║██║██║╚██╗██║██║  ██║██║     ██╔══██╗██╔══██║██╔══╝     ██║   ")
    print("██║ ╚═╝ ██║██║██║ ╚████║██████╔╝╚██████╗██║  ██║██║  ██║██║        ██║   ")
    print("╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝        ╚═╝   ")
    print("████████╗███████╗███████╗████████╗  █████╗ ██████╗ ██╗")
    print("╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝ ██╔══██╗██╔══██╗██║")
    print("   ██║   █████╗  ███████╗   ██║    ███████║██████╔╝██║")
    print("   ██║   ██╔══╝  ╚════██║   ██║    ██╔══██║██╔═══╝ ██║")
    print("   ██║   ███████╗███████║   ██║    ██║  ██║██║     ██║")
    print("   ╚═╝   ╚══════╝╚══════╝   ╚═╝    ╚═╝  ╚═╝╚═╝     ╚═╝ v%s" % "0.1.0")
    print("\n")
    print("| 📚 Documentation 📚")
    print("| redoc: http://0.0.0.0:8003/redoc")
    print("| swagger: http://0.0.0.0:8003/docs")
    print("\n\n")

    app = FastAPI(
        title="Mindcraft Test API",
        description="This is a test API for recruitment purposes",
        lifespan=lifespan,
        version="0.1.0",
    )
    app.include_router(query.router, prefix=settings.API_V1_STR)
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003, reload=True)
