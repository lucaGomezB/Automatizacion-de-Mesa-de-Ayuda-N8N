# docker-security-hardening — Spec

## Purpose

Define los requisitos de seguridad para contenedores Docker: usuarios no root, healthchecks, y archivos .dockerignore para optimizar el contexto de build.

## Requirements

### Requirement: Docker containers SHALL run as non-root users
The Dockerfiles SHALL create and use dedicated non-root users for running applications.

#### Scenario: Backend container runs as non-root user
- **WHEN** the backend container starts
- **THEN** the process SHALL run as a user other than root
- **AND** the user SHALL have appropriate permissions to access application files

#### Scenario: Frontend container runs as non-root user
- **WHEN** the frontend container starts
- **THEN** the process SHALL run as a user other than root
- **AND** the user SHALL have appropriate permissions to access nginx files

### Requirement: Dockerfiles SHALL include healthcheck instructions
The Dockerfiles SHALL define HEALTHCHECK instructions for container health monitoring.

#### Scenario: Backend healthcheck verifies application availability
- **WHEN** the backend container is running
- **THEN** the healthcheck SHALL verify that the FastAPI application is responding on port 8000

#### Scenario: Frontend healthcheck verifies nginx availability
- **WHEN** the frontend container is running
- **THEN** the healthcheck SHALL verify that nginx is serving content on port 3000

### Requirement: Projects SHALL include .dockerignore files
The project SHALL include .dockerignore files in service directories to exclude unnecessary files from Docker build context.

#### Scenario: Backend .dockerignore excludes development files
- **WHEN** building the backend Docker image
- **THEN** the build context SHALL exclude .git, __pycache__, tests/, .pytest_cache, and .env files

#### Scenario: Frontend .dockerignore excludes development files
- **WHEN** building the frontend Docker image
- **THEN** the build context SHALL exclude .git, node_modules/, dist/, and .env files
