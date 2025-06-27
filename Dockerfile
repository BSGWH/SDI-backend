# 1. Use a slim Python base
FROM python:3.10-slim

# 2. Create app directory
WORKDIR /usr/src/app

# 3. Install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 4. Copy source
COPY ./app ./app

# 5. Copy env (for local/dev testing only – in prod inject via docker-compose or CI/CD)
COPY .env .

# 6. Expose port and launch uvicorn
EXPOSE 8000

