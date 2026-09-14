"""
DOCX Text Extraction Module for LexiTrap.
Extracts paragraphs, tables, and text runs from DOCX archives.
Uses standard library zipfile + xml.etree with python-docx fallback for maximum compatibility.
"""

import io
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, Union, List

# WordprocessingML XML namespaces
W_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS_MAP = {"w": W_NAMESPACE}


def _extract_text_from_xml_tree(root: ET.Element) -> Dict[str, Any]:
    """
    Parses OpenXML document tree to extract paragraphs and tables in order.
    """
    paragraphs_data = []
    text_parts = []
    tables_data = []

    # Iterate over body elements (paragraphs and tables)
    body = root.find("w:body", NS_MAP)
    if body is None:
        body = root

    for elem in body:
        tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        
        if tag_name == "p":
            # Extract all text nodes within this paragraph
            text_nodes = elem.findall(".//w:t", NS_MAP)
            p_text = "".join([t.text for t in text_nodes if t.text]).strip()
            
            if p_text:
                # Check for heading style if defined in pPr
                pStyle = elem.find(".//w:pPr/w:pStyle", NS_MAP)
                style_val = pStyle.attrib.get(f"{{{W_NAMESPACE}}}val", "Normal") if pStyle is not None else "Normal"
                is_heading = "Heading" in style_val or "Title" in style_val
                
                paragraphs_data.append({
                    "index": len(paragraphs_data),
                    "text": p_text,
                    "style": style_val,
                    "is_heading": is_heading
                })
                text_parts.append(p_text)

        elif tag_name == "tbl":
            # Extract table rows and cells
            table_matrix = []
            rows = elem.findall("w:tr", NS_MAP)
            for row in rows:
                cells = row.findall("w:tc", NS_MAP)
                row_cells = []
                for cell in cells:
                    cell_text_nodes = cell.findall(".//w:t", NS_MAP)
                    c_text = "".join([t.text for t in cell_text_nodes if t.text]).strip()
                    row_cells.append(c_text)
                if any(row_cells):
                    table_matrix.append(row_cells)
                    text_parts.append(" | ".join(row_cells))
            if table_matrix:
                tables_data.append(table_matrix)

    combined_text = "\n\n".join(text_parts)
    return {
        "text": combined_text,
        "paragraph_count": len(paragraphs_data),
        "table_count": len(tables_data),
        "paragraphs": paragraphs_data,
        "tables": tables_data,
        "extraction_method": "OpenXML (docx parser)"
    }


def extract_text_from_docx(
    file_input: Union[str, bytes, io.BytesIO]
) -> Dict[str, Any]:
    """
    Extracts text, paragraphs, and table contents from a DOCX file or bytes stream.
    """
    if isinstance(file_input, (bytes, bytearray)):
        stream = io.BytesIO(file_input)
    elif isinstance(file_input, io.BytesIO):
        stream = file_input
    elif isinstance(file_input, str):
        with open(file_input, "rb") as f:
            stream = io.BytesIO(f.read())
    else:
        raise ValueError("Invalid DOCX input. Must be filepath string, bytes, or BytesIO.")

    try:
        with zipfile.ZipFile(stream) as zf:
            if "word/document.xml" not in zf.namelist():
                raise ValueError("Invalid DOCX format: word/document.xml not found in archive.")
            
            xml_content = zf.read("word/document.xml")
            root = ET.fromstring(xml_content)
            return _extract_text_from_xml_tree(root)
    except Exception as e:
        raise ValueError(f"Failed to extract DOCX text: {str(e)}")
