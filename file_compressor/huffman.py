import heapq
from collections import Counter
from pathlib import Path
import pickle


class HuffmanNode:
    def __init__(self, char=None, freq=0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


class HuffmanCoding:
    """
    Huffman Coding with proper level-based compression
    """

    def build_tree(self, frequency):
        """Build Huffman tree from frequency dictionary"""
        if not frequency:
            return None

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
        """Generate Huffman codes from tree"""
        codes = {}

        def dfs(node, code):
            if not node:
                return
            if node.char is not None:
                codes[node.char] = code or "0"
                return
            dfs(node.left, code + '0')
            dfs(node.right, code + '1')

        dfs(root, '')
        return codes

    def compress(self, input_path, output_path, level=6):
        """
        Level-aware Huffman compression
        
        level:
        1 = Fast (character-level only)
        6 = Balanced (character + common bigrams)
        9 = Max (character + bigrams + trigrams)
        """
        
        text = Path(input_path).read_text(encoding='utf-8')
        
        if not text:
            Path(output_path).write_bytes(b'')
            return

        # Build frequency based on compression level
        if level <= 1:  # Fast - just characters
            frequency = Counter(text)
            encoding_units = list(text)
            
        elif level <= 6:  # Balanced - characters + common bigrams
            frequency = Counter(text)
            
            # Add bigrams for better compression
            bigrams = [text[i:i+2] for i in range(len(text)-1)]
            bigram_freq = Counter(bigrams)
            
            # Only use bigrams that appear frequently enough
            threshold = max(2, len(text) // 500)
            for bigram, freq in bigram_freq.items():
                if freq >= threshold:
                    frequency[bigram] = freq
            
            # Build encoding units (prefer bigrams where beneficial)
            encoding_units = []
            i = 0
            while i < len(text):
                if i < len(text) - 1:
                    bigram = text[i:i+2]
                    if bigram in frequency and frequency[bigram] >= threshold:
                        encoding_units.append(bigram)
                        i += 2
                        continue
                encoding_units.append(text[i])
                i += 1
                
        else:  # Max - characters + bigrams + trigrams
            frequency = Counter(text)
            
            # Add bigrams
            bigrams = [text[i:i+2] for i in range(len(text)-1)]
            bigram_freq = Counter(bigrams)
            threshold_2 = max(2, len(text) // 500)
            
            for bigram, freq in bigram_freq.items():
                if freq >= threshold_2:
                    frequency[bigram] = freq
            
            # Add trigrams for even better compression
            trigrams = [text[i:i+3] for i in range(len(text)-2)]
            trigram_freq = Counter(trigrams)
            threshold_3 = max(2, len(text) // 300)
            
            for trigram, freq in trigram_freq.items():
                if freq >= threshold_3:
                    frequency[trigram] = freq
            
            # Build encoding units (prefer longer n-grams)
            encoding_units = []
            i = 0
            while i < len(text):
                if i < len(text) - 2:
                    trigram = text[i:i+3]
                    if trigram in frequency and frequency[trigram] >= threshold_3:
                        encoding_units.append(trigram)
                        i += 3
                        continue
                        
                if i < len(text) - 1:
                    bigram = text[i:i+2]
                    if bigram in frequency and frequency[bigram] >= threshold_2:
                        encoding_units.append(bigram)
                        i += 2
                        continue
                        
                encoding_units.append(text[i])
                i += 1

        # Build Huffman tree and codes
        root = self.build_tree(frequency)
        codes = self.build_codes(root)

        # Encode the text
        encoded_bits = ''.join(codes[unit] for unit in encoding_units)

        # Add padding
        padding = (8 - len(encoded_bits) % 8) % 8
        encoded_bits += '0' * padding

        # Convert to bytes
        byte_array = bytearray()
        
        # Store the tree and padding info for decompression
        header = {
            'padding': padding,
            'tree': root,
            'level': level
        }
        
        header_bytes = pickle.dumps(header)
        header_size = len(header_bytes)
        
        # Write: [header_size(4 bytes)][header][encoded_data]
        byte_array.extend(header_size.to_bytes(4, 'big'))
        byte_array.extend(header_bytes)
        
        # Add encoded bits
        for i in range(0, len(encoded_bits), 8):
            byte_array.append(int(encoded_bits[i:i + 8], 2))

        Path(output_path).write_bytes(byte_array)

    def decompress(self, input_path, output_path):
        """Decompress a Huffman-encoded file"""
        data = Path(input_path).read_bytes()
        
        if not data:
            Path(output_path).write_text('', encoding='utf-8')
            return
        
        # Read header
        header_size = int.from_bytes(data[:4], 'big')
        header = pickle.loads(data[4:4+header_size])
        
        padding = header['padding']
        root = header['tree']
        
        # Read encoded data
        encoded_data = data[4+header_size:]
        
        # Convert to bits
        bits = ''.join(f'{byte:08b}' for byte in encoded_data)
        
        # Remove padding
        if padding > 0:
            bits = bits[:-padding]
        
        # Decode
        decoded = []
        node = root
        
        for bit in bits:
            node = node.left if bit == '0' else node.right
            
            if node.char is not None:
                decoded.append(node.char)
                node = root
        
        Path(output_path).write_text(''.join(decoded), encoding='utf-8')