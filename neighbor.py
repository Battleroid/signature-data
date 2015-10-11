import operator


class Neighbor(object):
    """Used for comparing and determining neighbors.

    Used to compare against a base list of data against its relatives using
    a maximum distance and given operation to determine if it is a neighbor to
    the base observation.
    
    Args:
        data (List[int]): List of data to use as base for comparisons.
        maximum_distance (int): Maximum distance the result may still be
            considered a neighbor. Default is 1.
        operation: Operation from :py:class:`operator` to check data against.
            Default is :py:func:`operator.le`.
    """
    def __init__(self, data, maximum_distance=1, operation=operator.le):
        self.data = data
        self.maximum_distance = maximum_distance
        self.operation = operation

    def diff(self, opposing):
        """Return absolute distance of opposing set of data against base set.
        """
        return list(map(lambda x, y: abs(operator.sub(x, y)), self.data, opposing))

    def check(self, opposing):
        """Return whether or not the opposing set is a neighbor.

        Args:
            Opposing (List[int]): Set of data to check against.

        Returns:
            bool: Whether or not the observation is a neighbor. Always returns
                True if opposing data equals the base data (checking itself).
        """
        if opposing != self.data:
            # It is not itself, therefore check to see if it is a neighbor.
            r = self.diff(opposing)
            s = sum(r)
            t = 0
            for _ in r:
                if _ != 0:
                    t += 1
            st = float(s) / float(t)
            return self.operation(st, self.maximum_distance)
        else:
            # If it is itself, it is a neighbor to itself.
            return True
