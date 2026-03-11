# Specyfikacja projektu: Secure Incydent

## 1. Opis projektu

**Secure Incydent** to webowa platforma do zgłaszania i obsługi problemów oraz incydentów w obrębie organizacji i jej projektów.  
Jej celem jest uporządkowanie zgłoszeń, umożliwienie śledzenia statusu, przypisywania odpowiedzialnych osób oraz utrzymywania historii zmian w jednym miejscu.

Projekt ma charakter **edukacyjny**, ale równocześnie ma pokazywać dobre praktyki:
- projektowania aplikacji webowych,
- modelowania uprawnień,
- prowadzenia historii działań,
- bezpiecznego tworzenia oprogramowania,
- pracy zespołowej z wykorzystaniem repozytorium, testów i deploymentu.

System nie jest ograniczony do działu IT. Może służyć małym organizacjom i prywatnym strukturom, w których zgłoszenia problemów powinny być obsługiwane w podziale na projekty.

---

## 2. Cel biznesowy i problem, który rozwiązuje

W organizacjach zgłoszenia problemów często giną w komunikatorach, mailach lub ustnych ustaleniach. Trudno potem ustalić:
- kto zgłosił problem,
- kto odpowiada za jego rozwiązanie,
- na jakim etapie jest sprawa,
- jakie działania już wykonano,
- którego projektu dotyczy zgłoszenie.

Secure Incydent ma rozwiązać ten problem przez zapewnienie:
- jednego miejsca do rejestracji zgłoszeń,
- jasnego statusu każdego zgłoszenia,
- przypisania odpowiedzialnych osób,
- komentarzy i historii zmian,
- trwałego powiązania zgłoszenia z konkretnym projektem,
- widoczności danych zależnej od projektu i uprawnień.

---

## 3. Docelowy użytkownik

System jest projektowany głównie dla:
- **małych organizacji**,
- **prywatnych struktur**,
- zespołów, które potrzebują prostego i bezpiecznego narzędzia do obsługi problemów.

Projekt nie jest planowany jako rozwiązanie enterprise.  
Na etapie MVP skupia się na małej skali, prostocie użycia, bezpieczeństwie i łatwości wdrożenia.

---

## 4. Założenia domenowe

### 4.1 Organizacje i projekty
- organizacja może posiadać wiele projektów,
- użytkownik może nie być „członkiem organizacji globalnie”, ale może należeć do jednego lub wielu projektów,
- widoczność danych użytkownika wynika przede wszystkim z członkostwa w projektach,
- jeśli użytkownik nie ma uprawnień w danym projekcie, nie powinien go widzieć.

### 4.2 Projekty jako główny kontekst pracy
- zgłoszenia są tworzone **w obrębie konkretnego projektu**,
- użytkownik może mieć **inną rolę w każdym projekcie**,
- **jeden użytkownik ma dokładnie jedną rolę per projekt**,
- problemu **nie można przenosić pomiędzy projektami**.

### 4.3 Kategorie
- kategorie są definiowane **per projekt**,
- solver może być powiązany z jedną lub wieloma kategoriami w projekcie,
- solver widzi zgłoszenia zgodnie z zakresem swoich uprawnień projektowych i kategorii.

---

## 5. Zakres funkcjonalny projektu

### 5.1 Funkcje podstawowe
System ma umożliwiać:
- rejestrację użytkownika,
- logowanie użytkownika,
- utworzenie nowej organizacji przy pierwszej rejestracji,
- dołączenie do istniejącej organizacji:
  - przez kod,
  - przez link,
  - lub przez ręczne dodanie,
- tworzenie projektów w organizacji,
- zapraszanie użytkowników do projektu,
- przypisywanie użytkowników do projektów,
- przypisywanie jednej roli użytkownika w projekcie,
- tworzenie zgłoszeń/incydentów w projekcie,
- przypisywanie zgłoszeń do osoby odpowiedzialnej,
- komentowanie zgłoszeń,
- śledzenie statusu zgłoszenia,
- przeglądanie historii własnych zgłoszeń,
- zarządzanie rolami i użytkownikami w projektach,
- definiowanie kategorii zgłoszeń per projekt,
- prowadzenie historii zmian widocznych dla zgłaszającego.

### 5.2 Funkcje bezpieczeństwa
System ma zawierać:
- kontrolę dostępu opartą o role,
- możliwość tworzenia własnych ról,
- przypisywanie uprawnień do ról,
- bezpieczne uwierzytelnianie loginem i hasłem,
- podstawową politykę haseł,
- reset hasła w MVP,
- niemodyfikowalną historię zmian widocznych dla zgłaszającego,
- bezpieczne komunikaty błędów bez wycieku poufnych informacji,
- tekstowe komentarze i opisy,
- logowanie także nieudanych prób logowania.

### 5.3 Funkcje operacyjne
Projekt powinien uwzględniać:
- REST API,
- kontrakt API,
- dokumentację OpenAPI / Swagger,
- uruchamianie lokalne przez Docker i Docker Compose,
- deployment demo na jednej maszynie VPS,
- monorepo z oddzielonymi ścieżkami dla backendu, frontendu, infrastruktury i dokumentacji.

### 5.4 Funkcje jakościowe
Projekt ma pokazywać:
- testowalność,
- czytelny kod i dokumentację,
- łatwość deploymentu,
- prostotę użycia,
- bezpieczeństwo już na poziomie projektu i procesu.

---

## 6. MVP

### 6.1 Definicja MVP
MVP to **minimalna działająca wersja platformy**, która pozwala:
- utworzyć konto i organizację lub do niej dołączyć,
- utworzyć projekt lub zostać do niego zaproszonym,
- zalogować się,
- utworzyć zgłoszenie w projekcie,
- przypisać zgłoszenie do osoby odpowiedzialnej,
- zmieniać status zgłoszenia,
- komentować zgłoszenie,
- śledzić historię statusu i przypisania,
- korzystać z podstawowego modelu ról per projekt.

### 6.2 Minimalny zakres MVP
Do MVP wchodzą:
- rejestracja,
- logowanie,
- reset hasła,
- tworzenie organizacji,
- dołączanie do organizacji przez kod lub link,
- tworzenie projektów,
- dołączanie do projektów,
- role bazowe,
- tworzenie własnych ról,
- przypisywanie jednej roli użytkownika do projektu,
- zarządzanie użytkownikami projektu,
- tworzenie kategorii per projekt,
- zgłoszenia,
- przypisanie głównego solvera,
- komentarze,
- statusy,
- priorytety,
- historia zmian zgłoszenia,
- REST API + Swagger,
- uruchomienie lokalne przez Compose,
- deployment demo na VPS.

### 6.3 Poza MVP
Poza MVP odkładamy:
- notification system,
- dashboards / analytics,

Interfejs webowy powinien jednak być responsywny, aby dało się korzystać z niego z telefonu.

---

## 7. Model organizacyjny

### 7.1 Organizacje
- organizacja jest kontenerem dla projektów,
- organizacja ma jednego ownera, który może zarządzać wszystkimi projektami,
- admin może zarządzać w obrębie projektu,
- użytkownik może zostać zaproszony do organizacji lub bezpośrednio do projektu,
- sama widoczność danych biznesowych wynika głównie z projektów, nie z samego istnienia organizacji.

### 7.2 Projekty
- projekt należy do organizacji,
- projekt ma właściciela lub osobę zarządzającą (admin),
- projekt ma listę członków,
- projekt posiada własne role i/lub używa ról dostępnych w organizacji,
- projekt posiada własne kategorie,
- użytkownik bez przypisania do projektu nie może go widzieć.

### 7.3 Kategorie
- kategorie są zarządzane per projekt,
- solver może być przypisany do jednej lub wielu kategorii w projekcie,
- problem ma kategorię obowiązkową już przy tworzeniu zgłoszenia.

---

## 8. Role i uprawnienia

### 8.1 Role bazowe
Na start system przewiduje role:
- **owner**
- **admin**
- **problem_reporter**
- **problem_solver**

### 8.2 Zakres ról
Role są przypisywane **per projekt**.  
Użytkownik ma dokładnie **jedną rolę w projekcie**.

### 8.3 Rola owner
Owner:
- zarządza organizacją lub projektem,
- zarządza użytkownikami,
- tworzy role,
- definiuje uprawnienia,
- może przypisywać zgłoszenia,
- może zarządzać kategoriami.

### 8.4 Rola admin
Admin:
- może zarządzać użytkownikami,
- może zarządzać rolami,
- może przypisywać zgłoszenia,
- ma szeroki wgląd w zgłoszenia i historię zmian projektu.

### 8.5 Rola reporter
Reporter:
- może tworzyć zgłoszenia,
- widzi swoje zgłoszenia aktualne i historyczne,
- może komentować,
- nie może edytować treści zgłoszenia po utworzeniu,
- może zamknąć zgłoszenie, jeśli nie jest już ważne.

### 8.6 Rola solver
Solver:
- jest główną osobą rozwiązującą problem,
- może zmieniać status,
- może zmieniać priorytet,
- może zawnioskować o zmianę przypisania,
- nie może sam usunąć swojego przypisania,
- działa w obrębie kategorii przypisanych mu w projekcie.

### 8.7 Role niestandardowe
System ma zawierać mechanizm tworzenia własnych ról i ich dostępu.  
Na poziomie modelu danych przyjmuje się, że użytkownik ma jedną rolę per projekt.

---

## 9. Workflow zgłoszenia

### 9.1 Statusy
Zgłoszenie może mieć jeden z następujących statusów:
- `NEW`
- `PROBLEM_IS_BEING_SOLVED`
- `RESOLVED`
- `CLOSED`
- `REJECTED`

### 9.2 Zmiana statusu
Status mogą zmieniać:
- owner,
- admin,
- solver,
- reporter w zakresie zamknięcia zgłoszenia, gdy nie jest już ważne.

Reporter może także potwierdzić, że problem został rozwiązany, ale nie jest to obowiązkowe.

### 9.3 Przypisanie
- zgłoszenie ma jednego głównego solvera,
- inni mogą pomagać, ale nie jest to obowiązkowy element MVP,
- przypisania dokonuje:
  - owner,
  - admin,
  - lub inna rola z odpowiednim uprawnieniem.

### 9.4 Priorytet
System przewiduje priorytet, np.:
- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

Priorytet:
- może być ustawiony przez reportera przy zgłoszeniu,
- może być później zmieniony przez solvera, admina lub ownera.

### 9.5 Kategorie
- każde zgłoszenie ma kategorię,
- kategoria jest obowiązkowa już przy tworzeniu zgłoszenia,
- zgłoszenie należy do jednego projektu i nie może zostać do innego projektu przeniesione.

---

## 10. Formularz zgłoszenia

### 10.1 Pola obowiązkowe
Przy utworzeniu zgłoszenia obowiązkowe są:
- `title`
- `description`
- `category`
- `project`

### 10.2 Pola opcjonalne
Na dalszym etapie można przewidzieć:
- priorytet,
- dodatkowe kategorie,
- załączniki.

Załączniki nie wchodzą do MVP.

---

## 11. Komentarze i historia zmian

- reporter może dodawać komentarze po utworzeniu zgłoszenia,
- komentarze są widoczne także dla reportera,
- komentarze nie są edytowalne,
- zamiast edycji można dodać kolejny komentarz,
- komentarze pozostają przy zgłoszeniu nawet po zmianie przypisanego solvera.

### 11.1 Zakres historii widocznej dla zgłaszającego
W `problem_logs` przechowywane są wyłącznie informacje, które zgłaszający może widzieć:
- komentarz,
- zmiana statusu,
- zmiana przypisanego solvera.

Nie zakłada się osobnego, publicznie widocznego pełnego audytu dla zgłaszającego.

---

## 12. Audyt

### 12.1 Założenie
Historia zmian zgłoszenia ma być **niemodyfikowalna** z poziomu UI.

### 12.2 Zdarzenia audytowane / logowane w kontekście zgłoszenia
Do historii zgłoszenia trafiają:
- dodanie komentarza,
- zmiana statusu,
- zmiana przypisanego solvera.

### 12.3 Dodatkowe zdarzenia systemowe
System dodatkowo loguje:
- logowanie,
- nieudane próby logowania,
- zmiany ról i uprawnień,
- operacje administracyjne związane z organizacją i projektami.

Sposób przechowywania tych logów administracyjnych może być rozdzielony od `problem_logs`.

### 12.4 Widoczność historii
- owner i admin widzą pełniejszy zakres danych administracyjnych,
- reporter widzi historię swoich zgłoszeń:
  - komentarze,
  - historię statusu,
  - historię zmiany głównego solvera.

---

## 13. Wymagania bezpieczeństwa

### 13.1 Uwierzytelnianie
Logowanie odbywa się przez:
- login + hasło

### 13.2 Wymagania hasła
Hasło w MVP musi spełniać warunki:
- minimum 8 znaków,
- mała litera,
- duża litera,
- cyfra,
- znak specjalny.

### 13.3 Reset hasła
Reset hasła wchodzi do MVP.

### 13.4 Status konta
Konto użytkownika może być:
- aktywne,
- dezaktywowane

### 13.5 Bezpieczne błędy
Komunikaty błędów dla użytkownika:
- nie mogą ujawniać poufnych danych,
- powinny jasno wskazywać, że operacja się nie udała.

Szczegóły techniczne powinny trafiać do logów systemowych, a nie do odpowiedzi API.

### 13.6 Bezpieczne przetwarzanie danych
Na MVP:
- komentarze i opisy są zwykłym tekstem,
- nie dopuszczamy HTML,
- ograniczamy ryzyko XSS.

### 13.7 2FA
2FA może zostać rozważone później, jeśli okaże się wykonalne bez zbyt dużej komplikacji projektu.

---

## 14. API i architektura techniczna

### 14.1 Stack
- **Backend:** Python 3.x + FastAPI
- **Frontend:** React
- **Database:** PostgreSQL
- **Containerization:** Docker + Docker Compose
- **Tests:** pytest

### 14.2 API
- głównym sposobem komunikacji będzie **REST API**,
- projekt ma posiadać **kontrakt API**,
- dokumentacja ma być wystawiona przez **OpenAPI / Swagger**.

### 14.3 Frontend
Backend ma być przygotowany pod oddzielny frontend.  
Jednak do pierwszego demo dopuszczalne jest pokazanie:

- API
- Swagger UI

---

## 15. Deployment i środowiska

### 15.1 Środowisko lokalne
Do developmentu i testów:
- uruchamianie lokalne przez Docker Compose

### 15.2 Środowisko demo
Do prezentacji:
- deployment na jednej maszynie VPS

### 15.3 Dane demonstracyjne
Na tym etapie nie wymagacie seedów ani przykładowych organizacji w MVP, ale może to zostać dodane, jeśli ułatwi demo.

---

## 16. Wymagania niefunkcjonalne

Najważniejsze wymagania niefunkcjonalne projektu:
- **bezpieczeństwo**
- **testowalność**
- **łatwość deploymentu**
- **prostota użycia**

Wydajność nie jest priorytetem na etapie MVP, ponieważ projekt jest kierowany głównie do małych organizacji.

---

## 19. Proponowane demo MVP

Minimalne demo powinno pokazać:
1. Rejestrację i logowanie użytkownika
2. Utworzenie organizacji albo dołączenie do istniejącej
3. Utworzenie projektu albo dołączenie do projektu
4. Utworzenie zgłoszenia w projekcie
5. Przypisanie zgłoszenia do solvera
6. Zmianę statusu zgłoszenia
7. Podgląd historii i komentarzy

To pokazuje pełny przepływ biznesowy w modelu organizacja → projekt → problem.

---

## 20. Zdanie podsumowujące projekt

**Secure Incydent to webowa platforma dla małych organizacji do zgłaszania, przypisywania i śledzenia problemów oraz incydentów w obrębie projektów, z naciskiem na role, bezpieczeństwo, historię zmian i czytelny workflow.**

Wersja MVP:
**MVP to minimalna wersja systemu, w której użytkownik może utworzyć lub dołączyć do organizacji i projektu, zgłosić problem, przypisać go do rozwiązania, śledzić status i historię zmian oraz korzystać z podstawowego modelu ról per projekt.**
