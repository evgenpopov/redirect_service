# Redirect Service with Analytics

Django, PostgreSQL, Redis, Docker + Makefile

## Dev notes

- **Custom User model** - make it blank to avoid problems in the future (migration)
- **Redis cache** - cached with a configurable TTL
- **Analytics** - feature that no need extra resources

## Quick start

```bash
make up
```
http://localhost:8000

## First-time setup

```bash
make createsuperuser
```
http://localhost:8000/admin/ - login

## API Documentation

- http://localhost:8000/api/docs/

 - http://localhost:8000/api/redoc/

- http://localhost:8000/api/schema/


## Makefile commands

```
make build          
make up             
make down           
make logs          
make migrate        
make makemigrations 
make shell          
make createsuperuser
make install
```

## API Endpoints

### Authentication

| Method | Path | Description                     |
|---|---|---------------------------------|
| `POST` | `/retrieve-token/` | access + refresh JWT tokens     |
| `POST` | `/retrieve-token/refresh/` | refresh an expired access token |

```bash
curl -X POST http://127.0.0.1:8000/retrieve-token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "popov", "password": "popov"}'
```

### Redirect Rules

| Method | Path | Description                  |
|---|---|------------------------------|
| `GET` | `/url/` | get list your redirect rules |
| `POST` | `/url/` | create a new redirect rule   |
| `GET` | `/url/{id}/` | get a specific rule          |
| `PATCH` | `/url/{id}/` | update a rule                |
| `DELETE` | `/url/{id}/` | delete a rule                |

```bash
curl -X POST http://127.0.0.1:8000/url/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"redirect_url": "https://google.com", "is_private": false}'

curl -X PATCH http://127.0.0.1:8000/url/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"is_private": true}'
```

### Redirects

| Method | Path | Auth |
|---|---|--------------|
| `GET` | `/redirect/public/{id}/` | -            |
| `GET` | `/redirect/private/{id}/` | Bearer       |

`302 Found` on success 

`404 Not Found` if doesn't exist or privacy error

