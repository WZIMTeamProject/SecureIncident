# 📋 Dokumentacja Zmian - Backend Database Models

Data: 2 maja 2026

## 📝 Opis Ogólny

Stworzono kompletną warstwę modeli bazy danych dla aplikacji **Secure Incident** przy użyciu SQLAlchemy ORM.

---

## 📂 Struktura Plików

### `backend/db/base.py`
- **Cel:** Inicjalizacja bazy deklaratywnej SQLAlchemy
- **Zawiera:** `Base` - klasa bazowa dla wszystkich modeli
- **Import:** `from sqlalchemy.orm import declarative_base`

---

## 🗄️ Modele Bazy Danych

### 1. **User** (`backend/db/models/user.py`)
Reprezentuje użytkownika systemu.

**Pola:**
- `id` (PK) - identyfikator
- `organization_id` (FK) - przynależność do organizacji
- `first_name`, `last_name` - imię i nazwisko
- `login` - unikalny login
- `mail` - unikalny email
- `password` - zahaszowane hasło (bcrypt)
- `created_at`, `updated_at` - timestampy

**Relacje:**
- `organization` - wiele-do-jednego
- `owned_organizations` - użytkownik jako właściciel organizacji
- `owned_projects` - użytkownik jako właściciel projektów
- `user_projects` - projekty użytkownika
- `incidents` - zgłoszenia zgłoszone
- `assigned_incidents` - zgłoszenia przypisane do rozwiązania
- `incident_logs` - historia działań
- `comments` - komentarze

---

### 2. **Organization** (`backend/db/models/organization.py`)
Reprezentuje organizację.

**Pola:**
- `id` (PK) - identyfikator
- `org_owner_id` (FK) - właściciel organizacji
- `name` - nazwa organizacji
- `description` - opis
- `created_at`, `updated_at` - timestampy

**Relacje:**
- `owner` - właściciel (User)
- `users` - użytkownicy w organizacji
- `projects` - projekty organizacji

---

### 3. **Project** (`backend/db/models/project.py`)
Reprezentuje projekt w organizacji.

**Pola:**
- `id` (PK) - identyfikator
- `project_owner_id` (FK) - właściciel projektu
- `organization_id` (FK) - organizacja, do której należy projekt
- `name` - nazwa projektu
- `created_at`, `updated_at` - timestampy

**Relacje:**
- `owner` - właściciel (User)
- `organization` - organizacja
- `user_projects` - użytkownicy w projekcie
- `roles` - role w projekcie
- `incidents` - zgłoszenia w projekcie
- `categories` - kategorie w projekcie

---

### 4. **Role** (`backend/db/models/role.py`)
Reprezentuje rolę użytkownika w projekcie.

**Pola:**
- `id` (PK) - identyfikator
- `project_id` (FK) - projekt
- `name` - nazwa roli (np. "Developer", "Manager")
- `can_write_tickets` - prawo do tworzenia zgłoszeń
- `can_help` - prawo do pomocy w rozwiązywaniu
- `can_assign_help` - prawo do przypisywania pomocy
- `can_make_roles` - prawo do tworzenia ról
- `can_change_roles` - prawo do zmiany ról
- `can_assign_people_to_project` - prawo do dodawania użytkowników
- `created_at`, `updated_at` - timestampy

**Relacje:**
- `project` - projekt
- `user_projects` - przypisania użytkowników

---

### 5. **UserProject** (`backend/db/models/user_project.py`)
Reprezentuje relację wiele-do-wielu między User a Project.

**Pola:**
- `user_id` (PK, FK) - użytkownik
- `project_id` (PK, FK) - projekt
- `role_id` (FK) - rola użytkownika w projekcie
- `created_at`, `updated_at` - timestampy

**Relacje:**
- `user` - użytkownik
- `project` - projekt
- `role` - rola przypisana

---

### 6. **Incident** (`backend/db/models/incident.py`)
Reprezentuje zgłoszenie/problem.

**Pola:**
- `id` (PK) - identyfikator
- `user_id` (FK) - zgłaszający
- `project_id` (FK) - projekt
- `helper_id` (FK, nullable) - osoba rozwiązująca
- `title` - tytuł zgłoszenia
- `status` - status (Open, In Progress, Resolved, Closed)
- `priority_level` - priorytet (1-5)
- `description` - opis
- `creation_date` - data utworzenia
- `closing_date` - data zamknięcia (nullable)
- `updated_at` - ostatnia aktualizacja

**Enum:**
- `IncidentStatus` - typy statusów

**Relacje:**
- `reporter` - zgłaszający (User)
- `helper` - osoba rozwiązująca (User)
- `project` - projekt
- `comments` - komentarze
- `logs` - historia zmian
- `categories` - kategorie (many-to-many)

---

### 7. **Comment** (`backend/db/models/comment.py`)
Reprezentuje komentarz do zgłoszenia.

**Pola:**
- `id` (PK) - identyfikator
- `incident_id` (FK) - zgłoszenie
- `user_id` (FK) - autor komentarza
- `content` - treść komentarza
- `created_at`, `updated_at` - timestampy

**Relacje:**
- `incident` - zgłoszenie
- `user` - autor

---

### 8. **IncidentLog** (`backend/db/models/incident_log.py`)
Reprezentuje zdarzenie w historii zgłoszenia.

**Pola:**
- `id` (PK) - identyfikator
- `incident_id` (FK) - zgłoszenie
- `person_id` (FK) - osoba, która dokonała zmiany
- `type` - typ zdarzenia (priority_change, comment, helper_added, status_change, itd.)
- `comment` - opis zmiany
- `date` - data zdarzenia

**Enum:**
- `LogType` - typy zdarzeń

**Relacje:**
- `incident` - zgłoszenie
- `person` - osoba, która dokonała zmiany

---

### 9. **Category** (`backend/db/models/category.py`)
Reprezentuje kategorię zgłoszeń.

**Pola:**
- `id` (PK) - identyfikator
- `project_id` (FK) - projekt
- `name` - nazwa kategorii
- `description` - opis
- `created_at`, `updated_at` - timestampy

**Tabele Asocjacyjne:**
- `helper_category` - łączy User (helper) z Category
- `incident_category` - łączy Incident z Category

**Relacje:**
- `project` - projekt
- `incidents` - zgłoszenia (many-to-many)

---

### 10. **__init__.py** (`backend/db/models/__init__.py`)
Eksportuje wszystkie modele i enums dla łatwego importu.

**Eksportuje:**
- User, Organization, Project, Role, UserProject
- Incident, IncidentStatus
- Comment
- IncidentLog, LogType
- Category

---

## 📦 Aktualizacje `requirements.txt`

Dodano następujące pakiety:

| Pakiet | Wersja | Cel |
|--------|--------|-----|
| sqlalchemy | 2.0.23 | ORM dla bazy danych |
| pydantic-settings | 2.1.0 | Zmienne konfiguracyjne |
| python-jose | 3.3.0 | JWT authentication |
| passlib | 1.7.4 | Hashing haseł |
| bcrypt | 4.1.1 | Bezpieczne haszowanie |
| python-multipart | 0.0.6 | Obsługa formularzy |
| python-dotenv | 1.0.0 | Zmienne .env |
| PyMySQL | 1.1.0 | Driver MySQL |
| psycopg2-binary | 2.9.9 | Driver PostgreSQL |
| alembic | 1.12.1 | Database migrations |
| pytest | 7.4.3 | Testowanie |
| pytest-asyncio | 0.21.1 | Testy asynchroniczne |
| httpx | 0.25.2 | HTTP client |
| PyJWT | 2.12.1 | JWT token handling |

---

## 🔗 Relacje między modelami

```
User
├── Organization (as owner)
├── Organization (as member)
├── Project (as owner)
├── UserProject → Project (role assignment)
├── Incident (as reporter)
├── Incident (as helper)
├── IncidentLog
└── Comment

Organization
├── User (owner)
├── User (members)
└── Project

Project
├── User (owner)
├── Organization
├── UserProject
├── Role
├── Incident
└── Category

Role
├── Project
└── UserProject

UserProject
├── User
├── Project
└── Role

Incident
├── User (reporter)
├── User (helper)
├── Project
├── Comment
├── IncidentLog
└── Category (many-to-many)

Comment
├── Incident
└── User

IncidentLog
├── Incident
└── User

Category
├── Project
└── Incident (many-to-many)
```

---

## ✨ Cechy Implementacji

✅ **Proper Foreign Keys** - wszystkie relacje mają zdefiniowane FK
✅ **Cascade Delete** - usunięcie nadrzędnego rekordu kasuje powiązane
✅ **Timestamps** - każdy model ma `created_at` i `updated_at`
✅ **Enums** - typy statusów i zdarzeń zdefiniowane w kodzie
✅ **Many-to-Many** - obsługa relacji wielu-do-wielu
✅ **Session Management** - dependency injection dla FastAPI
✅ **Environment Configuration** - konfiguracja przez zmienne .env

---

## 🔧 Użycie

### Import modeli:
```python
from backend.db.models import User, Project, Incident
from backend.db.session import get_db
```

### W route'ach FastAPI:
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.db.models import User

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### Tworzenie tabel:
```python
from backend.db.base import Base
from backend.db.session import engine

# Utwórz wszystkie tabele
Base.metadata.create_all(bind=engine)
```

---
