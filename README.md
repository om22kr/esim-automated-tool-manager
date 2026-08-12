# eSim Automated Tool Manager

## 1. Project Overview

The eSim Automated Tool Manager is a Python-based command-line utility for managing software tools used in an eSim development environment.

The application provides a menu-driven interface to:

- List installed tools
- Check tool versions
- Install tools
- Update tools
- Check system dependencies
- Configure executable paths
- View application logs

The current tool configuration includes:

- Git
- KiCad
- Ngspice

---

## 2. Project Objectives

The main objectives of the project are:

1. Detect required development tools.
2. Check installed software versions.
3. Compare installed versions with required versions.
4. Install and update configured tools.
5. Check system dependencies.
6. Allow users to configure executable paths.
7. Maintain application logs.
8. Verify the integrity of downloaded software using SHA-256 hashing.
9. Support platform-specific package managers.
10. Provide a simple command-line interface for tool management.

---

## 3. Key Features

### 3.1 Tool Detection

The manager checks whether the configured tools are installed and available.

Supported tools:

- Git
- KiCad
- Ngspice

Example:

```text
Git          Version: 2.54.0     Status: Compatible
KiCad        Version: 10.0.5     Status: Compatible
Ngspice      Version: 47         Status: Compatible