import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "https://hiring.idenhq.com/"
LOGIN_URL = BASE_URL

USERNAME = os.getenv("IDEN_USERNAME")
PASSWORD = os.getenv("IDEN_PASSWORD")

SESSION_PATH = Path("sessions.json")
OUTPUT_JSON = "productss.json"

async def save_storage(context):
    await context.storage_state(path=SESSION_PATH)

async def load_or_login(playwright):
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(BASE_URL)
    email_field = await page.query_selector("input[type='email']")
    password_field = await page.query_selector("input[type='password']")
    
    if email_field and password_field:
        await email_field.fill(USERNAME)
        await password_field.fill(PASSWORD)
        await page.click("button[type='submit']")
        await page.wait_for_load_state("networkidle")
        await save_storage(context)
    return browser, context, page

async def navigate_to_products(page):
    await page.goto(f"{BASE_URL}challenge")
    await page.wait_for_load_state("networkidle")
    menu_button = await page.query_selector("text=Menu")
    if menu_button:
        await menu_button.click()
        try:
            data_mgmt = await page.wait_for_selector("text=Data Management", timeout=5000)
            await data_mgmt.click()
            inventory = await page.wait_for_selector("text=Inventory", timeout=5000)
            await inventory.click()
            view_products = await page.wait_for_selector("text=View All Products", timeout=5000)
            await view_products.click()
            await page.wait_for_load_state("networkidle")
            load_button = await page.wait_for_selector("button:has-text('Load Product Table')", timeout=5000)
            if not load_button:
                load_button = await page.query_selector("button:text('Load Product Table')")
            if not load_button:
                load_button = await page.query_selector("//button[contains(text(), 'Load Table')]")
            
            if load_button:
                await load_button.click()
                await page.wait_for_load_state("networkidle", timeout=10000)
                await asyncio.sleep(2)
                await page.wait_for_selector("div.rounded-lg", timeout=10000)
            else:
                pass
            return True
        except PlaywrightTimeoutError as e:
            pass
    
    try:
        await page.goto(f"{BASE_URL}challenge/products")
        await page.wait_for_load_state("networkidle")
        load_button = await page.query_selector("button:has-text('Load Table')")
        if load_button:
            await load_button.click()
            await page.wait_for_load_state("networkidle", timeout=10000)
            await asyncio.sleep(2)
        await page.wait_for_selector("div.rounded-lg", timeout=5000)
        return True
    except PlaywrightTimeoutError:
        pass
    
    return False

async def extract_products(page):
    products = []
    await page.wait_for_selector("div.rounded-lg", timeout=10000)
    product_containers = await page.query_selector_all("div.rounded-lg")
    
    for i, container in enumerate(product_containers):
        try:
            product = {}
            labels = await container.query_selector_all("span.text-gray-500")
            values = await container.query_selector_all("span.font-medium")
            
            if len(labels) == len(values) and len(labels) >= 4:
                for j in range(len(labels)):
                    label_text = await labels[j].inner_text()
                    value_text = await values[j].inner_text()
                    if "ID" in label_text:
                        product["ID"] = value_text
                    elif "Dimension" in label_text:
                        product["Dimensions"] = value_text
                    elif "Detail" in label_text:
                        product["Details"] = value_text
                    elif "Type" in label_text:
                        product["Type"] = value_text
            
            if not product:
                if len(values) >= 4:
                    product["ID"] = await values[0].inner_text()
                    product["Dimensions"] = await values[1].inner_text()
                    product["Details"] = await values[2].inner_text()
                    product["Type"] = await values[3].inner_text()
            
            if product:
                products.append(product)
        except Exception as e:
            pass
    
    return products

async def save_json(data):
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

async def main():
    async with async_playwright() as playwright:
        browser = None
        try:
            browser, context, page = await load_or_login(playwright)
            success = await navigate_to_products(page)
            if not success:
                return
            products = await extract_products(page)
            if products:
                await save_json(products)
        except Exception as e:
            pass
        finally:
            if browser:
                await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
