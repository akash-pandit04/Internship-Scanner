"""
CSE Internship Auto-Applier (Premium SaaS Tier POC)
Uses Playwright to automate the submission of internship applications
on standard ATS platforms (e.g., Greenhouse).
"""
import asyncio
from playwright.async_api import async_playwright

class GreenhouseAutoApplier:
    def __init__(self, user_profile):
        """
        user_profile expects a dict with:
        first_name, last_name, email, phone, resume_path
        """
        self.profile = user_profile

    async def apply_to_job(self, job_url):
        print(f"[*] Initiating Premium Auto-Applier for: {job_url}")
        
        async with async_playwright() as p:
            # Launch browser in headless mode for CI/CD compatibility
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # 1. Navigate to the internship posting
                await page.goto(job_url)
                print("[*] Loaded application page.")
                
                # 2. Fill standard Greenhouse fields
                # Note: Selectors map to standard Greenhouse form IDs
                if await page.locator("#first_name").is_visible():
                    await page.fill("#first_name", self.profile["first_name"])
                    await page.fill("#last_name", self.profile["last_name"])
                    await page.fill("#email", self.profile["email"])
                    await page.fill("#phone", self.profile["phone"])
                    print("[*] Injected user contact data.")
                    
                    # 3. Upload Resume
                    if self.profile.get("resume_path"):
                        await page.set_input_files("input[type='file']", self.profile["resume_path"])
                        print("[*] Uploaded Resume PDF.")
                        
                    # 4. Submit (Commented out in POC to prevent accidental spam)
                    # await page.click("#submit_app")
                    print("[+] Application successfully prepared for submission.")
                else:
                    print("[-] Not a standard Greenhouse form. Aborting auto-apply.")
                    
            except Exception as e:
                print(f"[-] Auto-Applier failed: {e}")
            finally:
                await browser.close()

if __name__ == "__main__":
    # Mock Data for Portfolio Demonstration
    mock_profile = {
        "first_name": "Akash",
        "last_name": "Pandit",
        "email": "akash@example.com",
        "phone": "555-0199",
        "resume_path": "resume.pdf"
    }
    
    applier = GreenhouseAutoApplier(mock_profile)
    # Target a test greenhouse URL (replace with live URL in production)
    test_url = "https://boards.greenhouse.io/testcompany/jobs/12345"
    asyncio.run(applier.apply_to_job(test_url))
