########################################
# Stage 1 — Build Angular frontend
########################################
FROM node:25.2.1 AS frontend-build

WORKDIR /app
COPY dna-visualizer/package*.json ./
RUN npm install
COPY dna-visualizer/ .
RUN npm run build


########################################
# Stage 2 — Build FastAPI backend (venv)
########################################
FROM python:3.12 AS backend-build

WORKDIR /backend

# Create virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
RUN chmod 777 src/format_molecule.sh


########################################
# Stage 3 — Runtime (python + nginx)
########################################
FROM python:3.12-slim

# Install nginx + supervisor
RUN apt-get update && \
    apt-get install -y nginx supervisor && \
    rm -rf /var/lib/apt/lists/*

# ---- Copy backend venv + code ----
COPY --from=backend-build /venv /venv
COPY --from=backend-build /backend /backend
ENV PATH="/venv/bin:$PATH"

# ---- Frontend ----
COPY --from=frontend-build /app/dist/dna-visualizer/browser /usr/share/nginx/html

# ---- Configs ----
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80

RUN apt-get update && \
    apt-get install -y nginx supervisor bash && \
    rm -rf /var/lib/apt/lists/*

CMD ["/usr/bin/supervisord", "-n"]
