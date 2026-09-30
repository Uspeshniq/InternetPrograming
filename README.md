# Quiz Conquest

Учебен проект по Интернет програмиране — Django REST Framework backend и React + Vite frontend.

## Структура

```text
├── backend/          Django проект (config) + приложения accounts, questions
└── frontend/         React + Vite
```

## Backend

### Инсталиране

Windows PowerShell:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Linux, macOS или WSL:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Migrations

```bash
python backend/manage.py migrate
```

### Зареждане на банката с въпроси

```bash
python backend/manage.py loaddata questions/question_bank.json
```

Fixture файлът съдържа 6 категории, 12 choice въпроса с 48 възможни отговора
и 12 numeric въпроса.

Проверка на заредените данни:

```bash
python backend/manage.py shell
```

```python
from questions.models import Category, ChoiceQuestion, NumericQuestion

Category.objects.count()         # 6
ChoiceQuestion.objects.count()   # 12
NumericQuestion.objects.count()  # 12
```

### Django Admin

```bash
python backend/manage.py createsuperuser
python backend/manage.py runserver
```

Административният панел е достъпен на `http://127.0.0.1:8000/admin/`.

### Тестове

```bash
python backend/manage.py test
```

Тестове само за банката с въпроси:

```bash
python backend/manage.py test questions
```

### Development сървър

```bash
python backend/manage.py runserver
```

Достъпен на `http://127.0.0.1:8000/`.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Достъпен на `http://localhost:5173/`.

## Приложения

| Приложение | Предназначение |
|---|---|
| `accounts` | Custom user модел (`AUTH_USER_MODEL`) |
| `questions` | Категории, choice въпроси, numeric въпроси, възможни отговори |

## Milestones

| Tag | Описание |
|---|---|
| `m0-setup` | Initial project setup |
| `m2-question-bank` | Question bank |
