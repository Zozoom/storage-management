from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_frontend_api_url_is_configured_at_build_time():
    compose = (ROOT / "docker-compose.yml").read_text()
    dockerfile = (ROOT / "frontend/Dockerfile").read_text()

    assert (
        "  frontend:\n"
        "    build:\n"
        "      context: ./frontend\n"
        "      args:\n"
        "        NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-http://localhost:8000}\n"
    ) in compose
    assert "ARG NEXT_PUBLIC_API_URL=http://localhost:8000" in dockerfile
    assert "ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL" in dockerfile
