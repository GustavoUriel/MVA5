import os
from html.parser import HTMLParser


class Node:
    def __init__(self, tag, attrs, parent=None):
        self.tag = tag
        self.attrs = dict(attrs)
        self.parent = parent
        self.children = []
        self.data = ''

    def add_child(self, node):
        self.children.append(node)


class DOMBuilder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = Node('root', {})
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, parent=self.stack[-1])
        self.stack[-1].add_child(node)
        if tag not in ('br', 'img', 'input', 'option'):
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                break

    def handle_data(self, data):
        if data.strip():
            self.stack[-1].data += data.strip()


def walk(node):
    yield node
    for c in node.children:
        yield from walk(c)


def find_labels(root):
    labels = {}
    for node in walk(root):
        if node.tag == 'label':
            fid = node.attrs.get('for')
            text = node.data or ' '.join(c.data for c in node.children if c.data)
            if fid:
                labels[fid] = text
    return labels


def get_selected_option(node):
    for c in node.children:
        if c.tag == 'option' and ('selected' in c.attrs or c.attrs.get('selected') == 'true'):
            return c.attrs.get('value') or c.data
    for c in node.children:
        if c.tag == 'option':
            return c.attrs.get('value') or c.data
    return ''


def build_map_from_html(html_path):
    with open(html_path, 'r', encoding='utf-8') as fh:
        data = fh.read()
    parser = DOMBuilder()
    parser.feed(data)
    root = parser.root
    labels = find_labels(root)

    out_lines = []

    def render(node, indent=0):
        pad = '\t' * indent
        if node.tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            text = node.data or ' '.join(c.data for c in node.children if c.data)
            out_lines.append(f"{pad}{text}")
        elif node.tag == 'span' and node.attrs.get('id') == 'editorTitle':
            out_lines.append(f"{pad}{node.data}")
        elif node.tag == 'input':
            itype = node.attrs.get('type', 'text')
            iid = node.attrs.get('id') or node.attrs.get('name') or ''
            name = node.attrs.get('name', '')
            val = node.attrs.get('value', '')
            checked = 'checked' if 'checked' in node.attrs else ''
            label = labels.get(iid, '')
            label_text = label or iid or f"input({itype})"
            if itype in ('checkbox', 'radio'):
                out_lines.append(f"{pad}{label_text}, {itype}, name: \"{name or iid}\", value: {val or checked}")
            else:
                out_lines.append(f"{pad}{label_text}, {itype}, name: \"{name or iid}\", value: \"{val}\"")
        elif node.tag == 'select':
            iid = node.attrs.get('id') or node.attrs.get('name') or ''
            name = node.attrs.get('name', '')
            sel = get_selected_option(node)
            label = labels.get(iid, '')
            label_text = label or iid or 'select'
            out_lines.append(f"{pad}{label_text}, select, name: \"{name or iid}\", value: \"{sel}\"")
        elif node.tag == 'button':
            text = node.data or 'button'
            out_lines.append(f"{pad}{text}, button")

        child_indent = indent
        if node.tag in ('div', 'section') and ('card' in (node.attrs.get('class') or '') or node.attrs.get('id')):
            child_indent = indent + 1

        for c in node.children:
            render(c, child_indent)

    # title
    for n in walk(root):
        if n.tag == 'span' and n.attrs.get('id') == 'editorTitle':
            out_lines.append(n.data)
            break

    for c in root.children:
        render(c, 0)

    return '\n'.join(out_lines)


if __name__ == '__main__':
    base = os.path.dirname(__file__)
    html_path = os.path.join(base, 'anaconf.html')
    out = build_map_from_html(html_path)
    out_path = os.path.join(base, 'map.txt')
    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write(out)
    print(out)
