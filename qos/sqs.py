import time
import typing as t
from collections import deque

# from kombu.transport.SQS import QoS

T_QueueItem = t.Tuple[t.Any, str]


class DataGetter:
    def __init__(self, message: t.Any):
        self.message = message

    def get_group_id(self) -> t.AnyStr:
        return self.message.properties.get('MessageGroupId', '')

    def get_message_correlation_id(self) -> t.AnyStr:
        return self.message.properties.get('delivery_tag', str(time.time()))


class StandaloneGroupedQueue(dict[t.AnyStr, deque]):
    __info_getter__ = DataGetter

    def has_messages_in_group(self, message: t.Any) -> bool:
        return self.group_size(self.get_message_group_id(message)) > 0

    def add_message(self, message: t.Any, delivery_tag: t.AnyStr) -> int:
        gid = self.get_message_group_id(message)
        if gid not in self:
            super().__setitem__(gid, deque())
        self.get(gid).append((message, delivery_tag))
        return self.group_size(gid)

    def pop_message(self, message: t.AnyStr) -> t.Optional[T_QueueItem]:
        gid = self.get_message_group_id(message)
        item = self.pop(gid)
        if not item:
            return None
        if self.get_message_correlation_id(message) != self.get_message_correlation_id(item[0]):
            raise ValueError(f"Message correlation id mismatch: {message} != {item[0]}")
        return item

    def group_size(self, gid: t.AnyStr) -> int:
        return len(self.get(gid, []))

    def get_message_group_id(self, message: t.Any) -> t.AnyStr:
        return self.__info_getter__(message).get_group_id()

    def get_message_correlation_id(self, message: t.Any) -> t.AnyStr:
        return self.__info_getter__(message).get_message_correlation_id()

    def pop(self, gid: t.AnyStr) -> t.Optional[T_QueueItem]:
        if self.group_size(gid) == 0:
            return None
        item = self.get(gid).popleft()
        if self.group_size(gid) == 0:
            self.delete_group(gid)
        return item

    def select_next_message(self, gid: t.AnyStr) -> t.Optional[T_QueueItem]:
        if self.group_size(gid) == 0:
            return None
        return self.get(gid)[0]

    def is_next_message(self, message: t.Any) -> bool:
        gid = self.get_message_group_id(message)
        return self.get_message_correlation_id(message) == self.get_message_correlation_id(self.select_next_message(gid)[0])

    def delete_group(self, gid: t.AnyStr) -> None:
        super().__delitem__(gid)


# FIXME:
def make_basic_consume_function(channel, callback, queue, no_ack,
                                on_message_scheduled: t.Callable = None) -> t.Callable:
    if not on_message_scheduled:
        on_message_scheduled = lambda _: None

    def _callback(raw_message):
        message = channel.Message(raw_message, channel=channel)
        if not no_ack:
            qos = channel.qos
            # If scheduled message just execute the callback
            try:
                message = qos.get(message.delivery_tag)
                callback(message)
            except KeyError:
                pass
            # Schedule for execution
            qos.append(message, message.delivery_tag)
            if qos.is_fifo(queue):
                # if fifo use group id to schedule or execute if current message is next
                channel.qos.fifo_schedule(message, message.delivery_tag)
                if not channel.qos.fifo_is_next_mesage(message):
                    return on_message_scheduled(message)
        return callback(message)

    return _callback
#
# class ExtendedSQSQoS(QoS):
#     """
#     ExtendedSQSQoS is a subclass of QoS that implements a GroupedQueue to manage
#     """
#     q: StandaloneGroupedQueue = StandaloneGroupedQueue()
#
#     def append(self, message, delivery_tag):
#         return super().append(message, delivery_tag)
#
#     def ack(self, delivery_tag):
#         return super().ack(delivery_tag)
#
#     def get(self, delivery_tag):
#         return super().get(delivery_tag)
#
# # TODO: monkey patch kombu.transport.SQS.QoS with ExtendedSQSQoS
# # QoS = ExtendedSQSQoS
