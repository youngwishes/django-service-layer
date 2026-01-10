from dataclasses import dataclass
from config.container import container


@dataclass(kw_only=True, slots=True, frozen=True)
class SendCRMService:
    def __call__(self) -> None:
        print("Sending data to crm...")


def send_crm_service_factory() -> SendCRMService:
    return SendCRMService()


container.register("SendCRMService", factory=send_crm_service_factory)
