import json

from aws_lambda_powertools.utilities.batch import sqs_batch_processor


def record_handler(record):
    print(f"メッセージを送るよ! :{json.dumps(record['body'])}")
    return


@sqs_batch_processor(record_handler=record_handler)
def handler(event, context):
    return
