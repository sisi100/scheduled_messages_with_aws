import os
import pathlib

from aws_cdk import aws_events, aws_events_targets, aws_lambda, aws_lambda_event_sources, aws_sqs
from constructs import Construct


class ScheduledMessages(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id)

        schedule_rule = aws_events.Rule(
            self,
            "Schedule",
            schedule=aws_events.Schedule.cron(minute="0", hour="12", month="*", week_day="*", year="*"),
        )
        queue = aws_sqs.Queue(self, "Queue")

        self.__create_dispatcher_lambda(trigger_rule=schedule_rule, send_queue=queue)

        self.__create_worker_lambda(consume_queue=queue)

    def __create_dispatcher_lambda(self, trigger_rule: aws_events.Rule, send_queue: aws_sqs.Queue):
        """
        ルールで起動して、SQSにアイテムを投げるLambdaを作成する
        """
        dispatcher_lambda = aws_lambda.Function(
            self,
            "DispatcherLambda",
            environment={"SQS_NAME": send_queue.queue_name},
            **self.__build_lambda_param("dispatcher.handler"),
        )
        send_queue.grant_send_messages(dispatcher_lambda)
        trigger_rule.add_target(aws_events_targets.LambdaFunction(dispatcher_lambda))

    def __create_worker_lambda(self, consume_queue: aws_sqs.Queue):
        """
        SQSをトリガーにしてメッセージを送信する想定のLambdaを作成する
        """
        powertools_layer = aws_lambda.LayerVersion.from_layer_version_arn(
            self,
            "lambda-powertools-layer",
            f"arn:aws:lambda:{os.getenv('CDK_DEFAULT_REGION')}:017000801446:layer:AWSLambdaPowertoolsPython:3",
        )
        worker_lambda = aws_lambda.Function(
            self, "WorkerLambda", layers=[powertools_layer], **self.__build_lambda_param("worker.handler")
        )
        worker_lambda.add_event_source(aws_lambda_event_sources.SqsEventSource(consume_queue))
        consume_queue.grant_consume_messages(worker_lambda)

    def __build_lambda_param(self, handler: str):
        """
        Lambdaの共有な設定
        """
        return dict(
            code=aws_lambda.Code.from_asset(str(pathlib.Path(__file__).resolve().parent.joinpath("runtime"))),
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler=handler,
        )
