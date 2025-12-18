# DV - Мини-проект «DevOps-конвейер»

---

## 0) Мета

- **Проект (опционально BYO):** SecDev Course Template (учебный шаблон)
- **Версия (commit/date):** ec618ac / 2025-12-18
- **Кратко (1-2 предложения):** FastAPI приложение для голосования за фичи с JWT-аутентификацией и PostgreSQL. Контейнеризировано, с полным CI/CD конвейером включающим тесты, security сканы, SBOM/SCA и SAST.

---

## 1) Воспроизводимость локальной сборки и тестов (DV1)

- **Одна команда для сборки/тестов:**

  ```bash
  pip install -r requirements.txt -r requirements-dev.txt && pytest --cov=app
  ```

- **Версии инструментов (фиксация):**

  ```bash
  python3 --version  # Python 3.9.6 (system) / 3.10-3.12 (CI matrix)
  docker --version   # Docker 29.1.2
  ```

  _Версии зафиксированы в `requirements.txt`, `requirements-dev.txt` и `pyproject.toml`_

- **Описание шагов (кратко):**
  1. Создать venv: `python3 -m venv .venv && source .venv/bin/activate`
  2. Установить зависимости: `pip install -r requirements.txt -r requirements-dev.txt`
  3. Запустить тесты: `pytest --cov=app --cov-report=html -v`
  4. Собрать wheel: `python -m build --wheel`

---

## 2) Контейнеризация (DV2)

- **Dockerfile:** `Dockerfile` (multi-stage: build + runtime, base `python:3.11-slim`)
  - **Build stage:** gcc для компиляции, venv с зависимостями, очистка apt cache
  - **Runtime stage:** только Python slim + venv, без dev-пакетов
  - **Размер:** ~200-250MB (оптимизирован)
  
- **Сборка/запуск локально:**

  ```bash
  docker build -t secdev-app:local .
  docker run --rm -p 8000:8000 secdev-app:local
  # Healthcheck: http://localhost:8000/health
  ```

  - **Порт:** 8000
  - **User:** non-root (appuser, UID 1000)
  - **HEALTHCHECK:** каждые 30s, проверяет `/health` endpoint
  - **ENV:** `PYTHONUNBUFFERED=1`, `PYTHONDONTWRITEBYTECODE=1`

- **(Опционально) docker-compose:** `compose.yaml` - полный стек
  - **db:** PostgreSQL 16-alpine с healthcheck
  - **app:** FastAPI приложение (depends_on db)
  - **Сети:** `secdev-network` (bridge)
  - **Volumes:** `postgres_data` для персистентности
  - Запуск: `docker compose up --build`

---

## 3) CI: базовый pipeline и стабильный прогон (DV3)

- **Платформа CI:** GitHub Actions
- **Файл конфига CI:** `.github/workflows/ci.yml` (основной), `ci-sbom-sca.yml`, `ci-sast-secrets.yml`
- **Стадии:** checkout → setup → **cache** → **build** → **lint** → **test** → **docker** → **deploy**
- **Фрагмент конфигурации (ключевые шаги):**

  ```yaml
  jobs:
    test:
      name: Test (Python ${{ matrix.python-version }} on ${{ matrix.os }})
      runs-on: ${{ matrix.os }}
      strategy:
        matrix:
          python-version: ["3.10", "3.11", "3.12"]
          os: [ubuntu-latest, macos-latest]
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with: { python-version: ${{ matrix.python-version }} }
        - uses: actions/cache@v4
          with:
            path: ~/.cache/pip
            key: ${{ runner.os }}-pip-${{ hashFiles('requirements*.txt', 'pyproject.toml') }}
        - run: pip install -r requirements.txt -r requirements-dev.txt
        - run: python -m build --wheel
        - run: pytest --cov=app --cov-report=xml --cov-report=html -v
        - uses: actions/upload-artifact@v4
          with:
            name: coverage-${{ matrix.os }}-py${{ matrix.python-version }}
            path: coverage.xml, htmlcov/, coverage.bin
    
    docker-scan:
      # Trivy + Hadolint сканирование
    docker-build:
      # Сборка и сохранение образа
    compose-test:
      # Интеграционный тест полного стека
    deploy-staging / deploy-production:
      # CD с эмуляцией деплоя
  ```

- **Стабильность:** Последние 5+ коммитов проходят все checks зелёными (test, docker-scan, docker-build, compose-test)
- **Ссылка/копия лога прогона:** https://github.com/dazuba/secdev/actions

---

## 4) Артефакты и логи конвейера (DV4)

_Артефакты сохраняются в GitHub Actions (retention 7-90 дней) и в `/EVIDENCE/` для трассировки._

| Артефакт/лог                        | Путь в `EVIDENCE/` или CI                          | Комментарий                                           |
|-------------------------------------|---------------------------------------------------|-------------------------------------------------------|
| Coverage reports                    | CI: `coverage-{os}-py{version}/`                  | HTML+XML coverage (per matrix), объединённый в `combined-coverage-report` |
| Wheel packages                      | CI: `wheel-{os}-py{version}/`                     | Python wheels (~10-15KB), `secdev_app-0.1.0-py3-none-any.whl` |
| Docker image                        | CI: `docker-image/` (7 days)                      | Сжатый tar.gz образа secdev-app:test (~80-100MB)      |
| Trivy security scan                 | CI: `trivy-security-report/` (30 days)            | SARIF формат, HIGH+CRITICAL уязвимости                 |
| SBOM + SCA                          | `P09/sbom.json`, `P09/sca_report.json`            | CycloneDX SBOM (Syft), уязвимости зависимостей (Grype)|
| SAST + Secrets                      | `P10/semgrep.sarif`, `P10/gitleaks.json`          | Semgrep findings, секреты в истории (Gitleaks)         |
| Deployment manifests                | CI: `staging/production-deployment-manifest`      | JSON с версией, временем, окружением                   |

---

## 5) Секреты и переменные окружения (DV5 - гигиена, без сканеров)

- **Шаблон окружения:** Секреты документированы в `compose.yaml` и `README.md`:
  - `DATABASE_URL` - PostgreSQL connection string
  - `JWT_SECRET` - JWT signing key (обязательный, нет дефолта после фикса SAST)
  - `STAGING_DATABASE_URL`, `STAGING_JWT_SECRET` (staging окружение)
  - `PRODUCTION_DATABASE_URL`, `PRODUCTION_JWT_SECRET` (production окружение)
  
- **Хранение и передача в CI:**  
  - Секреты настроены в GitHub Secrets (Settings → Secrets and variables → Actions)
  - В логах CI автоматически маскируются (`***`)
  
- **Пример использования секрета в job:**

  ```yaml
  - name: Start services
    env:
      DATABASE_URL: ${{ secrets.DATABASE_URL || 'postgresql://secdev_user:secdev_password@db:5432/feature_votes' }}
      JWT_SECRET: ${{ secrets.JWT_SECRET || 'test-secret-key-change-in-production' }}
    run: docker compose up -d --build
  
  - name: Test staging health endpoint
    env:
      DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}
      JWT_SECRET: ${{ secrets.STAGING_JWT_SECRET }}
    run: curl -f http://localhost:8000/health
  ```

- **Проверка отсутствия секретов в коде:**

  ```bash
  # Gitleaks v8.21.2 в CI (security/.gitleaks.toml)
  # Результат: EVIDENCE/P10/gitleaks.json (0 secrets found)
  ```

  _Gitleaks отчёт: `EVIDENCE/P10/gitleaks.json` (automated CI check)_
  
- **Памятка по ротации:**
  1. Отозвать скомпрометированный секрет в источнике (БД, API провайдер)
  2. Сгенерировать новое значение
  3. Обновить в GitHub Secrets (Settings → Secrets → Edit)
  4. Перезапустить активные деплои (staging/production jobs)
  5. Проверить логи на ошибки доступа
  6. Зафиксировать инцидент в `SECURITY.md` или issue tracker

---

## 6) Индекс артефактов DV

_Чтобы преподаватель быстро сверил файлы._

| Тип          | Файл в `EVIDENCE/`                     | Дата/время          | Коммит     | Runner/OS           |
|--------------|----------------------------------------|---------------------|------------|---------------------|
| CI Config    | `.github/workflows/ci.yml`             | 2025-12-18 22:21    | `ec618ac`  | -                   |
| Dockerfile   | `Dockerfile`                           | 2025-12-18          | `8d557e1`  | -                   |
| Compose      | `compose.yaml`                         | 2025-12-18          | `8d557e1`  | -                   |
| SBOM         | `P09/sbom.json`                        | 2025-12-18 15:26    | `8d557e1`  | `gha-ubuntu-latest` |
| SCA Report   | `P09/sca_report.json`, `sca_summary.md`| 2025-12-18 15:26    | `8d557e1`  | `gha-ubuntu-latest` |
| SAST         | `P10/semgrep.sarif`                    | 2025-12-18 18:37    | `8d557e1`  | `gha-ubuntu-latest` |
| Secrets Scan | `P10/gitleaks.json`, `sast_summary.md` | 2025-12-18 18:37    | `8d557e1`  | `gha-ubuntu-latest` |
| Package      | `dist/secdev_app-0.1.0-py3-none-any.whl` | Local build       | `ec618ac`  | `local-macOS`       |
| Coverage     | `coverage.xml`, `htmlcov/`             | Local run          | `ec618ac`  | `local`             |
| Scripts      | `scripts/run-ci-local.sh`              | 2025-12-18          | `8d557e1`  | -                   |

**Примечание:** CI артефакты (wheels, coverage, docker images) доступны в GitHub Actions Artifacts с retention 7-90 дней.

---

## 7) Связь с TM и DS (hook)

- **TM:** этот конвейер обслуживает риски процесса сборки/поставки (например, культура работы с секретами, воспроизводимость).  
- **DS:** сканы/гейты/триаж будут оформлены в `DS.md` с артефактами в `EVIDENCE/`.

---

## 8) Самооценка по рубрике DV (0/1/2)

- **DV1. Воспроизводимость локальной сборки и тестов:** [ ] 0 [ ] 1 [X] 2  
  _Фиксация зависимостей (requirements.txt, pyproject.toml), скрипт `run-ci-local.sh`, воспроизводимая матрица Python 3.10-3.12_
  
- **DV2. Контейнеризация (Docker/Compose):** [ ] 0 [ ] 1 [X] 2  
  _Multi-stage Dockerfile, оптимизация (~200MB), non-root user, healthcheck; compose с PostgreSQL, сетями, volumes_
  
- **DV3. CI: базовый pipeline и стабильный прогон:** [ ] 0 [ ] 1 [X] 2  
  _GitHub Actions с матрицей (6 комбинаций OS×Python), кэширование, параллельные jobs (test/docker/compose), concurrency control, стабильные прогоны_
  
- **DV4. Артефакты и логи конвейера:** [ ] 0 [ ] 1 [X] 2  
  _Coverage reports, wheel packages, Docker images, security scans (Trivy/Hadolint/Semgrep/Gitleaks), deployment manifests с метаданными_
  
- **DV5. Секреты и конфигурация окружения (гигиена):** [ ] 0 [ ] 1 [X] 2  
  _GitHub Secrets для окружений (staging/prod), Gitleaks автоматический скан (0 findings), убран hardcoded JWT_SECRET после SAST находки, маскирование в логах_

**Итог DV (сумма):** **10**/10
