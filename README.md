# AHM Python SDK demo

Azure Health Models (`Microsoft.CloudHealth/healthmodels`) demo using `azure-mgmt-cloudhealth`. Each script authenticates with `DefaultAzureCredential`, picks a health model, picks one of its entities, and sends a health report. `sync_demo.py` uses the synchronous client, `async_demo.py` uses the `aio` client.

## Run

```bash
export AZURE_SUBSCRIPTION_ID=<your-subscription-id>
uv run sync_demo.py
uv run async_demo.py
```

Without `AHM_HEALTH_MODEL_ID` the report is written to whichever health model the subscription lists first, so set it if you care which model gets the report.

## Environment variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `AZURE_SUBSCRIPTION_ID` | yes | Subscription to query. `DefaultAzureCredential` does not supply one. |
| `AHM_HEALTH_MODEL_ID` | no | Full ARM resource id of a health model. Defaults to the first model returned by `list_by_subscription`. |
| `AHM_ENTITY_NAME` | no | Entity to report on. Defaults to the first entity returned by `list_by_health_model`. |

## What gets written

Each run posts one health report. `sync_demo.py` sends signal `demo-sync-report` (`Healthy`), `async_demo.py` sends `demo-async-report` (`Degraded`). A signal name the entity does not already have is added by the resource provider as an `External` signal that expires after 60 minutes.

The ingest call returns an empty body, so read the result back to confirm it:

```bash
az rest --method GET --url "https://management.azure.com/<health-model-id>/entities/<entity-name>?api-version=2026-05-01-preview" \
  | jq .properties.signalGroups.external.signals
```

## Requirements

Python 3.14. `azure-core[aio]` is a direct dependency because the async client needs the `aiohttp` transport, which `azure-identity` does not pull in.
