from django.core.management.base import BaseCommand

import re
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.db import transaction
from Core.models import Professor, ClassData, Course

def normalize_prof_names(prof_field):
    if not prof_field:
        return []
    pf = prof_field.strip()
    if pf.lower() in ('not listed', 'not listed.', 'to be announced', 'tba', 'n/a', ''):
        return []
    # split on common separators (commas, semicolons, slashes, ampersand, ' and ')
    parts = re.split(r',|;|/|&|\band\b', pf, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]

@transaction.atomic
def attach_profs_to_existing_courses(all_courses_data, verbose=True):
    added = 0
    skipped = 0
    for item in all_courses_data:
        raw_number = item.get('number', '').strip()          # e.g. "CASCH 201"
        title = item.get('title', '').strip()
        prof_field = item.get('professor', '')

        # parse college (first 3 letters) and subject (next letters before space)
        try:
            left, catalog = raw_number.split(None, 1)  # splits on whitespace
        except ValueError:
            if verbose:
                print(f"Skipping malformed number: {raw_number!r}")
            skipped += 1
            continue

        if len(left) >= 5:
            college_code = left[:3]
            subject_code = left[3:]
        else:
            # fallback to regex: 3-letter college + 2-letter subject
            m = re.match(r'([A-Z]{3})([A-Z]{2,3})', left, re.I)
            if not m:
                if verbose:
                    print(f"Could not parse left part: {left!r}")
                skipped += 1
                continue
            college_code, subject_code = m.group(1).upper(), m.group(2).upper()

        catalog_number = catalog.strip().split()[0]  # take first token
        # find ClassData
        classdata = ClassData.objects.filter(
            college=college_code,
            subject=subject_code,
            catalog_number=catalog_number
        ).first()
        if not classdata:
            if verbose:
                print(f"No ClassData for {college_code}{subject_code} {catalog_number}; skipping")
            skipped += 1
            continue

        # find existing Course(s) for this ClassData
        # If you have duplicates and want to match title too, include name=title in the filter
        course_qs = Course.objects.filter(class_data=classdata)
        if title:
            course_qs = course_qs.filter(name__iexact=title)
        course = course_qs.first()
        if not course:
            # fallback: if strict name match fails, try any course for that classdata
            course = Course.objects.filter(class_data=classdata).first()
        if not course:
            if verbose:
                print(f"No Course found for {classdata}; skipped")
            skipped += 1
            continue

        # parse professor names and attach
        prof_names = normalize_prof_names(prof_field)
        if not prof_names:
            if verbose:
                print(f"No valid professor name for {classdata} / {title}; skipping")
            skipped += 1
            continue

        for pname in prof_names:
            prof_obj, created = Professor.objects.get_or_create(name=pname)
            course.professor.add(prof_obj)  # idempotent
            if created and verbose:
                print(f"Created Professor: {pname}")
            added += 1

    if verbose:
        print(f"Finished: added {added} professor links, skipped {skipped} items.")


def process_professors():

    # --------------------------
    # 1️⃣ Setup Chrome driver
    # --------------------------
    driver_path = r"C:\Users\evanj\OneDrive\Desktop\CourseScraper\chromedriver-win64\chromedriver.exe"
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)
    # Set up a 20-second wait (increased from 10)
    wait = WebDriverWait(driver, 20) 

    # --------------------------
    # 2️⃣ Open BU HUB login page
    # --------------------------
    driver.get("https://mybustudent.bu.edu")
    input("Log in manually and press Enter here once logged in...")

    # --------------------------
    # 3️⃣ Navigate to HUB course search page
    # --------------------------
    hub_url = "https://mybustudent.bu.edu/psp/BUPRD/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_Main?institution=BU001&term=2261&crse_attr=HUB&page=1"
    driver.get(hub_url)
    input("Perform the course search manually, then press Enter here once the results are fully loaded...")

    # --------------------------
    # 4️⃣ Switch to iframe if needed
    # --------------------------
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"Found {len(iframes)} iframe(s).")
    if iframes:
        driver.switch_to.frame(iframes[0])
        print("Switched into the first iframe.")

    # --------------------------
    # 5️⃣ Loop Through All Pages and Scrape
    # --------------------------

    NEXT_BUTTON_SELECTOR = "button[aria-label='Go to next page']"
    title_pattern = re.compile(r"(.+) \| ([A-Z]{3,5} \d{3})")
    instructor_pattern = re.compile(r"Instructor:\s+(.+)")

    all_courses_data = []
    seen_combinations = set()

    page_number = 1

    while True:
        print("\n" + "=" * 80)
        print(f"Scraping Page {page_number}...")
        
        try:
            # Wait for h2 elements AND their data (<ul>) to appear
            try:
                # 🔥 SOLUTION 1 FIX: Wait for the <ul> data, not just the <h2> title
                print("Waiting for page data to be present...")
                wait.until(EC.presence_of_element_located((By.XPATH, "//h2/following-sibling::ul[1]")))
                print("Data is present. Starting scrape.")
            except TimeoutException:
                print("No <h2> or <ul> data tags found on this page. Assuming no results.")
                break
            
            all_headings = driver.find_elements(By.TAG_NAME, "h2")
            print(f"Found {len(all_headings)} total <h2> headings...")
            
            if not all_headings:
                print("No headings found. Ending scrape.")
                break
                
            for heading in all_headings:
                try:
                    heading_text = heading.text
                    title_match = title_pattern.search(heading_text)
                    
                    if title_match:
                        current_title = title_match.group(1).strip()
                        current_number = title_match.group(2).strip()
                        print("-" * 80)
                        print(f"Found Course: {current_title} ({current_number})")
                        
                        try:
                            sections_ul = heading.find_element(By.XPATH, "./following-sibling::ul[1]")
                            sections_text = sections_ul.text
                            
                            professors_found = 0
                            instructor_matches = instructor_pattern.finditer(sections_text)
                            
                            for match in instructor_matches:
                                professors_found += 1
                                professor = match.group(1).strip()
                                if professor == "-" or professor == "None":
                                    professor = "Not listed"
                                
                                unique_key = (current_number, professor)
                                if unique_key not in seen_combinations:
                                    print(f"  -> Found Section with Professor: {professor}")
                                    all_courses_data.append({"title": current_title, "number": current_number, "professor": professor})
                                    seen_combinations.add(unique_key)
                                else:
                                    print(f"  -> Skipping duplicate: ({current_number}, {professor})")
                            
                            if professors_found == 0:
                                professor = "Not listed"
                                unique_key = (current_number, professor)
                                if unique_key not in seen_combinations:
                                    print("  -> No professor listed in the sections.")
                                    all_courses_data.append({"title": current_title, "number": current_number, "professor": "Not listed"})
                                    seen_combinations.add(unique_key)
                                else:
                                    print(f"  -> Skipping duplicate: ({current_number}, Not listed)")

                        except Exception as e:
                            print(f"  -> ERROR: Could not parse sections: {e}")
                except StaleElementReferenceException:
                    print("  -> StaleElement: Skipped one heading, continuing loop...")
                    continue

            # --------------------------
            # PAGINATION (REVISED with dynamic content wait)
            # --------------------------
            print("\nPage scrape complete. Looking for 'Next' button...")
            try:
                # 1. Get a reference to the first course heading on the *current* page.
                try:
                    first_heading_on_page = all_headings[0]
                except (IndexError, NameError):
                    first_heading_on_page = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2")))

                # 2. Find and click the 'Next' button
                next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, NEXT_BUTTON_SELECTOR)))
                next_button.click()
                
                print("Clicked 'Next'. Waiting for new page to load...")
                page_number += 1

                # 3. Wait for the *old* content to disappear (go stale)
                print(f"Waiting for old content (page {page_number-1}) to disappear...")
                wait.until(EC.staleness_of(first_heading_on_page))
                print("Old content is stale.")

                # 4. 🔥 SOLUTION 1 FIX: Wait for the *new data* (the <ul>) to appear.
                print(f"Waiting for new content data (page {page_number}) to appear...")
                wait.until(EC.presence_of_element_located((By.XPATH, "//h2/following-sibling::ul[1]")))
                
                print(f"Page {page_number} is now active. Starting scrape.")

            except (NoSuchElementException, TimeoutException):
                print("Could not find a clickable 'Next' button (or new content). Assuming this is the last page.")
                break
        
            
                
        except Exception as e:
            print(f"An unknown error occurred on page {page_number}: {e}")
            break

    # --------------------------
    # 6️⃣ Finish
    # --------------------------
    print("\n" + "=" * 80)
    print(f"Scraping complete. Found {len(all_courses_data)} unique course/professor combinations.")
    attach_profs_to_existing_courses(all_courses_data)


    

class Command(BaseCommand):
    help = "Populates the database with scraped professors"

    def handle(self, *args, **options):
        process_professors()