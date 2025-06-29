import uvicorn
import asyncio
import sys
from server import app

async def main():
    config = uvicorn.Config("server:app", port=31987, host="0.0.0.0", http="auto")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nСервер остановлен пользователем.")
        sys.exit(0)
    except Exception as e:
        print(f"Ошибка при запуске: {e}")
        sys.exit(1)
