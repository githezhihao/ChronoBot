import re
import pygments
from pygments import lexers, formatters

def render_markdown(text, escape_func=None):
    if escape_func:
        text = escape_func(text)
    code_blocks = []
    def pygments_codeblock(match):
        code = match.group(1)
        try:
            lexer = lexers.guess_lexer(code)
        except Exception:
            lexer = lexers.get_lexer_by_name('python')
        formatter = formatters.HtmlFormatter(noclasses=True, style='default', linenos=True)  # 启用行号
        highlighted = pygments.highlight(code, lexer, formatter)
        code_blocks.append(highlighted)
        return f'__CODEBLOCK_{len(code_blocks)-1}__'
    # 提取代码块并替换为占位符
    text = re.sub(r'```([\s\S]*?)```', pygments_codeblock, text)
    # 行内代码
    text = re.sub(r'`([^`]+)`', r'<span style="background:#f4f4f4;color:#c7254e;border-radius:4px;padding:2px 4px;font-family:monospace;">\\1</span>', text)
    # 只对非代码块部分做换行
    text = text.replace('\n', '<br>')
    # 恢复代码块
    for i, block in enumerate(code_blocks):
        text = text.replace(f'__CODEBLOCK_{i}__', block)
    return text
