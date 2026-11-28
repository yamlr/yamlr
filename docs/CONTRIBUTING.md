# Contributing to Yamlr (AI Agent Protocol)

Yamlr is developed via AI-led "vibe coding" for a product visionary. This document outlines the protocols for AI agents and the audit checklist for the visionary.

## Development Setup

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yamblr/yamlr.git
    cd yamlr
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run Tests**
    We use `pytest` for unit and integration testing.
    ```bash
    pytest
    ```

## Project Structure
*   `src/yamlr/core`: Core logic (Parser, Healer, Pipeline).
*   `src/yamlr/pro`: Enterprise features (OPA, Auth).
*   `src/yamlr/cli`: Command line interface.
*   `tests/`: Unit and integration tests.

## Submitting Changes
1.  Fork the repo.
2.  Create a feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes.
4.  Push to the branch.
5.  Open a Pull Request.

## Coding Standards
*   Follow PEP 8.
*   **Modular Architecture**: Adhere to the [Modularity Engineering Guide](MODULARITY_GUIDE.md). Do not create "God Objects".
*   Ensure all tests pass (`python test_runner.py`).
*   Add new tests for new features.
