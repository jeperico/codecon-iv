# Codecon IV — Sistema de Fila de Espera com Livro de Ofertas

API REST em Django/DRF para gerenciar **filas de espera** em que cada usuário ocupa uma posição e pode **vender essa posição** para outro usuário através de uma **oferta** no livro de ofertas (`BookOffer`).

Quando alguém compra uma posição:

- Se o comprador **não está** na fila, ele assume a posição exata do vendedor.
- Se o comprador **já está** na fila e atrás do vendedor, o vendedor sai e a fila compacta (todos atrás do vendedor sobem uma posição, incluindo o comprador).
- Se o comprador está à frente do vendedor (ou na mesma posição), a compra é bloqueada.

---

## Sumário

- [Stack](#stack)
- [Arquitetura](#arquitetura)
- [Modelo de domínio](#modelo-de-domínio)
- [Regras de negócio](#regras-de-negócio)
- [Setup do ambiente](#setup-do-ambiente)
- [Autenticação](#autenticação)
- [Endpoints](#endpoints)
- [Fluxos completos com exemplos](#fluxos-completos-com-exemplos)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Pontos em aberto / próximos passos](#pontos-em-aberto--próximos-passos)

---

## Stack

- **Python 3** + **Django 5.1** + **Django REST Framework**
- **PostgreSQL 16** (via Docker)
- **JWT** (`djangorestframework-simplejwt`)
- **drf-spectacular** (OpenAPI/Swagger)
- **django-cors-headers**, **django-jazzmin** (admin)

---

## Arquitetura

A API segue uma separação clara:

```
api.py        → viewsets DRF (thin layer; só roteamento + serialização)
serializers.py → validação de entrada/saída
services.py   → regra de negócio (transações atômicas)
models.py     → schema de dados + constraints
```

Operações que mexem em múltiplos registros (entrar na fila, criar oferta, comprar) vivem em `services.py` envoltas em `@transaction.atomic` com `select_for_update()` para evitar corrida.

---

## Modelo de domínio

```
User ─┬──< QueueUser >──┬─ Queue
      │                 │
      └──< BookOffer >──┘
       (seller/buyer)
```

| Modelo | Descrição |
|---|---|
| **User** | Usuário autenticável (extende `AbstractBaseUser`). PK UUID. Login por e-mail. |
| **Queue** | Uma fila nomeada. |
| **QueueUser** | Vínculo de um usuário a uma posição em uma fila. `position` inteiro positivo, único por fila. |
| **BookOffer** | Anúncio de venda de uma `QueueUser`. Tem `seller`, `buyer` (após venda), `queue`, `price`, `sold`. |

### Constraints

- `QueueUser.(user, queue)` único — um usuário só ocupa uma posição por fila.
- `QueueUser.(queue, position)` único — duas pessoas não dividem a mesma posição.
- `BookOffer.queue_user` é único quando `sold=False` — só uma oferta ATIVA por posição.

### Observação sobre `BookOffer`

- `queue_user` é **nullable** com `on_delete=SET_NULL`. Quando uma `QueueUser` é apagada (caso "comprador atrás do vendedor"), a oferta sobrevive e mantém o histórico.
- `seller`, `buyer` e `queue` são **denormalizados** na oferta para permitir consultas históricas mesmo após mudanças na fila.

---

## Regras de negócio

### Entrar na fila

- Calcula automaticamente `position = última + 1`.
- Bloqueia se o usuário já tem `QueueUser` naquela fila.

### Criar oferta

- O usuário precisa estar na fila para anunciar.
- Apenas **uma** oferta ativa (`sold=False`) por posição.
- `price` deve ser positivo.

### Comprar oferta

Lógica encapsulada em `services.buy_offer`:

| Situação do comprador | O que acontece |
|---|---|
| Não está na fila | Comprador **assume** a `QueueUser` do vendedor; demais posições inalteradas. |
| Está na fila, **atrás** do vendedor | Vendedor sai, fila **compacta** (todos com `position > seller_position` sobem 1). Comprador acaba uma posição à frente. |
| Está na fila, **na frente ou na mesma** posição do vendedor | **400 Bad Request**. |
| É o próprio vendedor | **400 Bad Request**. |

Após a compra, a oferta é marcada `sold=True` e `buyer` é preenchido.

---

## Setup do ambiente

### Pré-requisitos

- Docker + Docker Compose
- `make` (opcional, atalhos do `Makefile`)

### Variáveis de ambiente

Crie um `.env` na raiz com:

```bash
POSTGRES_USER=codecon
POSTGRES_PASSWORD=codecon
POSTGRES_DB=codecon
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=admin
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Subir tudo

```bash
make build          # build da imagem
make up             # sobe postgres + pgadmin + django
make migrate        # roda as migrations
make createsuperuser  # opcional, p/ acessar /admin/
make logs           # acompanha logs do Django
```

Serviços expostos:

| Serviço | Porta | URL |
|---|---|---|
| Django API | 8000 | http://localhost:8000/api/ |
| Swagger | 8000 | http://localhost:8000/api/schema/swagger/ |
| Redoc | 8000 | http://localhost:8000/api/schema/redoc/ |
| Postgres | 5432 | — |
| pgAdmin | 8081 | http://localhost:8081 |

### Comandos úteis

```bash
make bash             # shell no container Django
make makemigrations   # gerar migrations
make pyshell          # Django shell
make down             # derruba tudo
```

---

## Autenticação

A API usa **JWT (Bearer)** via `simplejwt`. Por padrão, **todos os endpoints exigem autenticação**, exceto:

- `POST /api/profiles/register-user/`
- `POST /api/token/`
- `POST /api/token/refresh/`
- `POST /api/token/verify/`
- Swagger / Redoc / schema

### Fluxo

1. **Registrar** um usuário em `/api/profiles/register-user/`.
2. **Obter token** em `/api/token/` (retorna `access` + `refresh`).
3. Em toda requisição autenticada, enviar header `Authorization: Bearer <access>`.
4. Quando o `access` expirar (12h), use `/api/token/refresh/` com o `refresh` (7 dias).

> Todas as actions que envolvem o usuário corrente (`enter`, `create offer`, `buy`) derivam o usuário do token JWT — **não passe `user_id` no body**, ele será ignorado.

---

## Endpoints

> Todos sob o prefixo `/api/`.

### Auth

| Método | Path | Descrição |
|---|---|---|
| POST | `/profiles/register-user/` | Cria um usuário. Body: `{ name, email, password }` |
| POST | `/token/` | Login. Body: `{ email, password }` → `{ access, refresh, user }` |
| POST | `/token/refresh/` | Renova access. Body: `{ refresh }` |
| POST | `/token/verify/` | Valida token. Body: `{ token }` |

### Usuários

| Método | Path | Descrição |
|---|---|---|
| GET | `/profiles/user/` | Lista usuários |
| GET | `/profiles/user/{id}/` | Detalha um usuário |
| GET | `/profiles/user/me/` | Retorna o usuário autenticado |

### Filas

| Método | Path | Descrição |
|---|---|---|
| GET | `/profiles/queue/` | Lista filas |
| POST | `/profiles/queue/` | Cria uma fila. Body: `{ name, description? }` |
| GET | `/profiles/queue/{id}/` | Detalha fila |
| PUT/PATCH/DELETE | `/profiles/queue/{id}/` | Atualiza/deleta fila |
| POST | `/profiles/queue/{id}/enter/` | **Entra na fila** (sem body). Retorna o `QueueUser` criado |

### Posições (somente leitura)

| Método | Path | Descrição |
|---|---|---|
| GET | `/profiles/queue_user/` | Lista todas as posições ativas |
| GET | `/profiles/queue_user/{id}/` | Detalha uma posição |

### Ofertas (BookOffer)

| Método | Path | Descrição |
|---|---|---|
| GET | `/profiles/book_offer/` | Lista ofertas. Suporta `?sold=true|false` e `?queue=<id>` |
| GET | `/profiles/book_offer/{id}/` | Detalha oferta |
| POST | `/profiles/book_offer/` | **Cria oferta**. Body: `{ queue: "<uuid>", price: 1000 }` |
| POST | `/profiles/book_offer/{id}/buy/` | **Compra oferta** (sem body) |

---

## Fluxos completos com exemplos

> Todos os exemplos usam `curl` apontando para `http://localhost:8000`.

### 1. Registrar dois usuários

```bash
# Alice
curl -X POST http://localhost:8000/api/profiles/register-user/ \
  -H 'Content-Type: application/json' \
  -d '{"name":"Alice","email":"alice@example.com","password":"superSecret123"}'

# Bob
curl -X POST http://localhost:8000/api/profiles/register-user/ \
  -H 'Content-Type: application/json' \
  -d '{"name":"Bob","email":"bob@example.com","password":"superSecret123"}'
```

### 2. Obter tokens

```bash
ALICE=$(curl -s -X POST http://localhost:8000/api/token/ \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@example.com","password":"superSecret123"}' \
  | jq -r .access)

BOB=$(curl -s -X POST http://localhost:8000/api/token/ \
  -H 'Content-Type: application/json' \
  -d '{"email":"bob@example.com","password":"superSecret123"}' \
  | jq -r .access)
```

### 3. Criar uma fila

```bash
QUEUE_ID=$(curl -s -X POST http://localhost:8000/api/profiles/queue/ \
  -H "Authorization: Bearer $ALICE" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Show do Coldplay","description":"Pista premium"}' \
  | jq -r .id)
```

### 4. Alice entra na fila

```bash
curl -X POST "http://localhost:8000/api/profiles/queue/$QUEUE_ID/enter/" \
  -H "Authorization: Bearer $ALICE"
# → { "id":"...", "position":1, "user":{...Alice...}, "queue":{...} }
```

### 5. Alice anuncia sua posição

```bash
OFFER_ID=$(curl -s -X POST http://localhost:8000/api/profiles/book_offer/ \
  -H "Authorization: Bearer $ALICE" \
  -H 'Content-Type: application/json' \
  -d "{\"queue\":\"$QUEUE_ID\",\"price\":15000}" \
  | jq -r .id)
```

### 6. Bob compra a posição da Alice (Bob não estava na fila)

```bash
curl -X POST "http://localhost:8000/api/profiles/book_offer/$OFFER_ID/buy/" \
  -H "Authorization: Bearer $BOB"
# → { "id":"...", "position":1, "user":{...Bob...}, "queue":{...} }
```

Resultado: Bob agora ocupa a posição 1; Alice está fora da fila; a oferta tem `sold=true` e `buyer=Bob`.

### 7. Listar apenas ofertas ativas de uma fila

```bash
curl "http://localhost:8000/api/profiles/book_offer/?queue=$QUEUE_ID&sold=false" \
  -H "Authorization: Bearer $BOB"
```

### 8. Cenário "fila compacta" (comprador já está atrás)

Fila inicial: `[A(1), Seller(2), C(3), Buyer(4)]`. Buyer compra a oferta do Seller.

Resultado:

```
[A(1), C(2), Buyer(3)]
```

Seller é removido; C avança de 3 → 2; Buyer avança de 4 → 3. A oferta fica registrada com `sold=true`, `queue_user=null` (a `QueueUser` do Seller foi deletada).

---

## Estrutura de pastas

```
codecon-iv/
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── requirements.txt
├── README.md                  # este arquivo
└── app/
    ├── manage.py
    ├── app/                   # projeto Django
    │   ├── settings.py
    │   ├── urls.py            # raiz das URLs ( /admin/, /api/ )
    │   └── wsgi.py
    ├── apps/
    │   ├── urls.py            # router DRF + swagger + jwt
    │   └── profiles/
    │       ├── models.py      # User, Queue, QueueUser, BookOffer
    │       ├── serializers.py # serializers DRF
    │       ├── services.py    # regras de negócio (enter/create_offer/buy_offer)
    │       ├── api.py         # viewsets thin + @actions
    │       ├── urls.py        # router do app profiles
    │       ├── admin.py
    │       └── migrations/
    └── utils/
        └── models.py          # BaseModel, DatedModel (mixins reusáveis)
```

---

## Pontos em aberto / próximos passos

Sugestões para evolução, em ordem de prioridade:

1. **Endpoint de sair da fila** (`POST /queue/{id}/leave/`) — hoje quem entrou e desistiu precisa vender; deveria poder sair de graça.
2. **Cancelar oferta** (`POST /book_offer/{id}/cancel/`) — vendedor mudou de ideia.
3. **Restringir criação de fila** — hoje qualquer usuário autenticado pode criar/editar/deletar `Queue`. Restringir a `is_staff` ou marcar `created_by` e exigir ownership.
4. **Notificações** — quando uma oferta é vendida, avisar comprador e vendedor (email/websocket).
5. **Testes automatizados** — principalmente para `buy_offer` (concorrência, edge cases das três variações de comprador).
6. **`Queue.is_open` / `closed_at`** — fechar fila quando o evento ocorre.
7. **Unidade monetária explícita** — hoje `price` é `PositiveIntegerField` sem unidade; padronizar (centavos? moeda?).
8. **Histórico expandido na oferta** — gravar `sold_at` e `seller_position_at_sale` para auditoria robusta.
