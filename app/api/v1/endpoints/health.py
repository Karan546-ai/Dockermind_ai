# app/api/v1/endpoints/health.py

from fastapi import APIRouter, status


class HealthEndpoints:
    def __init__(self):
        self.router = APIRouter(tags=["Health"])
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(
            "/health",
            self.get_health_status,
            methods=["GET"],
            summary="Check API Health",
            status_code=status.HTTP_200_OK,
        )

    def get_health_status(self):
        """Endpoint to check if the API is running and healthy."""
        return {"status": "ok"}
