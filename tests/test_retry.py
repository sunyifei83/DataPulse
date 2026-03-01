"""Tests for retry decorator and circuit breaker."""

from __future__ import annotations

import pytest

from datapulse.core.retry import retry, CircuitBreaker, CircuitBreakerOpen, RateLimitError


class TestRetry:
    def test_succeeds_first_attempt(self):
        call_count = 0

        @retry(max_attempts=3, base_delay=0.01)
        def success():
            nonlocal call_count
            call_count += 1
            return "ok"

        assert success() == "ok"
        assert call_count == 1

    def test_retries_then_succeeds(self):
        call_count = 0

        @retry(max_attempts=3, base_delay=0.01, retryable=(ValueError,))
        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("not yet")
            return "ok"

        assert flaky() == "ok"
        assert call_count == 3

    def test_raises_after_max_attempts(self):
        @retry(max_attempts=2, base_delay=0.01, retryable=(ValueError,))
        def always_fail():
            raise ValueError("always")

        with pytest.raises(ValueError, match="always"):
            always_fail()

    def test_non_retryable_exception_not_retried(self):
        call_count = 0

        @retry(max_attempts=3, base_delay=0.01, retryable=(ValueError,))
        def type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("wrong type")

        with pytest.raises(TypeError):
            type_error()
        assert call_count == 1

    def test_backoff_factor(self):
        """Verify that delay increases — we just check it doesn't crash."""
        call_count = 0

        @retry(max_attempts=3, base_delay=0.001, backoff_factor=2.0, max_delay=0.1)
        def backoff():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("retry")
            return "done"

        assert backoff() == "done"
        assert call_count == 3


class TestCircuitBreaker:
    def test_closed_state_passes_calls(self):
        cb = CircuitBreaker(failure_threshold=3)
        assert cb.state == CircuitBreaker.CLOSED
        result = cb.call(lambda: "ok")
        assert result == "ok"

    def test_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=60.0)

        def fail():
            raise ValueError("boom")

        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(fail)

        assert cb.state == CircuitBreaker.OPEN

    def test_open_rejects_calls(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60.0)

        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))

        with pytest.raises(CircuitBreakerOpen):
            cb.call(lambda: "should not reach")

    def test_success_resets_count(self):
        cb = CircuitBreaker(failure_threshold=3)

        # One failure
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))

        # Then a success
        cb.call(lambda: "ok")
        assert cb.state == CircuitBreaker.CLOSED
        assert cb._failure_count == 0

    def test_reset(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60.0)
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("x")))
        assert cb.state == CircuitBreaker.OPEN
        cb.reset()
        assert cb.state == CircuitBreaker.CLOSED

    def test_half_open_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.0, name="test")
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("x")))
        # With recovery_timeout=0, should immediately transition
        assert cb.state == CircuitBreaker.HALF_OPEN


class TestRateLimitError:
    def test_attributes(self):
        err = RateLimitError("too many", retry_after=5.0)
        assert str(err) == "too many"
        assert err.retry_after == 5.0

    def test_defaults(self):
        err = RateLimitError()
        assert err.retry_after == 0.0

    def test_retry_respects_retry_after(self):
        """retry() should use retry_after instead of exponential delay."""
        call_count = 0

        @retry(max_attempts=2, base_delay=100.0, retryable=(RateLimitError,))
        def rate_limited():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RateLimitError("429", retry_after=0.01)
            return "ok"

        assert rate_limited() == "ok"
        assert call_count == 2

    def test_retry_caps_retry_after_at_max_delay(self):
        call_count = 0

        @retry(max_attempts=2, base_delay=0.001, max_delay=0.01, retryable=(RateLimitError,))
        def capped():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RateLimitError("429", retry_after=999.0)
            return "ok"

        # Should succeed — the retry_after is capped at max_delay
        assert capped() == "ok"

    def test_retry_ignores_retry_after_when_disabled(self):
        call_count = 0

        @retry(
            max_attempts=2, base_delay=0.001, retryable=(RateLimitError,),
            respect_retry_after=False,
        )
        def no_respect():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RateLimitError("429", retry_after=0.01)
            return "ok"

        assert no_respect() == "ok"

    def test_retry_after_zero_uses_exponential(self):
        call_count = 0

        @retry(max_attempts=2, base_delay=0.001, retryable=(RateLimitError,))
        def zero_after():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RateLimitError("429", retry_after=0.0)
            return "ok"

        assert zero_after() == "ok"


class TestCircuitBreakerRateLimit:
    def test_rate_limit_weight_doubles_failure(self):
        cb = CircuitBreaker(failure_threshold=4, rate_limit_weight=2)

        def rate_limit():
            raise RateLimitError("429")

        # 2 rate-limit failures × weight 2 = 4 → should open
        for _ in range(2):
            with pytest.raises(RateLimitError):
                cb.call(rate_limit)

        assert cb.state == CircuitBreaker.OPEN

    def test_rate_limit_opens_faster(self):
        """With weight=2, circuit opens in half the failures vs normal."""
        cb_normal = CircuitBreaker(failure_threshold=4, rate_limit_weight=2)
        cb_rate = CircuitBreaker(failure_threshold=4, rate_limit_weight=2)

        # Normal: 4 regular failures needed
        for _ in range(3):
            with pytest.raises(ValueError):
                cb_normal.call(lambda: (_ for _ in ()).throw(ValueError("x")))
        assert cb_normal.state == CircuitBreaker.CLOSED

        # Rate-limit: 2 failures needed (2 × weight 2 = 4)
        for _ in range(2):
            with pytest.raises(RateLimitError):
                cb_rate.call(lambda: (_ for _ in ()).throw(RateLimitError("429")))
        assert cb_rate.state == CircuitBreaker.OPEN

    def test_normal_failure_uses_weight_1(self):
        cb = CircuitBreaker(failure_threshold=3, rate_limit_weight=2)

        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(lambda: (_ for _ in ()).throw(ValueError("x")))
        # 2 normal failures (weight 1 each) = 2, below threshold of 3
        assert cb.state == CircuitBreaker.CLOSED

    def test_default_rate_limit_weight(self):
        cb = CircuitBreaker()
        assert cb.rate_limit_weight == 2
