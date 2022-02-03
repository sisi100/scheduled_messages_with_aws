import aws_cdk as cdk

from deployment import ScheduledMessagesStack

app = cdk.App()
ScheduledMessagesStack(app, "ScheduledMessagesStack")

app.synth()
