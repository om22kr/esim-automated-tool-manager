# eSim Automated Tool Manager — Testing Report

## 1. Testing Objective

The objective of testing is to verify that the eSim Automated Tool Manager correctly detects, installs, updates, configures, and monitors the required software tools.

The primary tools configured in the project are:

- Git
- KiCad
- Ngspice

Testing also covers:

- Version tracking and comparison
- Dependency checking
- Package-manager integration
- Executable path configuration
- Application logging
- Ngspice installation/update workflow

---

## 2. Test Environments

### 2.1 Windows

| Component | Tested Version |
|---|---|
| Operating System | Windows 10 |
| Python | 3.14.3 |
| Git | 2.54.0 |
| KiCad | 10.0.5 |
| Ngspice | 47 |
| Winget | 1.29.280 |

### 2.2 Ubuntu through WSL

| Component | Tested Version |
|---|---|
| Operating System | Ubuntu on WSL |
| APT | 3.2.0 |
| Git | 2.53.0 |
| Python | Python 3 |

---

## 3. Syntax Testing

Core Python modules were compiled using:

```cmd
python -m py_compile src\main.py
python -m py_compile src\installer.py
python -m py_compile src\version_checker.py
python -m py_compile src\dependency_checker.py
python -m py_compile src\config_manager.py
python -m py_compile src\logger.py
python -m py_compile src\package_managers.py    