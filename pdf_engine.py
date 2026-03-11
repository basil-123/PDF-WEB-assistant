"""
DocuMind AI — PDF Engine (Font-Aware Processing & Editing)
"""
import os
import re
import json
import tempfile
import streamlit as st
import fitz  # PyMuPDF
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP, DEFAULT_FONT, DEFAULT_FONT_SIZE, DEFAULT_FONT_COLOR


# ============================================================
# PDF LOADING & TEXT PROCESSING
# ============================================================
def process_pdf(file_bytes: bytes, file_name: str) -> list[Document]:
    """Loads a PDF and returns Document objects. Also stores bytes for editing."""
    if "pdf_bytes_store" not in st.session_state:
        st.session_state["pdf_bytes_store"] = {}
    st.session_state["pdf_bytes_store"][file_name] = file_bytes

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file_bytes)
        tmp_file_path = tmp_file.name

    loader = PyPDFLoader(tmp_file_path)
    docs = loader.load()
    for doc in docs:
        doc.metadata["source_file"] = file_name
        doc.metadata["source_type"] = "pdf"
    os.unlink(tmp_file_path)
    return docs


def process_text(text: str, name: str) -> list[Document]:
    """Wraps raw text into a Document."""
    return [Document(
        page_content=text,
        metadata={"source_type": "text", "source_file": name}
    )]


def chunk_documents(docs: list[Document]) -> list[Document]:
    """Splits documents into chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len
    )
    return splitter.split_documents(docs)


# ============================================================
# FONT EXTRACTION & DETECTION
# ============================================================
def _extract_embedded_fonts(doc) -> dict:
    """
    Extracts embedded font files (.ttf/.otf) from a PDF document.
    Returns a dict mapping font_name -> temp_file_path.
    """
    font_files = {}
    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            font_list = page.get_fonts(full=True)
            for font_info in font_list:
                # font_info: (xref, ext, type, basefont, name, encoding, ...)
                xref = font_info[0]
                ext = font_info[1]       # e.g. "ttf", "cff", "n/a"
                basefont = font_info[3]  # e.g. "ABCDEF+Calibri-Bold"

                # Clean the font name (remove subset prefix like "ABCDEF+")
                clean_name = basefont.split("+")[-1] if "+" in basefont else basefont

                if clean_name in font_files:
                    continue
                if ext in ("n/a", ""):
                    continue

                try:
                    # Extract binary font data
                    font_data = doc.extract_font(xref)
                    if font_data and len(font_data) >= 4 and font_data[3]:
                        binary = font_data[3]
                        suffix = f".{ext}" if ext else ".ttf"
                        tmp = tempfile.NamedTemporaryFile(
                            delete=False, suffix=suffix,
                            prefix=f"font_{clean_name}_"
                        )
                        tmp.write(binary)
                        tmp.close()
                        font_files[clean_name] = tmp.name
                        # Also map the full basefont name
                        font_files[basefont] = tmp.name
                except Exception:
                    continue
    except Exception:
        pass
    return font_files


def _get_font_info_at(page, target_text: str) -> dict:
    """
    Extracts exact font name, size, and color of the target text on a page.
    """
    blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
    best_match = {
        "font": DEFAULT_FONT,
        "size": DEFAULT_FONT_SIZE,
        "color": DEFAULT_FONT_COLOR,
        "flags": 0,
    }

    for block in blocks:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            line_text = "".join(span["text"] for span in line["spans"])
            if target_text in line_text:
                for span in line["spans"]:
                    if target_text in span["text"] or any(
                        w in span["text"] for w in target_text.split()[:3]
                    ):
                        color_int = span["color"]
                        r = ((color_int >> 16) & 0xFF) / 255.0
                        g = ((color_int >> 8) & 0xFF) / 255.0
                        b = (color_int & 0xFF) / 255.0
                        return {
                            "font": span["font"],
                            "size": span["size"],
                            "color": (r, g, b),
                            "flags": span["flags"],
                        }
    return best_match


def _get_line_containing(page, target_text: str) -> list:
    """Returns line info for lines containing the target text."""
    blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
    results = []
    for block in blocks:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            line_text = "".join(span["text"] for span in line["spans"])
            if target_text in line_text:
                results.append({
                    "bbox": line["bbox"],
                    "spans": line["spans"],
                    "full_text": line_text
                })
    return results


# ============================================================
# PDF MODIFICATION (Font-Aware + Text Reflow)
# ============================================================
def modify_pdf(find_text: str, replace_text: str) -> str:
    """
    Font-aware PDF text replacement with embedded font re-use.
    - Detects exact font, size, color of original text
    - Extracts embedded fonts from PDF and reuses them
    - For removal, reflows remaining text to fill the gap
    """
    pdf_store = st.session_state.get("pdf_bytes_store", {})
    if not pdf_store:
        return "ERROR: No PDF files uploaded."

    pdf_name = list(pdf_store.keys())[0]
    pdf_bytes = pdf_store[pdf_name]

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        # Extract all embedded fonts from the PDF
        embedded_fonts = _extract_embedded_fonts(doc)

        found = False
        details = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text_instances = page.search_for(find_text)

            if not text_instances:
                continue

            found = True
            font_info = _get_font_info_at(page, find_text)
            is_removal = replace_text.strip() in ("", "-")

            # Resolve the font file (if embedded in the PDF)
            font_name = font_info["font"]
            clean_font = font_name.split("+")[-1] if "+" in font_name else font_name
            font_file = embedded_fonts.get(clean_font) or embedded_fonts.get(font_name)

            if is_removal:
                # --- REMOVAL MODE ---
                line_data = _get_line_containing(page, find_text)
                for inst in text_instances:
                    page.add_redact_annot(inst, fill=(1, 1, 1))
                page.apply_redactions()

                if line_data:
                    line = line_data[0]
                    new_text = line["full_text"].replace(find_text, "").strip()
                    new_text = re.sub(r'  +', ' ', new_text)

                    if new_text:
                        line_rect = fitz.Rect(line["bbox"])
                        page.add_redact_annot(line_rect, fill=(1, 1, 1))
                        page.apply_redactions()

                        # Insert with original font (embedded if available)
                        insert_kwargs = {
                            "fontsize": font_info["size"],
                            "color": font_info["color"],
                        }
                        if font_file and os.path.exists(font_file):
                            insert_kwargs["fontfile"] = font_file
                            insert_kwargs["fontname"] = f"F{hash(clean_font) % 9999}"
                        else:
                            insert_kwargs["fontname"] = DEFAULT_FONT

                        page.insert_text(
                            fitz.Point(line_rect.x0, line_rect.y1 - (font_info["size"] * 0.2)),
                            new_text,
                            **insert_kwargs
                        )

                details.append(
                    f"Removed from page {page_num + 1} "
                    f"(font: {clean_font}, {font_info['size']:.1f}pt"
                    f"{', embedded font reused' if font_file else ''})"
                )
            else:
                # --- REPLACEMENT MODE ---
                for inst in text_instances:
                    page.add_redact_annot(inst, fill=(1, 1, 1))
                page.apply_redactions()

                insert_kwargs = {
                    "fontsize": font_info["size"],
                    "color": font_info["color"],
                }
                if font_file and os.path.exists(font_file):
                    insert_kwargs["fontfile"] = font_file
                    insert_kwargs["fontname"] = f"F{hash(clean_font) % 9999}"
                else:
                    insert_kwargs["fontname"] = DEFAULT_FONT

                first_rect = text_instances[0]
                page.insert_text(
                    fitz.Point(first_rect.x0, first_rect.y1 - (font_info["size"] * 0.2)),
                    replace_text,
                    **insert_kwargs
                )

                details.append(
                    f"Replaced on page {page_num + 1} "
                    f"(font: {clean_font}, {font_info['size']:.1f}pt, "
                    f"color: RGB{tuple(round(c*255) for c in font_info['color'])}"
                    f"{', embedded font reused' if font_file else ''})"
                )

        if not found:
            doc.close()
            _cleanup_fonts(embedded_fonts)
            return f"ERROR: Could not find '{find_text}' in '{pdf_name}'."

        modified_bytes = doc.tobytes()
        doc.close()
        _cleanup_fonts(embedded_fonts)

        st.session_state["pdf_bytes_store"][pdf_name] = modified_bytes
        st.session_state["modified_pdf"] = {
            "name": f"modified_{pdf_name}",
            "bytes": modified_bytes
        }

        action = "Removed" if is_removal else "Replaced"
        return (f"SUCCESS: {action} '{find_text}' → '{replace_text}' in '{pdf_name}'. "
                f"{'; '.join(details)}. Download button is now available.")

    except Exception as e:
        return f"ERROR: Failed to modify PDF: {str(e)}"


def _cleanup_fonts(font_files: dict):
    """Removes temporary font files."""
    seen = set()
    for path in font_files.values():
        if path not in seen:
            seen.add(path)
            try:
                os.unlink(path)
            except Exception:
                pass


# ============================================================
# TOOL WRAPPER (Called by Agent)
# ============================================================
def modify_pdf_tool_func(input_str: str) -> str:
    """
    Agent-facing wrapper. Expects JSON: {"find": "...", "replace": "..."}
    """
    try:
        data = json.loads(input_str)
        find_text = data.get("find", "").strip()
        replace_text = data.get("replace", "").strip()
    except json.JSONDecodeError:
        if "|" in input_str:
            parts = input_str.split("|", 1)
            find_text = parts[0].strip()
            replace_text = parts[1].strip()
        else:
            return 'ERROR: Invalid format. Use JSON: {"find": "old", "replace": "new"}'

    if not find_text:
        return "ERROR: 'find' must be non-empty."

    return modify_pdf(find_text, replace_text)
