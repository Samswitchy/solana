import re

def extract_token_address(message_text):
    match = re.search(r'([A-HJ-NP-Za-km-z1-9]{32,44})', message_text)
    return match.group(1) if match else None

def extract_token_name(message_text):
    match = re.search(r'\[([\w\s\-()]+)\]', message_text)
    return match.group(1) if match else None

def extract_x_link(message_text):
    x_pattern = r'\[𝕏\]\((https:\/\/x\.com\/[^\)]+)\)'  
    match = re.search(x_pattern, message_text)
    return match.group(1) if match else None
