# Contributing to RealityDefender SDK

Thank you for your interest in contributing to the RealityDefender SDK! This document outlines the process for contributing to this project and the best practices for each supported language.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Language-Specific Guidelines](#language-specific-guidelines)
  - [Python](#python)
  - [TypeScript](#typescript)
  - [Rust](#rust)
  - [Go](#go)
- [Testing](#testing)
- [Documentation](#documentation)
- [Versioning](#versioning)

## Code of Conduct

We expect all contributors to adhere to the highest standards of respect and inclusivity. Please be considerate of other contributors and users.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/eng-sdk.git`
3. Add the upstream repository: `git remote add upstream https://github.com/Reality-Defender/eng-sdk.git`
4. Create a new branch for your work: `git checkout -b feature/your-feature-name`

## Development Workflow

1. Make your changes in your feature branch
2. Write or update tests for your changes
3. Ensure all tests pass for the language you're working with
4. Update documentation as needed
5. Push your changes to your fork
6. Submit a pull request to the main repository

## Pull Request Process

1. Ensure your PR title clearly describes the change
2. Link any related issues in the PR description
3. Include a detailed description of the changes made
4. Make sure all tests pass in CI
5. Request a review from a maintainer
6. Address any feedback from reviewers

## Language-Specific Guidelines

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use [type hints](https://docs.python.org/3/library/typing.html) for all function parameters and return values
- Format your code with [Black](https://black.readthedocs.io/) using the project's configuration
- Use [pytest](https://docs.pytest.org/) for writing tests
- Use [flake8](https://flake8.pycqa.org/) for linting

#### Development Setup

```bash
cd python
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

### TypeScript

- Follow the [TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- Use interfaces for complex types
- Use async/await for asynchronous code
- Format code with the project's ESLint and Prettier configuration
- Write tests using Jest

#### Development Setup

```bash
cd typescript
npm install
```

### Rust

- Follow the [Rust Style Guide](https://doc.rust-lang.org/1.0.0/style/README.html)
- Format code with `rustfmt`
- Use the [Rust 2018 edition](https://doc.rust-lang.org/edition-guide/rust-2018/index.html)
- Handle errors using the `Result` type, not panics
- Prefer strong typing with enums and structs
- Use `cargo test` for running tests

#### Development Setup

```bash
cd rust
cargo build
```

### Go

- Follow the [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
- Format code with `gofmt`
- Use meaningful variable names
- Provide context in error messages
- Write tests using the standard library testing package
- Use the `just` tool for running common tasks

#### Development Setup

```bash
cd go
go mod download
```

## Testing

- Write unit tests for all new functionality
- Ensure existing tests continue to pass
- Add integration tests for any API changes
- Local tests should pass before submitting a PR
- All PRs will be automatically tested via GitHub Actions

## Documentation

- Update the README if you change behavior or add features
- Document all public functions, methods, and types
- Keep code examples in the documentation up-to-date
- Use clear, concise language in documentation

## Versioning

We follow [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for backward-compatible functionality additions
- PATCH version for backward-compatible bug fixes

---

Thank you for contributing to the RealityDefender SDK! Your efforts help improve the toolkit for all users. 
