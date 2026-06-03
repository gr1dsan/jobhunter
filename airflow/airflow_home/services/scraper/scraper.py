from playwright.async_api import async_playwright
from .config import *


async def get_pages(page):
    try:
        locator = page.locator("ul.pages_ul_inner li a").last
        await locator.wait_for(timeout=5000)
        return int(await locator.inner_text())
    except Exception:
        return 1


async def get_job_data(page, links):
    results = []

    for link in links:
        link = link + "?save_locale=1&translate_ads=1"
        try:
            await page.goto(link, wait_until="domcontentloaded")

            title = await page.locator("h1#jobad_heading1").inner_text()

            company = await page.locator("#jobad_location").evaluate("""
                el => [...el.childNodes]
                    .filter(n => n.nodeType === Node.TEXT_NODE)
                    .map(n => n.textContent.trim())
                    .filter(Boolean) 
                    .join(' ')
                    .replace(/^[–-]\\s*/, '')
                    .trim()
            """)

            salary_amount = await page.locator(
                "span.data_tag_component_salary_amount"
            ).first.inner_text()

            salary_type = await page.locator(
                "div.label_component_body"
            ).first.inner_text()

            work_type = await page.locator(
                "div.label_component_body"
            ).last.inner_text()

            location = await page.locator("#jobad_location").evaluate("""
                el => [...el.querySelectorAll("span[itemprop='addressLocality']")]
                    .map(s => s.textContent.trim())
                    .filter((v, i, a) => a.indexOf(v) === i)
                    .join(', ')
            """)

            details = "\n\n".join([
                (await d.inner_text()).strip()
                for d in await page.locator("div.jobad_txt").all()
            ])

            results.append({
                "title": title.strip(),
                "company": company,
                "work_type": work_type.strip(),
                "location": location,
                "salary": salary_amount,
                "salary_type": salary_type,
                "details": details,
                "url": link,
            })

        except Exception as e:
            print(f"Failed on {link}: {e}")

    return {"jobs": results}


async def scrape_data(url):
    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=headless_state)

        context = await browser.new_context(
            locale="en-US",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9"
            }
        )

        page = await context.new_page()

        await page.goto(url + "&page=1", wait_until="domcontentloaded")
        pages_count = await get_pages(page)

        links = []

        for current_page in range(1, pages_count + 1):

            if len(links) >= max_links:
                break

            await page.goto(
                url + f"&page={current_page}",
                wait_until="domcontentloaded"
            )

            jobs = await page.locator("article.list_article").all()

            for job in jobs:
                link = await job.locator("a").get_attribute("href")

                if link:
                    links.append(link)

                    if len(links) >= max_links:
                        break

        result = await get_job_data(page, links)

        await browser.close()

        return result