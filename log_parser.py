
def parse_log_file(log_text: str, max_chunk_lines: int = 30) -> list:
    """
    Parses the MySQL log content into smaller chunks suitable for LLM analysis.

    Parameters:
        log_text (str): Full content of the uploaded MySQL log.
        max_chunk_lines (int): Number of lines per chunk (default: 30).

    Returns:
        List[str]: List of log chunks (each a multi-line string).
    """
    # 1. Split the log into lines
    lines = log_text.splitlines()

    # 2. Filter out empty lines and comments
    clean_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]

    # 3. Group lines into chunks of max_chunk_lines
    chunks = []
    for i in range(0, len(clean_lines), max_chunk_lines):
        chunk = "\n".join(clean_lines[i:i + max_chunk_lines])
        chunks.append(chunk)

    return chunks
