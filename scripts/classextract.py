import argparse
from bs4 import BeautifulSoup

def extract_class_text_from_files(class_name, file_list):
    for file_path in file_list:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Parse XHTML content
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find all <p> tags with the specified class
            paragraphs = soup.find_all('p', class_=class_name)
            
            print(f"\nFile: {file_path}")
            if paragraphs:
                for i, p in enumerate(paragraphs, start=1):
                    print(f"  Paragraph {i}: {p.get_text(strip=True)}")
            else:
                print("  No matching paragraphs found.")
        
        except FileNotFoundError:
            print(f"Error: File not found - {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(
        description='Extract text from <p> tags with a specific class in XHTML files.'
    )
    parser.add_argument(
        'class_name',
        type=str,
        help='The CSS class to search for in <p> tags.'
    )
    parser.add_argument(
        'files',
        metavar='file',
        type=str,
        nargs='+',
        help='One or more XHTML files to process.'
    )
    
    args = parser.parse_args()
    
    extract_class_text_from_files(args.class_name, args.files)

if __name__ == '__main__':
    main()
