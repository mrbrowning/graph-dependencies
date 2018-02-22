import itertools


class DependencyTrie:

    def __init__(self):
        self.root = DependencyTrieNode(None)

    def _add(self, path):
        current_node = self.root

        for current_value in path:
            child_node = current_node.get_child(current_value)

            if child_node is None:
                child_node = DependencyTrieNode(current_value, current_node)
                current_node.add_child(child_node)

            current_node = child_node

    def _get(self, path):
        current_node = self.root

        for current_value in path:
            child_node = current_node.get_child(current_value)

            if child_node is None:
                return None
            current_node = child_node

        return current_node

    def __iter__(self):
        return DependencyTrieIterator(self)


class DependencyTrieNode:

    def __init__(self, value, parent=None):
        self.value = value
        self.parent = parent
        self.children = {}
        self.dependencies = {}
        self.path = parent.path + [self.value] if parent is not None else []

    def add_child(self, child):
        self.children[child.value] = child

    def _add_dependency(self, dependency):
        self.dependencies[dependency.qualified_value] = dependency

    def add_dependency(self, dependency):
        self._add_dependency(dependency)
        common_ancestor = _most_recent_common_ancestor(self, dependency)

        # Whether this node is a class or package, we consider any ancestor packagees of the
        # dependent up to but not including their common ancestor as dependents themselves.
        # Since _add_dependency is idempotent, we can put the current dependency in this list
        # to make things easier later.
        ancestor_dependents = []
        current_node = dependency
        while current_node != common_ancestor:
            ancestor_dependents.append(current_node)
            current_node = current_node.parent

        # Packages also have as dependencies any dependencies of their children, up to but not
        # including the common ancestor of depender and dependent.
        current_node = self
        while current_node != common_ancestor:
            for d in ancestor_dependents:
                current_node._add_dependency(d)
            current_node = current_node.parent

    def get_child(self, value):
        return self.children.get(value)

    @property
    def qualified_value(self):
        return tuple(self.path)

    def __iter__(self):
        return iter(self.children.values())

    def __eq__(self, other):
        return self.qualified_value == other.qualified_value
 

class DependencyTrieIterator:

    def __init__(self, trie):
        self.trie = trie
        self.next_nodes = iter([trie.root])

    def __next__(self):
        next_node = next(self.next_nodes)
        self.next_nodes = itertools.chain(self.next_nodes, iter(next_node))

        return (
            next_node.qualified_value,
            tuple([n.qualified_value for n in next_node.dependencies.values()])
        )


def _most_recent_common_ancestor(node1, node2):
    current_node, other_node = node1, node2

    while True:
        if len(other_node.qualified_value) > len(current_node.qualified_value):
            current_node, other_node = other_node, current_node

        while len(current_node.qualified_value) > len(other_node.qualified_value):
            if current_node.parent is None:
                return current_node

            current_node = current_node.parent

        if current_node == other_node or current_node.parent is None:
            return current_node

        current_node = current_node.parent


def _get_path_from_filename(filename):
    return filename.split('.')[0].split('/')


def from_file_dependencies(dependencies):
    trie = DependencyTrie()

    for depender, dependents in dependencies.items():
        trie._add(_get_path_from_filename(depender))

        for d in dependents:
            trie._add(_get_path_from_filename(d))

    for i, (depender, dependents) in enumerate(dependencies.items()):
        depender_node = trie._get(_get_path_from_filename(depender))

        for j, d in enumerate(dependents):
            depender_node.add_dependency(trie._get(_get_path_from_filename(d)))

    return trie
