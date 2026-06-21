
## TEST 1 — Zmiana hasła

### Krok 1.1 — Zarejestruj użytkownika

Endpoint: **`POST /api/auth/register`** → *Try it out* → wklej body → *Execute*.

```json
{
  "first_name": "Pawel",
  "last_name": "Testowy",
  "username": "pwtest",
  "email": "pwtest@example.com",
  "password": "TestPassword123!"
}
```

**Oczekiwane:** kod **201**, body `{ "id": "<uuid>" }`.

> Jeśli dostaniesz **409** „Username already registered” — ten user już istnieje
> z poprzedniej próby. Użyj innej nazwy, np. `pwtest2` i `pwtest2@example.com`,
> i pamiętaj o tym w kolejnych krokach.

### Krok 1.2 — Zaloguj się i skopiuj token

Endpoint: **`POST /api/auth/login`**.

```json
{
  "username": "pwtest",
  "password": "TestPassword123!",
  "remember_user": false
}
```

**Oczekiwane:** kod **200**, body:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "user": { "id": "<uuid>", "username": "pwtest", "organization_id": null }
}
```

**Skopiuj wartość `access_token`** (sam ciąg, bez cudzysłowów).

### Krok 1.3 — Autoryzuj się w Swaggerze

Kliknij przycisk **Authorize** (kłódka, prawy górny róg) → w polu wklej
**sam token** (Swagger sam dołoży `Bearer`) → **Authorize** → **Close**.

### Krok 1.4 — Zmień hasło (happy path)

Endpoint: **`POST /api/auth/change-password`**.

```json
{
  "current_password": "TestPassword123!",
  "new_password": "NewPassword123!"
}
```

**Oczekiwane:** kod **204 No Content** (puste body). Hasło zmienione. ✅

### Krok 1.5 — Potwierdź: logowanie nowym hasłem działa, starym nie

`POST /api/auth/login` z **nowym** hasłem:

```json
{ "username": "pwtest", "password": "NewPassword123!", "remember_user": false }
```

**Oczekiwane:** **200**.

`POST /api/auth/login` ze **starym** hasłem:

```json
{ "username": "pwtest", "password": "TestPassword123!", "remember_user": false }
```

**Oczekiwane:** **401** `{"detail":"Invalid authentication credentials"}`. ✅

> Uwaga: token z kroku 1.2 **nadal działa** po zmianie hasła — celowo nie unieważniamy
> aktywnej sesji (spójnie z resetem hasła). Nie musisz się ponownie autoryzować.

### Krok 1.6 — Przypadki błędne (warto sprawdzić)

Wszystkie poniższe wołasz na `POST /api/auth/change-password` (musisz być zalogowany — kłódka).
Po zmianie z kroku 1.4 aktualne hasło to teraz `NewPassword123!`.

| Body | Oczekiwany kod | Oczekiwany `detail` |
|---|---|---|
| `{"current_password":"zleHaslo1!","new_password":"Inne12345!"}` | **400** | `Current password is incorrect` |
| `{"current_password":"NewPassword123!","new_password":"NewPassword123!"}` | **400** | `New password must be different from the current password` |
| `{"current_password":"NewPassword123!","new_password":"slabe"}` | **422** | komunikat o wymaganiach hasła |

Test braku tokena: kliknij **Authorize → Logout**, potem wywołaj change-password →
**401** `{"detail":"Not authenticated"}`. Następnie autoryzuj się ponownie.

---

## TEST 2 — Usunięcie organizacji

Do tego testu potrzebny jest **właściciel organizacji**. Zrobimy świeżego użytkownika,
który założy własną organizację i ją usunie.

### Krok 2.1 — Zarejestruj właściciela

`POST /api/auth/register`:

```json
{
  "first_name": "Ola",
  "last_name": "Owner",
  "username": "orgowner",
  "email": "orgowner@example.com",
  "password": "TestPassword123!"
}
```

**Oczekiwane:** **201**, `{ "id": "<uuid>" }`.

### Krok 2.2 — Zaloguj i autoryzuj

`POST /api/auth/login`:

```json
{ "username": "orgowner", "password": "TestPassword123!", "remember_user": false }
```

Skopiuj `access_token` → **Authorize** (kłódka) → wklej → **Authorize** → **Close**.

### Krok 2.3 — Utwórz organizację

Endpoint: **`POST /api/organization`**.

```json
{ "name": "Acme Corp", "description": "Organizacja testowa" }
```

**Oczekiwane:** **201**, `{ "id": "<uuid>" }`. Twój user jest teraz jej właścicielem.

(Możesz zweryfikować: **`GET /api/organization`** → **200**, body z `name: "Acme Corp"`.)

### Krok 2.4 — Usuń organizację (happy path)

Endpoint: **`DELETE /api/organization`** → *Try it out* → *Execute* (body nie ma).

**Oczekiwane:** kod **204 No Content**. Organizacja usunięta. ✅

### Krok 2.5 — Potwierdź usunięcie

`GET /api/organization` (dalej zalogowany jako `orgowner`):

**Oczekiwane:** **404** `{"detail":"User does not belong to any organization"}`
— bo po usunięciu Twoje `organization_id` zostało wyzerowane. ✅

`DELETE /api/organization` jeszcze raz:

**Oczekiwane:** **404** (już nie masz organizacji). ✅

---
