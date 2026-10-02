from app.models import Hub
from app.schemas import HubPublic


def hub_to_public(hub: Hub, *, participant_count: int = 0) -> HubPublic:
    return HubPublic(
        id=hub.id,
        slug=hub.slug,
        name=hub.name,
        description=hub.description,
        participant_count=participant_count,
    )
