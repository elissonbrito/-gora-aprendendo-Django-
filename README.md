# Ágora Django Fullstack

Projeto fullstack base do Ágora com:
- Backend: Django + DRF + JWT
- Frontend: React + Vite
- PostgreSQL como banco principal
- MongoDB para auditoria
- Redis para cache simples

## Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Login inicial:
- email: admin@agora.local
- senha: 123456

## Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Observações
- MongoDB e Redis são opcionais no boot: se não estiverem disponíveis, o sistema continua rodando.
- O projeto é uma base funcional e extensível, pronta para evoluir.
