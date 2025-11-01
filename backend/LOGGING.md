# Logging

Setup a globally logger at: `backend/app/core/logging.py`

## Usage

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

logger.debug("some debug message")
```

## Log Levels

Please try to use the correct log level: https://docs.python.org/3/library/logging.html#logging-levels

- **DEBUG**: Detailed information, typically of interest only when diagnosing problems
- **INFO**: Confirmation that things are working as expected
- **WARNING**: An indication that something unexpected happened
- **ERROR**: Due to a more serious problem, the software has not been able to perform some function
- **CRITICAL**: A serious error, indicating that the program itself may be unable to continue running

