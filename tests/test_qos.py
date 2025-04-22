import unittest

from qos.sqs import StandaloneGroupedQueue


class FakeMessage:
    """
    Simulates a message with a `properties` dict.
    """

    def __init__(self, group_id: str, correlation_id: str = None):
        self.properties = {
            'MessageGroupId': group_id,
            'correlation_id': correlation_id
        }


class TestStandaloneGroupedQueue(unittest.TestCase):

    def setUp(self):
        self.queue = StandaloneGroupedQueue()

    def test_add_and_pop_message(self):
        """
        Verify basic add/pop of a single message in the queue.
        """
        msg = FakeMessage(group_id="group1", correlation_id="corr1")
        self.assertFalse(self.queue.has_messages_in_group(msg))
        self.queue.add_message(msg, "tag1")
        self.assertTrue(self.queue.has_messages_in_group(msg))

        item = self.queue.pop_message(msg)
        self.assertIsNotNone(item)
        popped_msg, popped_tag = item
        self.assertIs(popped_msg, msg)
        self.assertEqual(popped_tag, "tag1")
        self.assertFalse(self.queue.has_messages_in_group(msg))

    def test_correlation_id_mismatch(self):
        """
        Confirm ValueError is raised when correlation IDs differ.
        """
        real_msg = FakeMessage(group_id="group1", correlation_id="corr1")
        self.queue.add_message(real_msg, "tag1")

        # Attempt to pop with a different correlation ID
        fake_msg = FakeMessage(group_id="group1", correlation_id="corr2")
        with self.assertRaises(ValueError):
            self.queue.pop_message(fake_msg)

    def test_multiple_messages_same_group(self):
        """
        Ensure multiple messages in the same group pop in FIFO order.
        """
        msg1 = FakeMessage(group_id="group1", correlation_id="corr1")
        msg2 = FakeMessage(group_id="group1", correlation_id="corr2")

        self.queue.add_message(msg1, "tag1")
        self.queue.add_message(msg2, "tag2")

        popped1 = self.queue.pop_message(msg1)
        self.assertEqual(popped1[0], msg1)
        self.assertEqual(popped1[1], "tag1")

        popped2 = self.queue.pop_message(msg2)
        self.assertEqual(popped2[0], msg2)
        self.assertEqual(popped2[1], "tag2")

        self.assertFalse(self.queue.has_messages_in_group(msg1))
        self.assertFalse(self.queue.has_messages_in_group(msg2))

    def test_delete_group(self):
        """
        Confirm groups can be removed explicitly.
        """
        msg = FakeMessage(group_id="groupX", correlation_id="cx")
        self.queue.add_message(msg, "t1")
        gid = self.queue.get_message_group_id(msg)
        self.assertIn(gid, self.queue)

        self.queue.delete_group(gid)
        self.assertNotIn(gid, self.queue)

    def test_pop_nonexistent_group(self):
        """
        Popping from a non-existent group should return None.
        """
        item = self.queue.pop("does_not_exist")
        self.assertIsNone(item)

    # -----------------------------------
    # Additional Tests
    # -----------------------------------

    def test_multiple_messages_different_groups(self):
        """
        Check that messages in different groups don't affect each other.
        """
        msg1 = FakeMessage(group_id="A", correlation_id="corrA1")
        msg2 = FakeMessage(group_id="B", correlation_id="corrB1")

        self.queue.add_message(msg1, "tagA1")
        self.queue.add_message(msg2, "tagB1")

        # Each message should only affect its own group
        self.assertTrue(self.queue.has_messages_in_group(msg1))
        self.assertTrue(self.queue.has_messages_in_group(msg2))

        popped1 = self.queue.pop_message(msg1)
        self.assertEqual(popped1[0], msg1)
        popped2 = self.queue.pop_message(msg2)
        self.assertEqual(popped2[0], msg2)

    def test_group_size(self):
        """
        Verify group_size returns correct counts.
        """
        msgA1 = FakeMessage(group_id="A", correlation_id="corrA1")
        msgA2 = FakeMessage(group_id="A", correlation_id="corrA2")
        gidA = self.queue.get_message_group_id(msgA1)

        self.queue.add_message(msgA1, "tagA1")
        self.queue.add_message(msgA2, "tagA2")

        self.assertEqual(self.queue.group_size(gidA), 2)

    def test_get_message_group_id(self):
        """
        Ensure get_message_group_id returns the correct group_id.
        """
        msg = FakeMessage(group_id="TestGroup", correlation_id="corrTest")
        gid = self.queue.get_message_group_id(msg)
        self.assertEqual(gid, "TestGroup")

    def test_get_message_correlation_id(self):
        """
        Ensure get_message_correlation_id returns correlation ID or default value.
        """
        msg = FakeMessage(group_id="G", correlation_id="corrG")
        cid = self.queue.get_message_correlation_id(msg)
        self.assertEqual(cid, "corrG")

    def test_delete_group_with_messages_in_it(self):
        """
        Verify deleting a group that still has messages removes everything.
        """
        msg = FakeMessage(group_id="X", correlation_id="corrX")
        self.queue.add_message(msg, "tX1")
        gid = self.queue.get_message_group_id(msg)
        self.assertIn(gid, self.queue)
        self.queue.delete_group(gid)
        self.assertNotIn(gid, self.queue)

    def test_pop_with_empty_group(self):
        """
        Ensure popping from an empty group returns None.
        """
        msg = FakeMessage(group_id="GG", correlation_id="gg1")
        gid = self.queue.get_message_group_id(msg)
        # Create the group with no messages
        self.queue[gid] = []
        popped = self.queue.pop(gid)
        self.assertIsNone(popped)


