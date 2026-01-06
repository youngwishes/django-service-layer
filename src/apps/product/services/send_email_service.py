from dataclasses import dataclass

from config.container import container


@dataclass(kw_only=True, slots=True, frozen=True)
class SendSmsService:
    def __call__(self) -> None:
        print("Sending sms...")


def send_sms_service_factory() -> SendSmsService:
    return SendSmsService()


container.register("SendSmsService", factory=send_sms_service_factory)
