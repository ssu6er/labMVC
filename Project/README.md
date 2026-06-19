# RandomChoice

RandomChoice to prosty projekt edukacyjny MVC, który pomaga użytkownikowi losowo wybrać jedną z wcześniej dodanych opcji.

## Funkcje

* rejestracja i logowanie użytkownika;
* autoryzacja za pomocą JWT;
* tworzenie i usuwanie kategorii;
* dodawanie, usuwanie oraz włączanie i wyłączanie opcji;
* losowanie aktywnej opcji;
* zapisywanie wyników w historii;
* oddzielenie danych różnych użytkowników.

## Architektura MVC

* **Model** — PostgreSQL, SQLAlchemy 2 i Pydantic 2;
* **Controller** — FastAPI, obsługa API i kontrola dostępu;
* **View** — HTML, CSS i JavaScript z Fetch API.

## Technologie

* Python;
* FastAPI;
* PostgreSQL;
* SQLAlchemy;
* Pydantic;
* HTML, CSS i JavaScript;
* Docker i Docker Compose.

## Uruchomienie

Skopiuj plik konfiguracyjny:

```bash
cp .env.example .env
```

W systemie Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Uruchom projekt:

```bash
docker compose up --build
```

Aplikacja będzie dostępna pod adresem:

```text
http://localhost:8000
```

Dokumentacja API:

```text
http://localhost:8000/docs
```

## Zatrzymanie projektu

```bash
docker compose down
```

Plik `.env` nie jest wysyłany do repozytorium. Przykładowa konfiguracja znajduje się w pliku `.env.example`.
