# SCA Summary Report

**Generated:** 2025-12-18 15:26:24 UTC
**Commit:** 8d557e1a1787a76678c5f0880ea1edf1c9c16d8a

## Severity Distribution

- **High**: 5
- **Medium**: 2

## Critical and High Severity Issues

### GHSA-wj6h-64fc-37mp - ecdsa@0.19.1
- **Severity**: High
- **Fixed in**: 
- **Description**: Minerva timing attack on P-256 in python-ecdsa

### GHSA-r9hx-vwmv-q579 - setuptools@58.0.4
- **Severity**: High
- **Fixed in**: 65.5.1
- **Description**: pypa/setuptools vulnerable to Regular Expression Denial of Service (ReDoS)

### GHSA-cx63-2mw6-8hw5 - setuptools@58.0.4
- **Severity**: High
- **Fixed in**: 70.0.0
- **Description**: setuptools vulnerable to Command Injection via package URL

### GHSA-5rjg-fvgr-3xxf - setuptools@58.0.4
- **Severity**: High
- **Fixed in**: 78.1.1
- **Description**: setuptools has a path traversal vulnerability in PackageIndex.download that leads to Arbitrary File Write

### GHSA-7f5h-v6xp-fcq8 - starlette@0.41.3
- **Severity**: High
- **Fixed in**: 0.49.1
- **Description**: Starlette vulnerable to O(n^2) DoS via Range header merging in ``starlette.responses.FileResponse``


## Actions Taken

- **GHSA-f96h-pmfr-66vw (Starlette DoS)**: Fixed by upgrading fastapi from 0.112.2 to 0.115.6, which includes starlette 0.41.3 with the fix
- **GHSA-7f5h-v6xp-fcq8 (Starlette)**: Waived - requires starlette 0.49.1 which breaks fastapi compatibility. Monitoring for fastapi update.
- **GHSA-wj6h-64fc-37mp (ecdsa timing attack)**: Waived - transitive dependency, low risk timing attack, no fix available
- **GHSA-r9hx-vwmv-q579, GHSA-cx63-2mw6-8hw5, GHSA-5rjg-fvgr-3xxf (setuptools)**: Waived - build-time only dependencies, not in production runtime

All waivers documented in `policy/waivers.yml` with expiration dates and issue references.
