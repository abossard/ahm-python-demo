import os
import sys

from azure.identity import DefaultAzureCredential
from azure.mgmt.cloudhealth import CloudHealthMgmtClient
from azure.mgmt.cloudhealth.models import HealthReportRequest, HealthState

SIGNAL_NAME = "demo-sync-report"


def main() -> int:
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        print("AZURE_SUBSCRIPTION_ID is not set", file=sys.stderr)
        return 1

    model_id = os.environ.get("AHM_HEALTH_MODEL_ID")
    entity_name_override = os.environ.get("AHM_ENTITY_NAME")

    credential = DefaultAzureCredential()
    client = CloudHealthMgmtClient(credential, subscription_id)

    if model_id:
        segments = model_id.strip("/").split("/")
        resource_group = segments[3]
        model_name = segments[-1]
        model = client.health_models.get(resource_group, model_name)
    else:
        model = next(iter(client.health_models.list_by_subscription()), None)
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
        listed = next(
            iter(client.entities.list_by_health_model(resource_group, model_name)), None
        )
        if listed is None:
            print(f"no entity found in health model {model_name}", file=sys.stderr)
            return 1
        entity_name = listed.name

    entity = client.entities.get(resource_group, model_name, entity_name)
    print(f"entity: {entity.name}")
    print(f"entity display name: {entity.properties.display_name}")

    client.entities.ingest_health_report(
        resource_group,
        model_name,
        entity.name,
        HealthReportRequest(
            signal_name=SIGNAL_NAME,
            health_state=HealthState.HEALTHY,
            value=1.0,
            additional_context="sent by the synchronous azure-mgmt-cloudhealth demo",
            expires_in_minutes=60,
        ),
    )
    print(f"health report sent: signal {SIGNAL_NAME} on {entity.name}")

    client.close()
    credential.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
