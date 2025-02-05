import asyncio
from playwright.async_api import async_playwright
import argparse
from pathlib import Path
import base64

async def convert_mermaid_to_png(mermaid_code, output_file):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <script>
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: 'default'
                }});
            </script>
        </head>
        <body>
            <div class="mermaid">
                {mermaid_code}
            </div>
        </body>
        </html>
        """
        
        await page.set_content(html_content)
        await page.wait_for_selector(".mermaid svg")
        
        svg = await page.query_selector(".mermaid svg")
        await svg.screenshot(path=output_file)
        
        await browser.close()

def batch_convert(input_dir):
    for file in Path(input_dir).glob('*.mermaid'):
        output_file = file.with_suffix('.png')
        with open(file, 'r') as f:
            mermaid_code = f.read()
        asyncio.run(convert_mermaid_to_png(mermaid_code, str(output_file)))
        print(f"Converted {file} to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Convert Mermaid diagram to PNG')
    parser.add_argument('input', help='Input .mermaid file or directory')
    parser.add_argument('-o', '--output', help='Output PNG file path (optional)')
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if input_path.is_dir():
        batch_convert(input_path)
    else:
        output_path = args.output if args.output else input_path.with_suffix('.png')
        with open(input_path, 'r') as f:
            mermaid_code = f.read()
        asyncio.run(convert_mermaid_to_png(mermaid_code, str(output_path)))
        print(f"Converted {input_path} to {output_path}")

if __name__ == "__main__":
    main()
