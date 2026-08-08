# ===========================================================
# Aura Ecosystem - Master Makefile 
# ===========================================================

# Force Windows command interpreter for cross-environment compatibility
SHELL = cmd.exe
.SHELLFLAGS = /c

PYTHON = python
PIP = pip
NMAKE = nmake

REQ = requirements.txt
DEVREQ = requirements-dev.txt

DASHBOARD = extensions\cert_dashboard
CERT = extensions\cert_automation
SPECS = specs\asyncapi.yaml
MATLAB_DIR = matlab

.PHONY: help install dev update clean dashboard cert lint test format doctor aura api web build package docs docker deploy xlsl agent models benchmark spec-check matlab-status

help:
	@echo.
	@echo Aura Master Build Commands
	@echo ================================================
	@echo install     Install Python dependencies
	@echo dev         Install development packages
	@echo update      Upgrade installed packages
	@echo dashboard   Launch Streamlit dashboard
	@echo cert        Run certificate automation
	@echo lint        Run Ruff linter
	@echo format      Format code
	@echo test        Run tests
	@echo doctor      Check environment
	@echo clean       Remove cache files
	@echo aura        Start Aura core Python script
	@echo api         Run FastAPI backend
	@echo web         Start frontend web app
	@echo xlsl        Compile .xlsl definitions
	@echo spec-check  Verify 3xpl AsyncAPI specification
	@echo.

install:
	@echo Installing dependencies...
	@$(PIP) install -r $(REQ)

dev:
	@echo Installing development tools...
	@$(PIP) install -r $(DEVREQ)

update:
	@echo Updating packages...
	@$(PIP) install --upgrade -r $(REQ)

dashboard:
	@echo Launching dashboard...
	@cd $(DASHBOARD) && streamlit run app.py

cert:
	@echo Running certificate automation...
	@powershell -ExecutionPolicy Bypass -File $(CERT)\auto_cert.ps1

lint:
	@echo Running Ruff...
	@ruff check .

format:
	@echo Formatting source...
	@black .

test:
	@echo Running tests...
	@pytest

doctor:
	@echo Python Version
	@$(PYTHON) --version
	@echo Pip Version
	@$(PIP) --version
	@where python

clean:
	@echo Cleaning...
	@if exist .pytest_cache rmdir /S /Q .pytest_cache
	@if exist .ruff_cache rmdir /S /Q .ruff_cache
	@if exist __pycache__ rmdir /S /Q __pycache__
	@for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /S /Q "%%d"

aura:
	@python aura.py

api:
	@uvicorn aura.api:app --reload

web:
	@cd web && npm install && npm run dev

build:
	@python setup.py build

package:
	@python -m build

docs:
	@mkdocs serve

docker:
	@docker compose up --build

deploy:
	@python scripts/deploy.py

xlsl:
	@python tools/xlsl_compiler.py

agent:
	@python aura/agent.py

models:
	@python aura/model_manager.py

benchmark:
	@benchmarks\run.py

spec-check:
	@echo Checking AsyncAPI specification integrity...
	@if exist $(SPECS) (echo Found: $(SPECS)) else (echo Error: asyncapi.yaml missing in specs/!)
