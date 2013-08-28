"""
Readers module
"""

NEWLINE_CHAR = u'\n'


class ParagraphReader(object):
    def __init__(self, stream):
        self.stream = stream
        self.paragraph_buffer = u""
        self.is_paragraph_buffered = False
        self.is_line_truncated = False
        self.is_next_paragraph_empty = False

    def _strip_ending(self, line):
        if not line:
            return line
        for i, c in enumerate(reversed(line)):
            if c not in (u'\n', u'\r'):
                break
        else:
            i += 1
        line = line[:-i]
        return line

    def _concat_lines(self, line, next_line):
        if not (line and next_line):
            return line or next_line
        if line[-1].isspace() or next_line[0].isspace():
            line += next_line
        else:
            line += u" " + next_line
        return line

    def _finalize_buffered_paragraph(self, keepends):
        self.paragraph_buffer = self.paragraph_buffer.rstrip()
        if keepends:
            self.paragraph_buffer += NEWLINE_CHAR
        self.is_paragraph_buffered = True

    def read(self, length=None, keepends=True):
        """Read one paragraph from the input stream."""

        if length is not None and length < 0:
            raise ValueError("The length argument could not be negative.")

        while True:
            if self.is_paragraph_buffered:
                # The current paragraph is buffered, stop reading
                break
            if length is not None and length < len(self.paragraph_buffer):
                # The paragraph buffer contains enough characters for the request.
                # NOTE: Reserve at least one character to do a correct line concatenation.
                break
            line = self.stream.readline(length)
            if not line:
                # The input stream is exhausted, finish the last paragraph
                if self.paragraph_buffer:
                    self._finalize_buffered_paragraph(keepends)
                break
            truncated = True
            if line.endswith((u'\n', u'\r')):
                # Finished reading the current line
                truncated = False
                line = self._strip_ending(line)
                if not line and not self.is_line_truncated:
                    # An empty line indicates the end of the current paragraph
                    if self.paragraph_buffer:
                        # The buffer contains the remaining data of the current paragraph,
                        # so keep in mind that the next paragraph should be empty.
                        self.is_next_paragraph_empty = True
                    self._finalize_buffered_paragraph(keepends)
                    break
            if self.is_line_truncated:
                # Previous call truncated the line
                self.paragraph_buffer += line
            else:
                self.paragraph_buffer = self._concat_lines(self.paragraph_buffer, line)
            self.is_line_truncated = truncated
        # Extract data from the buffer
        if length is not None:
            paragraph = self.paragraph_buffer[:length]
            self.paragraph_buffer = self.paragraph_buffer[length:]
        else:
            paragraph = self.paragraph_buffer
            self.paragraph_buffer = u""
        if not self.paragraph_buffer:
            self.is_paragraph_buffered = False
            if self.is_next_paragraph_empty:
                self._finalize_buffered_paragraph(keepends)
                self.is_next_paragraph_empty = False
        return paragraph
