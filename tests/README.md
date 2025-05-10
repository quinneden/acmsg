# Testing acmsg

This directory contains the test suite for the `acmsg` package.

## Running Tests

You can run the tests using pytest:

```bash
pytest
```

### Running with Coverage

To run tests with coverage reporting:

```bash
pytest --cov=acmsg
```

## Test Structure

- `conftest.py`: Contains shared fixtures used across tests
- `test_*.py`: Individual test modules for each component

## Writing New Tests

When adding new functionality to acmsg, please also add corresponding tests:

1. Use appropriate fixtures from `conftest.py` when possible
2. Mock external dependencies (subprocess calls, API requests)
3. Test both success cases and error handling
4. Ensure high coverage for critical components
