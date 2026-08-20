import asyncio
import os
import sys

from azure.identity.aio import DefaultAzureCredential
from azure.mgmt.cloudhealth.aio import CloudHealthMgmtClient
from azure.mgmt.cloudhealth.models import HealthReportRequest, HealthState

SIGNAL_NAME = "demo-async-report"


async def main() -> int:
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        print("AZURE_SUBSCRIPTION_ID is not set", file=sys.stderr)
        return 1

    model_id = os.environ.get("AHM_HEALTH_MODEL_ID")
    entity_name_override = os.environ.get("AHM_ENTITY_NAME")

    async with DefaultAzureCredential() as credential:
        async with CloudHealthMgmtClient(credential, subscription_id) as client:
            if model_id:
                segments = model_id.strip("/").split("/")
                resource_group = segments[3]
                model_name = segments[-1]
                model = await client.health_models.get(resource_group, model_name)
            else:
                model = None
                async for listed_model in client.health_models.list_by_subscription():
                    model = listed_model
                    break
                if model is None:
                    print("no health model found in this subscription", file=sys.stderr)
                    return 1
                resource_group = model.id.strip("/").split("/")[3]
                model_name = model.name

            print(f"health model: {model.name}")
            print(f"health model id: {model.id}")

            if entity_name_override:
                entity_name = entity_name_override
            else:
                entity_name = None
                async for listed in client.entities.list_by_health_model(
                    resource_group, model_name
                ):
                    entity_name = listed.name
                    break
                if entity_name is None:
                    print(
                        f"no entity found in health model {model_name}", file=sys.stderr
                    )
                    return 1

            entity = await client.entities.get(
                resource_group, model_name, entity_name
            )
            print(f"entity: {entity.name}")
            print(f"entity display name: {entity.properties.display_name}")

            await client.entities.ingest_health_report(
                resource_group,
                model_name,
                entity.name,
                HealthReportRequest(
                    signal_name=SIGNAL_NAME,
                    health_state=HealthState.DEGRADED,
                    value=2.0,
                    additional_context="sent by the asynchronous azure-mgmt-cloudhealth demo",
                    expires_in_minutes=60,
                ),
            )
            print(f"health report sent: signal {SIGNAL_NAME} on {entity.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
