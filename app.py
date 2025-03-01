from flask import Flask
import nest_asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from base64 import b64decode
import base64
from playwright.async_api import Page, BrowserContext
import json
import socket
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv
load_dotenv()

import math
from collections import Counter
import re
from pydantic import BaseModel, Field
nest_asyncio.apply()
import time

mykeys = {
  "type": os.getenv('TYPE'),
  "project_id": os.getenv('PROJECT_ID'),
  "private_key_id": os.getenv('PRIVATE_KEY_ID'),
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDSTA5IwwBbxSia\nAAeXYGIqRM0hnt1m+l0XlItb0mvijspz3RTfhKpaky+5S6EbqcQESImZn5/7f53e\ns++mm310E4/lC707G36FCtO+BBO3+dODf0a5m1cL/s16/teA7kt+1TQSubFUoJCs\nyWcyRUBEDCSBddSiUGc013w7BwprZTnWvQs5us64VTfM8wavi2dUPqQEpX9vM8t8\nSx1hReDzMvinr54Cv8pAF6zn0B81tXpKeG8Sts20BTuE39O5vpFGnSmNqwWyV3Sp\nMy85TB/tjKtjs8rTpNFbhBoondopgeyD9fUEsS7vo1Gx/9GaYyG3y0nOwfDkHPO1\n8psZMquVAgMBAAECggEABw0oz3TGbs1SGrPUjVVchUlQTYfLqbfMZk2DTL1mA69B\nB5iKqiIDKk1UJNTt3oUXPwOFpaKOFTtGumBzMTV2g+1h/k6h9jjqSaC+z9jIJnuY\nhYi/gNq+FPdiwXSJGlgjLOoOOHCEiy9lGn4YWT2sNXvov3SJgDXM+B8fmcUXKtmm\n8bVSBLLDKGfDUVvWew6+PN29glFOLZtwQJ84wkPm31z3/a4DimEyuZOEy51YDZ/V\nHBJRgnm4ZvFnKVIxMXcL8Sb1f/ZCnJnEYU4wlLa5Mqj0DwAecXPoxFAZSGvShfr9\nW8ODL5sWXzoS5gD6YOUWIO6YCIgo/cd9ro3I02NpIwKBgQD+nx2D8TfMZj9hiv4f\ncDFs11fdG8uIKsgqnS8sJTpr3BG3fHQ3MH3wbH3N3Hxq6M5TEGPJ1M2RwvA+JiN/\n7PUcylXlKaJK1WKIzU+1vfQ0mGL7+rQScg1OeufG08/SMfzJT0SNWnz5N5RvCGEo\npWY+dY5ItkK2Kt6mgvQg5MYltwKBgQDTb4KrVirWnXeq6C2n09uaqD2UwFUaSNVs\nUyRm9I5EMHx86f5j69vJxsITzSj9LB9kv3oaorYqNx5p6xJ5d9VZM8VqJQmnP+8o\nMgd8LCYgpKdb40yOUVubUM/dJMvS+/IFlhlEWlBniuwYxBQo8VKCcsqNDQ7O2viV\nThVTGakZEwKBgQDlfA1DDNZIj+MSDA7L0PeK7G9RZirD2CM+XRrWA9uquNby8+Ve\nlIL9fRrJvq4YQSksLjpx/y0j8XlL2l3mf2/PegF+oE6YecfsGnd8Cu8dtDaKesNv\nWIHruNRLHD5TaSA3ZA0aBXNbvp82j2vaEXCcXKFXoYVw4CR6GM7lEqwP8wKBgGAp\nAPbHs6fz6e7ytYD0m5XVGlzCtHHF2jrv/UhNxT5CBvwQt7/eDxHPsYir8A5kuMpr\nQy9F/S9p7g0h+j8APynYn9pMif1k2HIhfsH8mkKSYAMsdy7q1YznzgG3sHN+Xm4n\n+8nYgWT2C7afxsNwLaRibLiFzcxKTnApGQ24R+29AoGBAIh03tj3sQ+DE/FJ/adl\nrnXExWz2Og/rGYXBz7C4WLdiqMD3zhroP88jsc7IabROzarmlDF50076Pyyx+2OZ\nh/VUkmK0JSEDpgWN1bXyohLXf3YOeivaghS+w3IDZLg6huWlhRknGOH/NnbwJFKI\nFafEtHcmk32GdyQyt/4xfYlw\n-----END PRIVATE KEY-----\n",
  "client_email": os.getenv('CLIENT_EMAIL'),
  "client_id": os.getenv('CLIENT_ID'),
  "auth_uri": os.getenv('AUTH_URI'),
  "token_uri": os.getenv('TOKEN_URI'),
  "auth_provider_x509_cert_url": os.getenv('AUTH_PROVIDER_X509_CERT_URL'),
  "client_x509_cert_url": os.getenv('CLIENT_X509_CERT_URL'),
  "universe_domain": os.getenv('UNIVERSE_DOMAIN'),
}

with open("person.json","w") as output:
    json.dump(mykeys,output)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] ='person.json'
WORD = re.compile(r"\w+")

 

def base64_to_image(base64_string):
  # Remove the data URI prefix if present
  if "data:image" in base64_string:
      base64_string = base64_string.split(",")[1]
      

  # Decode the Base64 string into bytes
  image_bytes = base64.b64decode(base64_string)
  return image_bytes

def create_image_from_bytes(image_bytes):
  # Create a BytesIO object to handle the image data
  image_stream = BytesIO(image_bytes)

  # Open the image using Pillow (PIL)
  image = Image.open(image_stream)
  return image

def detect_text(path):
    """Detects text in the file."""
    from google.cloud import vision

    client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    # for non-dense text 
    # response = client.text_detection(image=image)
    # for dense text
    response = client.text_detection(image=image)
    texts = response.text_annotations
    #print(texts)
    ocr_text = ""

    for text in texts:
        ocr_text = text.description

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    
    return ocr_text

def find_open_port():
    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a random available port
    sock.bind(('127.0.0.1', 0))

    # Get the port that was actually bound
    _, port = sock.getsockname()

    # Close the socket
    sock.close()

    return port

schema_get_captcha = {
     "name": "Commit Extractor",
            "baseSelector": ".ui-inputgroup",
            "fields": [
                {
                    "name": "src",
                    "selector": ".captcha-img-fix",
                    "type": "attribute",
                    "attribute":"src"
                    
                },
            ],
}
extraction_strategy = JsonCssExtractionStrategy(schema_get_captcha)


app = Flask(__name__)


async def hello_world():
    # 1) Configure the browser
    browser_config = BrowserConfig(
        headless=True,
        verbose=True
    )

    # 2) Configure the crawler run
    strategy = JsonCssExtractionStrategy(schema_get_captcha)
    #js_code = 'document.querySelector(".ui-inputgroup .captcha-img-fix").src'#diseñado para realizar acciones

    crawler_run_config = CrawlerRunConfig(
        #js_code="window.scrollTo(0, document.body.scrollHeight);",
        #wait_for="body",
        extraction_strategy=strategy,
        cache_mode=CacheMode.BYPASS,
        #screenshot=True,
    )
    crawler_run_config1 = CrawlerRunConfig(
        #js_code="window.scrollTo(0, document.body.scrollHeight);",
        #wait_for="body",
        #extraction_strategy=strategy,
        cache_mode=CacheMode.BYPASS,
        screenshot=True,
    )

    
    # 3) Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()
    # 4) Run the crawler on an example page
    url = "https://remaju.pj.gob.pe/remaju/pages/seguridad/login.xhtml"
    result = await crawler.arun(url, config=crawler_run_config)

    if result.success:
        #print("\nCrawled URL:", result.extracted_content)
        news_teasers = json.loads(result.extracted_content)
        imagen64 = news_teasers[0]
        image_bytes = base64_to_image(imagen64['src'])
        # Create an image from bytes
        img = create_image_from_bytes(image_bytes)
        # Display or save the image as needed
        #img.show()
        img.save("output_image.jpg")

    else:
            print("Error:", result.error_message)
    
    await crawler.close()
    return detect_text('output_image.jpg')




@app.route('/')
async def inicio():
    lacaptcha = await hello_world()
    print(lacaptcha)
    print("🔗 Hooks Example: Demonstrating recommended usage")

    # 1) Configure the browser
    browser_config = BrowserConfig(
        headless=True,
        verbose=True
    )

    # 2) Configure the crawler run
    crawler_run_config = CrawlerRunConfig(
        #js_code="window.scrollTo(0, document.body.scrollHeight);",
        #wait_for=".main",
        #cache_mode=CacheMode.BYPASS,
        screenshot=True
    )

    # 3) Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)

    #
    # Define Hook Functions
    #

    async def on_browser_created(browser, **kwargs):
        # Called once the browser instance is created (but no pages or contexts yet)
        print("[HOOK] on_browser_created - Browser created successfully!")
        # Typically, do minimal setup here if needed
        return browser

    async def on_page_context_created(page: Page, context: BrowserContext, **kwargs):
        # Called right after a new page + context are created (ideal for auth or route config).
        print("[HOOK] on_page_context_created - Setting up page & context.")
        await page.goto("https://remaju.pj.gob.pe/remaju/pages/seguridad/login.xhtml")
        await page.click(".ui-corner-left")#btn con casilla
        await page.fill("input[name='frmLogin:usuario']","191543")#usuario
        await page.fill("input[name='frmLogin:claveConCasilla']", "Messenger2")#password
        await page.fill("input[name='frmLogin:captcha']", lacaptcha)
        await page.click('.btn-rojo')
        #await page.wait_for_selector(".main")


        await page.set_viewport_size({"width": 1080, "height": 600})
        return page

    

    async def after_goto(page: Page, context: BrowserContext, url: str, response, **kwargs):
        # Called after navigation completes.
        print(f"[HOOK] after_goto - Successfully loaded: {url}")
        # e.g., wait for a certain element if we want to verify
        try:
            await page.wait_for_selector('a[id="bar-menu-button"]', timeout=1000)
            print("[HOOK] Found .content element!")
        except:
            print("[HOOK] .content not found, continuing anyway.")
        return page

    async def on_user_agent_updated(page: Page, context: BrowserContext, user_agent: str, **kwargs
    ):
        # Called whenever the user agent updates.
        print(f"[HOOK] on_user_agent_updated - New user agent: {user_agent}")
        return page

    async def on_execution_started(page: Page, context: BrowserContext, **kwargs):
        # Called after custom JavaScript execution begins.
        print("[HOOK] on_execution_started - JS code is running!")
        return page

    async def before_retrieve_html(page: Page, context: BrowserContext, **kwargs):
        # Called before final HTML retrieval.
        print("[HOOK] before_retrieve_html - We can do final actions")
        # Example: Scroll again
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        return page

    async def before_return_html(page: Page, context: BrowserContext, html: str, **kwargs):
        # Called just before returning the HTML in the result.
        print(f"[HOOK] before_return_html - HTML length: {len(html)}")
        return page

    #
    # Attach Hooks
    #

    #crawler.crawler_strategy.set_hook("on_browser_created", on_browser_created)
    crawler.crawler_strategy.set_hook("on_page_context_created", on_page_context_created)
    #crawler.crawler_strategy.set_hook("before_goto", before_goto)#antes
    crawler.crawler_strategy.set_hook("after_goto", after_goto)#despues
    #crawler.crawler_strategy.set_hook("on_user_agent_updated", on_user_agent_updated)
    crawler.crawler_strategy.set_hook("on_execution_started", on_execution_started)
    #crawler.crawler_strategy.set_hook("before_retrieve_html", before_retrieve_html)
    crawler.crawler_strategy.set_hook("before_return_html", before_return_html)

    await crawler.start()

    # 4) Run the crawler on an example page
    url = "https://remaju.pj.gob.pe/remaju/pages/inicio.xhtml"
    result = await crawler.arun(url, config=crawler_run_config)

    if result.success:
        if result.screenshot:
            with open("page.png", "wb") as f:
                f.write(base64.b64decode(result.screenshot))
    else:
        print("Error:", result.error_message)

    await crawler.close()
    os.remove("person.json")
    return {"hi":"ktal"}


if __name__ == "__main__":
    app.run()