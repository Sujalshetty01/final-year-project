// Centralized API config with robust environment detection
// - Uses REACT_APP_API_URL if set (local or Docker Compose)
// - Fallback: detects Docker vs local by window.location.hostname
// - Warns if API URL is likely misconfigured
// - Provides a function to test backend connectivity

const getApiBaseUrl = () => {
  // 1. Use env variable if set
  let url = process.env.REACT_APP_API_URL;
  // 2. Fallback: detect Docker vs local
  if (!url) {
    const host = window.location.hostname;
    if (host === "localhost" || host === "127.0.0.1") {
      url = "http://localhost:8000/api/v1";
    } else if (host === "backend") {
      url = "http://backend:8000/api/v1";
    } else {
      // Default to current origin, but warn
      url = `${window.location.protocol}//${host}:8000/api/v1`;
      console.warn("[config] API URL fallback used:", url);
    }
  }
  // Validation: warn if using Docker hostname outside Docker
  if (url.includes("backend") && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")) {
    console.error("[config] API URL is set to 'backend' but frontend is running locally. This will NOT work. Use 'localhost' for local dev.");
  }
  if (url.includes("localhost") && window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
    console.warn("[config] API URL is set to 'localhost' but frontend is not running on localhost. This may not work in Docker.");
  }
  return url.replace(/\/$/, "");
};

// Health check utility
export async function checkBackendHealth() {
  const url = getApiBaseUrl() + "/health";
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error("Non-200 response");
    return true;
  } catch (e) {
    console.error(`[config] Backend health check failed: ${url}`, e);
    return false;
  }
}

export const API_BASE_URL = getApiBaseUrl();