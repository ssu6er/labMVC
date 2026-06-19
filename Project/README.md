# RandomChoice

RandomChoice to prosta aplikacja internetowa napisana w architekturze MVC. Umożliwia użytkownikowi tworzenie kategorii i opcji, a następnie losowanie jednej aktywnej opcji. Wyniki losowań są zapisywane w historii.


## Funkcjonalności

- rejestracja nowego użytkownika;
- logowanie za pomocą adresu e-mail i hasła;
- autoryzacja z użyciem tokenu JWT;
- wylogowanie przez usunięcie tokenu z `localStorage`;
- tworzenie i usuwanie kategorii;
- dodawanie i usuwanie opcji;
- włączanie i wyłączanie opcji;
- losowanie jednej aktywnej opcji po stronie backendu;
- zapisywanie wyniku losowania w historii;
- wyświetlanie i czyszczenie historii;
- ochrona danych użytkowników — każdy użytkownik widzi wyłącznie własne kategorie, opcje i historię;
- polski interfejs użytkownika.

## Technologie

### Backend

- Python;
- FastAPI;
- SQLAlchemy 2;
- Pydantic 2;
- PostgreSQL;
- JWT;
- bcrypt.

### Frontend

- HTML;
- CSS;
- JavaScript;
- Fetch API.

### Infrastruktura

- Docker;
- Docker Compose;
- Uvicorn.

## Architektura MVC

Projekt wykorzystuje uproszczony podział MVC:

- **Model** — modele SQLAlchemy, schematy Pydantic i konfiguracja bazy danych;
- **Controller** — endpointy FastAPI, logowanie, JWT, sprawdzanie dostępu i logika losowania;
- **View** — interfejs HTML, style CSS oraz JavaScript komunikujący się z API.

Przepływ danych:

```text
Użytkownik → View → Controller → Model → PostgreSQL
                         ↓
                    odpowiedź JSON
                         ↓
                       View
```

## Struktura projektu

```text
Project/
├── app/
│   ├── main.py
│   ├── model/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── entities.py
│   │   └── schemas.py
│   ├── controller/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── routes.py
│   └── view/
│       ├── index.html
│       ├── style.css
│       └── app.js
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### Odpowiedzialność plików

- `app/main.py` — tworzy aplikację FastAPI, podłącza router, pliki statyczne i tworzy tabele bazy danych;
- `app/model/database.py` — konfiguracja połączenia z PostgreSQL i sesji SQLAlchemy;
- `app/model/entities.py` — modele tabel: użytkownik, kategoria, opcja i historia;
- `app/model/schemas.py` — schematy Pydantic do walidacji danych;
- `app/controller/auth.py` — haszowanie haseł, tworzenie i sprawdzanie JWT;
- `app/controller/routes.py` — wszystkie endpointy API i kontrola dostępu;
- `app/view/index.html` — struktura interfejsu;
- `app/view/style.css` — wygląd i responsywność aplikacji;
- `app/view/app.js` — obsługa formularzy, tokenu JWT i komunikacji z API;
- `Dockerfile` — budowanie obrazu aplikacji;
- `docker-compose.yml` — uruchamianie aplikacji i PostgreSQL;
- `requirements.txt` — lista zależności Pythona;
- `.env.example` — przykładowe zmienne środowiskowe.


## Pakiety

Pakiety znajdują się w pliku `requirements.txt`.



