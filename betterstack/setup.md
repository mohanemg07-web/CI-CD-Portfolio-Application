# Better Stack Setup

This guide wires the Portfolio API into Better Stack for **uptime monitoring**
and **structured log ingestion**. Steps assume you already have a Better Stack
account and the backend deployed to Railway with a public URL.

---

## 1. Create an HTTP uptime monitor

1. Open **Uptime → Monitors → Create monitor**.
2. **Type:** `HTTP request`
3. **URL:** `https://<your-railway-backend>.up.railway.app/health`
4. **HTTP method:** `GET`
5. **Expected status code:** `200`
6. **Expected response body contains:** `"status":"ok"`

## 2. Set check frequency

- **Check frequency:** `1 minute`
- **Request timeout:** `10 seconds`
- **Regions:** at minimum `North America` + `Europe` (catches regional outages).

## 3. Set the downtime alert threshold

- **Confirm downtime after:** `1 minute`
  (sends the first alert once the monitor has been failing for ≥60 s)

## 4. Configure escalation

Open **On-call → Escalation policies → New policy** and add steps:

| Step | Delay         | Channel                |
|------|---------------|------------------------|
| 1    | Immediately   | Email                  |
| 2    | After 5 min   | SMS                    |
| 3    | After 15 min  | Phone call (optional)  |

Attach the policy to the monitor created in step 1 under **Alerts → On-call escalation**.

## 5. Configure the log drain

1. Open **Logs → Sources → Connect source**.
2. **Platform:** `HTTP`
3. **Name:** `portfolio-backend`
4. Copy the **Source token** that Better Stack displays.
5. In **Railway → Project → Variables**, add:

   ```
   BETTERSTACK_SOURCE_TOKEN=<paste source token>
   ```

6. Redeploy the backend service so it picks up the new env var.

The backend's [`StructuredLoggingMiddleware`](../backend/app/middleware/logging.py)
detects the token on startup and attaches an HTTP handler that POSTs every
request log to `https://in.logs.betterstack.com` with bearer auth. If the token
is unset, the handler is skipped entirely (no-op).

## 6. Verify logs are flowing

1. Hit the backend a few times to generate traffic:

   ```bash
   for i in {1..5}; do curl -s https://<your-railway-backend>.up.railway.app/health; done
   ```

2. Open **Better Stack → Logs → portfolio-backend → Live tail**.
3. Within ~5 seconds you should see JSON records like:

   ```json
   {
     "timestamp": "2026-05-27T14:23:11.842Z",
     "level": "INFO",
     "route": "/health",
     "method": "GET",
     "latency_ms": 2.117,
     "status_code": 200,
     "request_id": "8c1f4f4e-…"
   }
   ```

4. Confirm both `route` and `latency_ms` fields are present — that confirms the
   structured middleware is shipping correctly. If you see only stream output
   without `latency_ms`, the request was processed before `TimingMiddleware`
   ran; check middleware order in [`backend/app/main.py`](../backend/app/main.py).

---

## Troubleshooting

| Symptom                                  | Likely cause                                      | Fix                                                            |
|-----------------------------------------|---------------------------------------------------|----------------------------------------------------------------|
| Monitor shows green but no logs appear  | `BETTERSTACK_SOURCE_TOKEN` not set in Railway     | Add the env var and redeploy                                   |
| 401 errors in Better Stack ingestion    | Wrong source token                                | Regenerate token in Better Stack and update Railway variable   |
| Monitor flapping every check            | Cold-start latency exceeds 10 s timeout           | Raise request timeout, or enable Railway's "always-on" plan    |
| `latency_ms: null` in records           | Middleware order regression                        | Ensure `TimingMiddleware` is registered before logging         |
