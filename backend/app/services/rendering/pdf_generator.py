import asyncio
from playwright.async_api import async_playwright
import os
import sys
from loguru import logger
from concurrent.futures import ThreadPoolExecutor

class PDFGenerator:
    """
    Generates ATS-compatible PDFs from HTML using Playwright.
    """
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=3)

    async def generate_pdf(self, html_content: str, output_path: str) -> bool:
        """
        Renders HTML to PDF and saves it to the specified path.
        On Windows, if the current loop is a SelectorEventLoop, this runs
        in a separate thread with a ProactorEventLoop to support subprocesses.
        """
        loop = asyncio.get_running_loop()
        
        # Core Issue: Windows SelectorEventLoop doesn't support subprocesses (needed by Playwright)
        if sys.platform == 'win32' and not isinstance(loop, getattr(asyncio, 'ProactorEventLoop', type(None))):
            logger.info("Detected SelectorEventLoop on Windows. Offloading PDF generation to a ProactorEventLoop thread.")
            return await loop.run_in_executor(
                self.executor, 
                self._run_in_new_loop, 
                html_content, 
                output_path
            )
        
        return await self._generate_pdf_async(html_content, output_path)

    def _run_in_new_loop(self, html_content: str, output_path: str) -> bool:
        """Helper to run the async generation in a new dedicated event loop."""
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            # Ensure the new loop is a ProactorEventLoop on Windows
            if sys.platform == 'win32':
                from app.core import windows_compat # Re-apply policy just in case
            
            return new_loop.run_until_complete(self._generate_pdf_async(html_content, output_path))
        except Exception as e:
            logger.error(f"Threaded PDF generation failed: {e}")
            return False
        finally:
            new_loop.close()

    async def _generate_pdf_async(self, html_content: str, output_path: str) -> bool:
        """The actual playwright logic."""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set content and wait for it to be fully loaded
                await page.set_content(html_content, wait_until="networkidle")

                # Scale oversized content down to exactly one source-sized page.
                dimensions = await page.evaluate("""() => {
                    const container = document.querySelector('.resume-container') || document.body;
                    const style = getComputedStyle(container);
                    return {
                        width: container.scrollWidth,
                        height: container.scrollHeight,
                        pageWidth: parseFloat(style.width),
                    };
                }""")
                # Browser measurements are CSS pixels. Keep the same unit when
                # passing dimensions to Playwright; Chromium does not accept pt.
                page_width = max(float(dimensions["pageWidth"] or dimensions["width"]), 1.0)
                page_height = max(dimensions["height"], 1)
                source_ratio = page_width / 612.0
                target_height = 792.0 * source_ratio
                scale = max(0.1, min(1.0, target_height / page_height))
                
                # Generate PDF with A4 format and 100% scale
                await page.pdf(
                    path=output_path,
                    width=f"{page_width:.2f}px",
                    height=f"{target_height:.2f}px",
                    print_background=True,
                    margin={
                        "top": "0mm",
                        "bottom": "0mm",
                        "left": "0mm",
                        "right": "0mm"
                    },
                    display_header_footer=False,
                    scale=scale
                )
                
                await browser.close()
                logger.info(f"PDF generated successfully at: {output_path}")
                return True
        except Exception as e:
            logger.error(f"Error in _generate_pdf_async: {e}")
            return False
