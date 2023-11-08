import logging
import re
import markdownify
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from llm_bot_dep.splitter_utils import MarkdownHeaderTextSplitter

logger = logging.getLogger(__name__)


class CustomHtmlLoader(BaseLoader):
    """Load `HTML` files using `Unstructured`.

    You can run the loader in one of two modes: "single" and "elements".
    If you use "single" mode, the document will be returned as a single
    langchain Document object. If you use "elements" mode, the unstructured
    library will split the document into elements such as Title and NarrativeText.
    You can pass in additional unstructured kwargs after mode to apply
    different unstructured settings.

    """

    def clean_html(self, html_str: str) -> str:
        # Filter out DOCTYPE
        html_str = ' '.join(html_str.split())
        re_doctype = re.compile(r'<!DOCTYPE .*?>', re.S)
        s = re_doctype.sub('', html_str)

        # Filter out CDATA
        re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)
        s = re_cdata.sub('', s)

        # Filter out script
        re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)
        s = re_script.sub('', s)

        # Filter out style
        re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)
        s = re_style.sub('', s)

        # Filter out HTML comments
        re_comment = re.compile('<!--[^>]*-->')
        s = re_comment.sub('', s)

        # Remove extra blank lines
        blank_line = re.compile('\n+')
        s = blank_line.sub('\n', s)

        return s.strip()

    # def load(self, file_content: str) -> List[Document]:
    def load(self, file_content: str):
        file_content = self.clean_html(file_content)
        file_content = markdownify.markdownify(file_content)
        doc = Document(page_content=file_content,
                       metadata={"file_type": "html"})

        return doc


def process_html(html_str: str, **kwargs):
    loader = CustomHtmlLoader()
    doc = loader.load(html_str)
    splitter = MarkdownHeaderTextSplitter()
    doc_list = splitter.split_text(doc)

    return doc_list
