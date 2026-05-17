#!/usr/bin/env bash
# Check whether the warn→fail flip admission for DATAPULSE_MODELBUS_VALIDATION_MODE
# is granted. Exit 0 = granted, 1 = pending, 2 = argument error.
# See issue #52 and design §11.2.
set -euo pipefail
exec uv run python -m datapulse.core.validation_counter check "$@"
