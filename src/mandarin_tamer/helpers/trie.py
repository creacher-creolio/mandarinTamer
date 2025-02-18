class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.value = None


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, value: str):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.value = value

    def find_all_matches(self, text: str) -> list[tuple[int, int, str]]:
        """Returns list of (start_idx, end_idx, replacement_value)"""
        matches = []
        for i in range(len(text)):
            node = self.root
            j = i
            while j < len(text) and text[j] in node.children:
                node = node.children[text[j]]
                if node.is_end:
                    matches.append((i, j + 1, node.value))
                j += 1
        return matches
