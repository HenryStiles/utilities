
# **XHTML Paragraph Extractor**

A command-line tool to extract text from `<p>` tags with a specific CSS class in XHTML files.

---

## **Usage**

```bash
python extract_class_text.py <class_name> <file1.xhtml> [file2.xhtml ...]
```

### **Arguments:**
- **`class_name`** *(str)*: The CSS class to search for in `<p>` tags.  
- **`file1.xhtml`** *(str)*: Path to the first XHTML file.  
- **`[file2.xhtml ...]`** *(optional)*: Additional XHTML files to process.  

---

## **Example**

Extract paragraphs with the class `x05-Head-A` from two XHTML files:

```bash
python extract_class_text.py x05-Head-A file1.xhtml file2.xhtml
```

**Output Example:**
```
File: file1.xhtml
  Paragraph 1: This is the first header.
  Paragraph 2: Another header here.

File: file2.xhtml
  No matching paragraphs found.
```

---

##  **Installation**

Ensure `beautifulsoup4` is installed:

```bash
pip install beautifulsoup4
```

---

## **Description**

- Parses XHTML files.  
- Finds `<p>` tags with the specified CSS class.  
- Extracts and displays text content without HTML tags.  
- Handles multiple files and error scenarios gracefully.

---

## **Error Handling**
- **File Not Found:** Displays an error if a file does not exist.  
- **Parsing Error:** Reports any issues with XHTML structure.

---

## **License**

MIT License.
