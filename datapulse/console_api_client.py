"""Shared browser-side API boundary for the DataPulse console."""

from __future__ import annotations


def render_console_api_client_script() -> str:
    return """    function createConsoleApiClient() {
      function normalizeRequestOptions(options = {}) {
        const normalized = { ...options };
        if (!Object.prototype.hasOwnProperty.call(normalized, "payload")) {
          return normalized;
        }
        const payload = normalized.payload;
        delete normalized.payload;
        normalized.headers = {
          "Content-Type": "application/json",
          ...(normalized.headers || {}),
        };
        normalized.body = JSON.stringify(payload);
        return normalized;
      }

      async function request(path, { responseType = "json", ...options } = {}) {
        const response = await fetch(path, normalizeRequestOptions(options));
        if (!response.ok) {
          const detail = await response.text();
          throw new Error(detail || `Request failed: ${response.status}`);
        }
        if (responseType === "text") {
          return response.text();
        }
        return response.json();
      }

      return {
        json(path, options = {}) {
          return request(path, options);
        },
        text(path, options = {}) {
          return request(path, { ...options, responseType: "text" });
        },
      };
    }

    const consoleApiClient = createConsoleApiClient();

    async function api(path, options = {}) {
      return consoleApiClient.json(path, options);
    }

    async function apiText(path, options = {}) {
      return consoleApiClient.text(path, options);
    }
"""
