from aws_cdk import Stack
from constructs import Construct

from scheduled_messages.infrastructure import ScheduledMessages


class ScheduledMessagesStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ScheduledMessages(self, "ScheduledMessages")
