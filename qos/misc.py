
class GroupedQueue(dict[t.AnyStr, deque]):
    gid_getter = DataGetter

    def append(self, message: t.Any, delivery_tag: t.AnyStr, group_id: t.AnyStr) -> None:
        if group_id not in self:
            super().__setitem__(group_id, deque())

        q: deque = super().__getitem__(group_id).append((message, delivery_tag))

    def pop(self, group_id: t.AnyStr) -> t.Optional[T_QueueItem]:
        if group_id not in self:
            return None

        queue = super().__getitem__(group_id)
        item = queue.popleft()
        if not queue:
            super().__delitem__(group_id)
        return item

    def delete_group(self, group_id: t.AnyStr) -> None:
        if group_id in self:
            super().__delitem__(group_id)

    def size(self, group_id: t.AnyStr) -> int:
        return len(self.get(group_id, []))

    def __setitem__(self, delivery_tag: t.AnyStr, message: t.Any) -> None:
        group_id = self.gid_getter(message).get_group_id()
        self.append(message, delivery_tag, group_id)

    def __getitem__(self, delivery_tag: t.AnyStr) -> T_QueueItem:
        for gid, queue in self.items():
            for item in queue:
                if item[1] == delivery_tag:
                    return item
        raise KeyError(delivery_tag)

    def __del__(self, delivery_tag: t.AnyStr) -> None:
        for gid, queue in self.items():
            for item in queue:
                if item[1] == delivery_tag:
                    queue.remove(item)
                    if self.size(gid) == 0:
                        self.delete_group(gid)
                    return
        raise KeyError(delivery_tag)

    def __len__(self):
        return sum(len(group) for group in self.values())

