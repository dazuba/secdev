# P12 - IaC & Container Security Summary
## Обзор результатов сканирования

Дата: 2025-12-24
Артефакт: P12_EVIDENCE

---

## 1. Hadolint - Dockerfile Security Linting

**Статус:** ✅ PASSED
**Отчёт:** `hadolint_report.json`

**Результаты:**
- Найдено проблем: **0**
- Dockerfile соответствует лучшим практикам безопасности
---

## 2. Checkov - Infrastructure as Code Security

**Статус:** ⚠️ WARNINGS FOUND
**Отчёт:** `checkov_report.json`

**Результаты:**
- **Passed:** 80 проверок
- **Failed:** 11 проверок
- **Skipped:** 0
- **Resource count:** 4
- **Parsing errors:** 0

### Найденные проблемы:

1. **CKV_K8S_38** - Ensure that Service Account Tokens are only mounted where necessary
   - **Файл:** /deployment.yaml
   - **Ресурс:** Deployment.default.secdev-app

2. **CKV_K8S_21** - The default namespace should not be used
   - **Файл:** /deployment.yaml
   - **Ресурс:** Deployment.default.secdev-app

3. **CKV_K8S_40** - Containers should run as a high UID to avoid host conflict
   - **Файл:** /deployment.yaml
   - **Ресурс:** Deployment.default.secdev-app

4. **CKV_K8S_31** - Ensure that the seccomp profile is set to docker/default or runtime/default
   - **Файл:** /deployment.yaml
   - **Ресурс:** Deployment.default.secdev-app

5. **CKV_K8S_15** - Image Pull Policy should be Always
   - **Файл:** /deployment.yaml
   - **Ресурс:** Deployment.default.secdev-app

6. **CKV_K8S_35** - Prefer using secrets as files over secrets as environment variables
   - **Файл:** /deployment.yaml
   - **Ресурс:** Deployment.default.secdev-app

7. **CKV_K8S_43** - Image should use digest
   - **Файл:** /deployment.yaml
   - **Ресурс:** Deployment.default.secdev-app

8. **CKV_K8S_22** - Use read-only filesystem for containers where possible
   - **Файл:** /deployment.yaml
   - **Ресурс:** Deployment.default.secdev-app

9. **CKV_K8S_21** - The default namespace should not be used
   - **Файл:** /service.yaml
   - **Ресурс:** Service.default.secdev-app

10. **CKV_K8S_21** - The default namespace should not be used
   - **Файл:** /secret.yaml
   - **Ресурс:** Secret.default.app-secrets

---

## 3. Trivy - Container Image Vulnerability Scanning

**Статус:** ⚠️ VULNERABILITIES FOUND
**Отчёт:** `trivy_report.json`

**Результаты:**
- **Всего уязвимостей:** 65
- **os-pkgs:** 61 уязвимостей
- **lang-pkgs:** 4 уязвимостей
- **Критичные/Высокие:** 2

### Критичные/Высокие уязвимости:

1. **HIGH: CVE-2024-23342** - ecdsa
   - **Версия:** 0.19.1
   - **Описание:** python-ecdsa: vulnerable to the Minerva attack

2. **HIGH: CVE-2025-62727** - starlette
   - **Версия:** 0.41.3
   - **Описание:** starlette: Starlette DoS via Range header merging

---

## Статистика

| Инструмент | Статус | Найдено проблем |
|------------|--------|-----------------|
| Hadolint   | ✅ PASS | 0               |
| Checkov    | ⚠️ WARN | 11              |
| Trivy      | ⚠️ WARN | 65              |
