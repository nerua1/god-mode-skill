#!/usr/bin/env python3
"""
God Mode - Text Obfuscation Tool
Parseltongue encoder for OpenClaw
"""

import sys
import base64
import argparse

# Character mappings
LEET_BASIC = {
    'a': '4', 'e': '3', 'i': '1', 'o': '0',
    's': '5', 't': '7', 'l': '1', 'g': '9', 'b': '8'
}

LEET_HEAVY = {
    'a': '@', 'e': '3', 'i': '!', 'o': '0', 's': '$',
    't': '7', 'l': '1', 'g': '9', 'b': '8',
    'c': '(', 'k': '|<', 'h': '#', 'x': '%'
}

UNICODE_MAP = {
    'a': 'а', 'c': 'с', 'e': 'е', 'o': 'о',
    'p': 'р', 'x': 'х', 'y': 'у'
}

BUBBLE_MAP = {
    'a': 'ⓐ', 'b': 'ⓑ', 'c': 'ⓒ', 'd': 'ⓓ', 'e': 'ⓔ',
    'f': 'ⓕ', 'g': 'ⓖ', 'h': 'ⓗ', 'i': 'ⓘ', 'j': 'ⓙ',
    'k': 'ⓚ', 'l': 'ⓛ', 'm': 'ⓜ', 'n': 'ⓝ', 'o': 'ⓞ',
    'p': 'ⓟ', 'q': 'ⓠ', 'r': 'ⓡ', 's': 'ⓢ', 't': 'ⓣ',
    'u': 'ⓤ', 'v': 'ⓥ', 'w': 'ⓦ', 'x': 'ⓧ', 'y': 'ⓨ', 'z': 'ⓩ'
}

MATH_BOLD = {
    'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞',
    'f': '𝐟', 'g': '𝐠', 'h': '𝐡', 'i': '𝐢', 'j': '𝐣',
    'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧', 'o': '𝐨',
    'p': '𝐩', 'q': '𝐪', 'r': '𝐫', 's': '𝐬', 't': '𝐭',
    'u': '𝐮', 'v': '𝐯', 'w': '𝐰', 'x': '𝐱', 'y': '𝐲', 'z': '𝐳'
}

FULLWIDTH_MAP = {
    'a': 'ａ', 'b': 'ｂ', 'c': 'ｃ', 'd': 'ｄ', 'e': 'ｅ',
    'f': 'ｆ', 'g': 'ｇ', 'h': 'ｈ', 'i': 'ｉ', 'j': 'ｊ',
    'k': 'ｋ', 'l': 'ｌ', 'm': 'ｍ', 'n': 'ｎ', 'o': 'ｏ',
    'p': 'ｐ', 'q': 'ｑ', 'r': 'ｒ', 's': 'ｓ', 't': 'ｔ',
    'u': 'ｕ', 'v': 'ｖ', 'w': 'ｗ', 'x': 'ｘ', 'y': 'ｙ', 'z': 'ｚ'
}

def leetspeak(text, heavy=False):
    """Convert to leetspeak"""
    mapping = LEET_HEAVY if heavy else LEET_BASIC
    return ''.join(mapping.get(c.lower(), c) for c in text)

def unicode_obfuscate(text):
    """Replace with cyrillic homoglyphs"""
    return ''.join(UNICODE_MAP.get(c.lower(), c) for c in text)

def bubble(text):
    """Convert to bubble letters"""
    return ''.join(BUBBLE_MAP.get(c.lower(), c) for c in text)

def spaced(text):
    """Add spaces between characters"""
    return ' '.join(text)

def fullwidth(text):
    """Convert to fullwidth characters"""
    return ''.join(FULLWIDTH_MAP.get(c.lower(), c) for c in text)

def mixed_case(text):
    """Alternate case"""
    return ''.join(c.upper() if i % 2 == 0 else c.lower() 
                   for i, c in enumerate(text))

def reversed_text(text):
    """Reverse text"""
    return text[::-1]

def base64_encode(text):
    """Base64 encode"""
    return base64.b64encode(text.encode()).decode()

def hex_encode(text):
    """Hex encode"""
    return ' '.join(f'0x{ord(c):02x}' for c in text)

def math_bold(text):
    """Math bold characters"""
    return ''.join(MATH_BOLD.get(c.lower(), c) for c in text)

def obfuscate(text, method='unicode'):
    """Apply obfuscation method"""
    methods = {
        'leet': lambda t: leetspeak(t),
        'leet-heavy': lambda t: leetspeak(t, heavy=True),
        'unicode': unicode_obfuscate,
        'bubble': bubble,
        'spaced': spaced,
        'fullwidth': fullwidth,
        'mixed': mixed_case,
        'reversed': reversed_text,
        'base64': base64_encode,
        'hex': hex_encode,
        'math-bold': math_bold,
    }
    
    if method not in methods:
        raise ValueError(f"Unknown method: {method}. Available: {list(methods.keys())}")
    
    return methods[method](text)

def main():
    parser = argparse.ArgumentParser(description='God Mode Text Obfuscator')
    parser.add_argument('text', help='Text to obfuscate')
    parser.add_argument('-m', '--method', default='unicode',
                       choices=['leet', 'leet-heavy', 'unicode', 'bubble', 
                               'spaced', 'fullwidth', 'mixed', 'reversed',
                               'base64', 'hex', 'math-bold'],
                       help='Obfuscation method')
    parser.add_argument('-l', '--list', action='store_true',
                       help='List available methods')
    
    args = parser.parse_args()
    
    if args.list:
        print("Available methods:")
        for m in ['leet', 'leet-heavy', 'unicode', 'bubble', 'spaced', 
                  'fullwidth', 'mixed', 'reversed', 'base64', 'hex', 'math-bold']:
            print(f"  - {m}")
        return
    
    result = obfuscate(args.text, args.method)
    print(result)

if __name__ == '__main__':
    main()
