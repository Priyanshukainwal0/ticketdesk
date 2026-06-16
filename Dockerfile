# ── TicketDesk Dockerfile ─────────────────────────────────────────────────
#
# Build:  docker build -t ticketdesk .
# Run:    docker run -p 8000:8000 -e DB_PATH=/data/td.db ticketdesk
#
# Layer strategy: dependencies are installed BEFORE the application code is
# copied.  This means "pip install" is only re-run when requirements.txt
# changes, not on every code edit — dramatically faster rebuilds in CI.
# ──────────────────────────────────────────────────────────────────────────

# 1. Use the official slim Python image to keep the final image small
#    (~150 MB vs ~900 MB for the full image).
FROM python:3.12-slim

# 2. Create a non-root system user and group.
#    Running as root inside a container is a security risk; most cloud
#    runtimes (Cloud Run, ECS, k8s) expect non-root workloads.
RUN addgroup --system appgroup \
 && adduser  --system --ingroup appgroup appuser

# 3. Set the working directory inside the container.
WORKDIR /app

# 4. Copy ONLY the requirements file first (not the whole repo).
#    Docker caches each layer; this layer is invalidated only when
#    requirements.txt changes, keeping pip installs off the critical path.
COPY requirements.txt .

# 5. Install Python dependencies.
#    --no-cache-dir  → don't write the pip download cache to the image layer.
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the application source into the image.
#    .dockerignore excludes tests/, .git/, *.db, etc.
COPY app/ ./app/

# 7. Give the non-root user ownership of the working directory.
RUN chown -R appuser:appgroup /app

# 8. Drop privileges — all subsequent commands run as appuser.
USER appuser

# 9. Tell Docker (and cloud platforms) which port the app listens on.
#    This is metadata only; actual port mapping is done at `docker run -p`.
EXPOSE 8000

# 10. Liveness / readiness probe used by Docker and Kubernetes.
#     Checks the /health endpoint every 30 s; fails after 3 retries.
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c \
        "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# 11. Start the API with uvicorn.
#     --host 0.0.0.0 binds to all interfaces (required inside a container).
#     DB_PATH is supplied at runtime via -e or docker-compose environment:.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
