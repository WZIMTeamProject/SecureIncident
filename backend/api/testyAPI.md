# Instrukcja_Endpointów.md

# 1. Przygotowanie czystego środowiska Docker

## Usunięcie starych kontenerów i danych

W katalogu projektu uruchom:

```bash
docker compose down -v
```

Parametr `-v` usuwa również wolumeny PostgreSQL.

Następnie sprawdź:

```bash
docker ps -a
docker volume ls
```

Jeżeli nadal istnieją wolumeny projektu:

```bash
docker volume rm NAZWA_WOLUMENU
```

## Uruchomienie czystego środowiska

```bash
docker compose up --build
```

Po uruchomieniu:

```bash
docker ps
```

Powinieneś widzieć:

* backend
* postgres
* mailpit (jeżeli używasz)

## Sprawdzenie migracji

Backend uruchamia Alembic automatycznie podczas startu.

W logach backendu powinno pojawić się:

```text
Running database migrations...
Database migrations completed successfully.
```

## Swagger

Otwórz:

```text
http://localhost:8000/docs
```

Wszystkie poniższe testy wykonuj ze Swaggera.

---

# 2. Przygotowanie użytkowników testowych

## Rejestracja użytkownika nr 1

POST

```text
/api/auth/register
```

Body:

```json
{
  "first_name": "Jan",
  "last_name": "Kowalski",
  "username": "owner",
  "email": "owner@test.pl",
  "password": "Password123!"
}
```

Oczekiwany wynik:

```http
201 Created
```

Zapamiętaj ID.

---

## Rejestracja użytkownika nr 2

POST

```text
/api/auth/register
```

Body:

```json
{
  "first_name": "Adam",
  "last_name": "Nowak",
  "username": "member",
  "email": "member@test.pl",
  "password": "Password123!"
}
```

Oczekiwany wynik:

```http
201 Created
```

---

## Logowanie użytkownika owner

POST

```text
/api/auth/login
```

Body:

```json
{
  "username": "owner",
  "password": "Password123!",
  "remember_user": false
}
```

Oczekiwany wynik:

```http
200 OK
```

Skopiuj:

```json
access_token
```

Kliknij:

```text
Authorize
```

Wklej:

```text
Bearer TOKEN
```

---

# ORGANIZATION

# Endpoint: POST /api/organization

## Test poprawny

Body:

```json
{
  "name": "Test Organization",
  "description": "Organizacja testowa"
}
```

Oczekiwany wynik:

```http
201 Created
```

Odpowiedź:

```json
{
  "id": "uuid"
}
```

Zapisz organization_id.

---

## Test bez tokenu

Usuń autoryzację.

Wykonaj ponownie.

Oczekiwany wynik:

```http
401 Unauthorized
```

---

## Test drugi raz

Użytkownik owner należy już do organizacji.

Ponownie wykonaj request.

Oczekiwany wynik:

```http
409 Conflict
```

---

# Endpoint: GET /api/organization

## Test poprawny

Oczekiwany wynik:

```http
200 OK
```

Przykład:

```json
{
  "id": "...",
  "name": "Test Organization",
  "description": "Organizacja testowa"
}
```

---

## Test bez tokenu

Oczekiwany wynik:

```http
401 Unauthorized
```

---

# Endpoint: POST /api/organization/invites

## Test poprawny

Body:

```json
{
  "expires_at": null,
  "max_uses": 5
}
```

Oczekiwany wynik:

```http
201 Created
```

Odpowiedź:

```json
{
  "token": "...",
  "invite_url": "..."
}
```

Zapisz token.

---

## Test bez tokenu

Oczekiwany wynik:

```http
401 Unauthorized
```

---

## Test użytkownikiem niebędącym właścicielem

Zaloguj się jako member.

Wykonaj endpoint.

Oczekiwany wynik:

```http
403 Forbidden
```

---

# Endpoint: POST /api/organization/join

## Test poprawny

Zaloguj się jako member.

Body:

```json
{
  "token": "TOKEN_ZAPROSZENIA"
}
```

Oczekiwany wynik:

```http
204 No Content
```

---

## Test ponownego dołączenia

Ponownie wykonaj endpoint.

Oczekiwany wynik:

```http
409 Conflict
```

---

## Test błędnego tokenu

```json
{
  "token": "abcd"
}
```

Oczekiwany wynik:

```http
400 Bad Request
```

---

# PROJECTS

# Endpoint: POST /api/projects

## Test projektu organizacyjnego

Body:

```json
{
  "name": "Projekt A",
  "description": "Opis projektu",
  "scope": "ORGANIZATION"
}
```

Oczekiwany wynik:

```http
201 Created
```

Zapisz project_id.

---

## Test bez tokenu

Oczekiwany wynik:

```http
401 Unauthorized
```

---

## Test pustej nazwy

```json
{
  "name": "",
  "description": "Opis",
  "scope": "ORGANIZATION"
}
```

Oczekiwany wynik:

```http
422 Unprocessable Entity
```

---

# Endpoint: GET /api/projects

## Test poprawny

Oczekiwany wynik:

```http
200 OK
```

Powinna pojawić się lista projektów użytkownika.

---

## Test filtrowania

Query:

```text
?scope=ORGANIZATION
```

Oczekiwany wynik:

```http
200 OK
```

---

# Endpoint: GET /api/projects/{project_id}

## Test poprawny

Wstaw zapisany project_id.

Oczekiwany wynik:

```http
200 OK
```

---

## Test nieistniejącego projektu

Losowy UUID.

Oczekiwany wynik:

```http
404 Not Found
```

---

# Endpoint: PATCH /api/projects/{project_id}

## Test poprawny

Body:

```json
{
  "name": "Projekt A Updated",
  "description": "Nowy opis"
}
```

Oczekiwany wynik:

```http
204 No Content
```

---

## Test użytkownikiem niewłaścicielem

Zaloguj się jako member.

Oczekiwany wynik:

```http
403 Forbidden
```

---

# Endpoint: GET /api/projects/{project_id}/members

## Test poprawny

Oczekiwany wynik:

```http
200 OK
```

Lista członków projektu.

---

## Test użytkownikiem spoza projektu

Oczekiwany wynik:

```http
403 Forbidden
```

---

# Endpoint: POST /api/projects/{project_id}/members

## Test poprawny

Najpierw pobierz:

```text
member user_id
role_id
```

Body:

```json
{
  "user_id": "USER_UUID",
  "role_id": "ROLE_UUID"
}
```

Oczekiwany wynik:

```http
204 No Content
```

---

## Test dodania drugi raz

Oczekiwany wynik:

```http
409 Conflict
```

---

## Test nieistniejącego użytkownika

Oczekiwany wynik:

```http
404 Not Found
```

---

# Endpoint: PATCH /api/projects/{project_id}/members/{user_id}/role

## Test poprawny

Body:

```json
{
  "role_id": "NOWA_ROLA_UUID"
}
```

Oczekiwany wynik:

```http
204 No Content
```

---

## Test nieistniejącej roli

Oczekiwany wynik:

```http
404 Not Found
```

---

# ROLES

# Endpoint: GET /api/projects/{project_id}/roles

## Test poprawny

Oczekiwany wynik:

```http
200 OK
```

Lista ról.

Powinna zawierać:

```text
Owner
```

---

## Test bez członkostwa

Oczekiwany wynik:

```http
403 Forbidden
```

---

# Endpoint: POST /api/projects/{project_id}/roles

## Test poprawny

Body:

```json
{
  "name": "Developer",
  "permissions": {
    "can_write_tickets": true,
    "can_help": true,
    "can_assign_help": false,
    "can_change_status": false,
    "can_make_roles": false,
    "can_change_roles": false,
    "can_assign_people_to_project": false
  }
}
```

Oczekiwany wynik:

```http
201 Created
```

Zapisz role_id.

---

## Test pustej nazwy

```json
{
  "name": "",
  "permissions": {
    "can_write_tickets": true,
    "can_help": true,
    "can_assign_help": false,
    "can_change_status": false,
    "can_make_roles": false,
    "can_change_roles": false,
    "can_assign_people_to_project": false
  }
}
```

Oczekiwany wynik:

```http
422 Unprocessable Entity
```

---

## Test użytkownikiem niewłaścicielem

Oczekiwany wynik:

```http
403 Forbidden
```

---

# Endpoint: GET /api/projects/{project_id}/roles/{role_id}

## Test poprawny

Oczekiwany wynik:

```http
200 OK
```

Powinna zostać zwrócona pełna definicja roli.

---

## Test nieistniejącej roli

Oczekiwany wynik:

```http
404 Not Found
```

---

# Endpoint: PATCH /api/projects/{project_id}/roles/{role_id}

## Test zmiany nazwy

Body:

```json
{
  "name": "Senior Developer"
}
```

Oczekiwany wynik:

```http
204 No Content
```

---

## Test zmiany uprawnień

Body:

```json
{
  "permissions": {
    "can_write_tickets": true,
    "can_help": true,
    "can_assign_help": true,
    "can_change_status": true,
    "can_make_roles": false,
    "can_change_roles": false,
    "can_assign_people_to_project": false
  }
}
```

Oczekiwany wynik:

```http
204 No Content
```

---

## Test nieistniejącej roli

Oczekiwany wynik:

```http
404 Not Found
```

---

## Test użytkownikiem niewłaścicielem

Oczekiwany wynik:

```http
403 Forbidden
```

---

# Test końcowy integralności

Po wykonaniu wszystkich testów:

1. GET /api/organization
2. GET /api/projects
3. GET /api/projects/{project_id}
4. GET /api/projects/{project_id}/members
5. GET /api/projects/{project_id}/roles

Wszystkie powinny zwracać poprawne dane bez błędów 4xx i 5xx.

Jeżeli którykolwiek endpoint zwróci:

```http
500 Internal Server Error
```

oznacza to błąd implementacji backendu wymagający naprawy.
