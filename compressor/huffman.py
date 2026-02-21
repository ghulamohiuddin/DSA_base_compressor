import heapq
from collections import Counter
from pathlib import Path

# -----------------------------
# DSA: TREE NODE
# -----------------------------
class HuffmanNode:
    def __init__(self, char=None, freq=0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    # Required for Priority Queue
    def __lt__(self, other):
        return self.freq < other.freq


# -----------------------------
# DSA: HUFFMAN CODING
# -----------------------------
class HuffmanCoding:

    def build_tree(self, text):
        frequency = Counter(text)

        # Priority Queue (Min Heap)
        heap = [HuffmanNode(ch, freq) for ch, freq in frequency.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)

            merged = HuffmanNode(freq=left.freq + right.freq)
            merged.left = left
            merged.right = right

            heapq.heappush(heap, merged)

        return heap[0]

    def build_codes(self, root):
        codes = {}

        def dfs(node, code):
            if not node:
                return
            if node.char:
                codes[node.char] = code
            dfs(node.left, code + "0")
            dfs(node.right, code + "1")

        dfs(root, "")
        return codes

    def compress(self, input_path, output_path):
        text = Path(input_path).read_text()

        root = self.build_tree(text)
        codes = self.build_codes(root)

        encoded = ''.join(codes[ch] for ch in text)

        padding = 8 - len(encoded) % 8
        encoded += '0' * padding
        encoded = f"{padding:08b}" + encoded

        byte_array = bytearray(
            int(encoded[i:i+8], 2) for i in range(0, len(encoded), 8)
        )

        Path(output_path).write_bytes(byte_array)
        return codes

    def decompress(self, compressed_path, output_path, codes):
        reverse_codes = {v: k for k, v in codes.items()}
        bits = ""

        for byte in Path(compressed_path).read_bytes():
            bits += f"{byte:08b}"

        padding = int(bits[:8], 2)
        bits = bits[8:-padding]

        current = ""
        decoded = ""

        for bit in bits:
            current += bit
            if current in reverse_codes:
                decoded += reverse_codes[current]
                current = ""

        Path(output_path).write_text(decoded)
