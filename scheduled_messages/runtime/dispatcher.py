import json
import os
from dataclasses import asdict, dataclass

import boto3

sqs = boto3.resource("sqs")
queue = sqs.get_queue_by_name(QueueName=os.getenv("SQS_NAME"))

MAX_NUMBER_OF_ENTRIES = 10  # １回のキューに送信できる最大数
NUMBER_OF_SAMPLE_ITEMS = 20  # 動作確認でキューにプッシュするアイテムの数


def handler(event, context):
    for entries in get_entries():
        queue.send_messages(Entries=entries)


def get_entries():
    """
    普通のユースケースだとDBから送信対象を取ってくる感じだけれども、
    ここでは適当なデータを作るだけ
    """

    @dataclass
    class SampleItem:
        """Queueに送信するサンプルデータ"""

        user_id: int
        message: str

        def convert_entry(self):
            """`send_messages`のエンティティのフォーマットに変形する"""
            return {"Id": f"{self.user_id}", "MessageBody": json.dumps(asdict(self))}

    items_to_send = [SampleItem(i, f"メッセージ_{i}") for i in range(NUMBER_OF_SAMPLE_ITEMS)]

    entries = []
    for item in items_to_send:
        entries.append(item.convert_entry())
        if len(entries) == MAX_NUMBER_OF_ENTRIES:
            yield entries
            entries.clear()
