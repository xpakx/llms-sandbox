import requests
from selectolax.parser import HTMLParser
from typing import List


def get_direct_children(root_node):
    direct_children = []
    child = root_node.child
    while child: 
        if child.tag != '-text':
            direct_children.append(child) 
        child = child.next 
    return direct_children


def get_page(url: str) -> HTMLParser:
      response = requests.get(url)
      response.raise_for_status()
      return HTMLParser(response.text)


def fetch_skeleton_html(html: HTMLParser, ignore: List[str]) -> str:
  try:
      def _process_node(node): 
          if node.tag in ignore:
              return ""

          tag_name = node.tag
          attributes = ''.join([f' {k}="{v}"' for k, v in node.attributes.items()]) if node.attributes else ''
          opening_tag = f"<{tag_name}{attributes}>"
          closing_tag = f"</{tag_name}>"

          children = get_direct_children(node)
          children_content = "".join([_process_node(child) for child in children]) 

          return opening_tag + children_content + closing_tag 

      return _process_node(html.body) 
  except requests.exceptions.RequestException as e:
      print(f"error : {e}") 
      return "" 
  except Exception as e:
      print(f"error : {e}") 
      return "" 

def extract_content(html: HTMLParser, data):
    title = html.body.css(data.title);
    content = html.body.css(data.content);
    if isinstance(title, list):
        title = title[0].text() if len(title) > 0 else ""
    else:
        title = title.text()
    if isinstance(content, list):
        content = content[0].html if len(content) > 0 else ""
    else:
        content = content.html
    return {
            "title": title,
            "content": content
            }
