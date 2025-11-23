from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
import requests
from Core.models import Hub, ClassData, Course, Offered, HUB_CHOICES
import re

from typing import overload, Literal

HUB_LABEL_TO_CODE = {label: code for code, label in HUB_CHOICES}

# 1436 / 2241
prefix = "https://www.bu.edu/hub/hub-courses/"
urls = [
    "https://www.bu.edu/hub/hub-courses/philosophical-inquiry-and-lifes-meanings/",
    "https://www.bu.edu/hub/hub-courses/aesthetic-exploration/",
    "https://www.bu.edu/hub/hub-courses/historical-consciousness/",
    "https://www.bu.edu/hub/hub-courses/scientific-inquiry-i/",
    "https://www.bu.edu/hub/hub-courses/scientific-inquiry-ii/",
    "https://www.bu.edu/hub/hub-courses/social-inquiry-i/",
    "https://www.bu.edu/hub/hub-courses/social-inquiry-ii/",
    "https://www.bu.edu/hub/hub-courses/quantitative-reasoning-i/",
    "https://www.bu.edu/hub/hub-courses/quantitative-reasoning-ii/",
    "https://www.bu.edu/hub/hub-courses/the-individual-in-community/",
    "https://www.bu.edu/hub/hub-courses/global-citizenship-and-intercultural-literacy/",
    "https://www.bu.edu/hub/hub-courses/ethical-reasoning/",
    "https://www.bu.edu/hub/hub-courses/first-year-writing-seminar/",
    "https://www.bu.edu/hub/hub-courses/writing-research-and-inquiry/",
    "https://www.bu.edu/hub/hub-courses/writing-intensive-course/",
    "https://www.bu.edu/hub/hub-courses/oral-and-or-signed-communication/",
    "https://www.bu.edu/hub/hub-courses/digital-multimedia-expression/",
    "https://www.bu.edu/hub/hub-courses/critical-thinking/",
    "https://www.bu.edu/hub/hub-courses/research-and-information-literacy/",
    "https://www.bu.edu/hub/hub-courses/teamwork-collaboration/",
    "https://www.bu.edu/hub/hub-courses/creativity-innovation/"
]

def parse_terms(text: str) -> list[str]:
    # Replace "and" with comma, then split on commas/whitespace
    cleaned = re.sub(r"\band\b", ",", text, flags=re.IGNORECASE)
    parts = re.split(r"[,\s]+", cleaned)
    # Filter blank entries and enforce title case
    return [p.title() for p in parts if p]

@overload
def get_current_db_content(pick: str) -> dict: ...

@overload
def get_current_db_content(pick: Literal["hub"]) -> dict[str, Hub]: ...

@overload
def get_current_db_content(pick: Literal["classdata"]) -> dict[tuple[str, str, str], ClassData]: ...

@overload
def get_current_db_content(pick: Literal["course"]) -> dict[tuple[str, str, str], Course]: ...


def get_current_db_content(pick) -> dict[str, Hub] | dict[tuple[str, str, str], ClassData] | dict[tuple[str, str, str], Course] | dict:
    if pick == 'hub':
        # Get all hubs once so we don't hit DB repeatedly
        return {h.unit_name: h for h in Hub.objects.all()}

    elif pick == 'classdata':
        # Cache ClassData rows
        return {
            (cd.college, cd.subject, cd.catalog_number): cd
            for cd in ClassData.objects.all()
        }

    elif pick == 'course':
        # Cache Course rows
        return {
            (c.class_data.college, c.class_data.subject, c.class_data.catalog_number): c
            for c in Course.objects.select_related("class_data")
        }

    return {}

def hub_parser(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    courses = soup.find_all('div', 'cf-course-card')

    classdata_map = get_current_db_content('classdata')

    new_classdata = []

    updates = []  # Courses whose fields need updating
    hub_updates = {}  # map Course → list of hub_codes
    offered_updates = {}

    for course in courses:
        id = course.find('span', 'cf-course-id').text
        college, subject, catalog_number = id.split()
        key = (college, subject, catalog_number)
        # --- ClassData ---
        if key not in classdata_map:
            cd = ClassData(
                college=college,
                subject=subject,
                catalog_number=catalog_number,
            )
            classdata_map[key] = cd
            new_classdata.append(cd)

    # Save all new ClassData
    if new_classdata:
        ClassData.objects.bulk_create(new_classdata)

    # Refresh with IDs
    classdata_map = get_current_db_content('classdata')
    course_map = get_current_db_content('course')

    new_courses = []

    # Now process courses again for Course table
    for course in courses:
        id = course.find('span', 'cf-course-id').text
        college, subject, catalog_number = id.split()
        key = (college, subject, catalog_number)

        name = course.find('h3', 'bu_collapsible').text
        credits = course.find('span', 'cf-course-credits').text.split()[0]
        prereqs = course.find('span', 'cf-course-prereqs').text
        offered = course.find('span', 'cf-course-offered').text
        # print(offered) #Fall, Spring, Summer Fall and Spring
        description = course.find('p', 'cf-course-description').text

        offered_updates[key] = parse_terms(offered)
        if catalog_number[-1] == 'S':
            offered_updates[key].append('Summer')


        hub_units = []
        hub_list = course.find('ul', 'cf-hub-offerings')
        hubs = hub_list.find_all('li')
        for hub in hubs:
            label = hub.text.strip()
            code = HUB_LABEL_TO_CODE.get(label)
            if code:
                hub_units.append(code)

        classdata = classdata_map[key]

        # --- Course ---
        if key not in course_map:
            # Create new Course
            c = Course(
                class_data=classdata,
                name=name,
                credits=credits,
                description=description,
            )
            course_map[key] = c
            new_courses.append(c)
        else:
            # Update existing Course if fields changed
            c = course_map[key]
            changed = False
            if c.name != name:
                c.name = name
                changed = True
            if c.credits != credits:
                c.credits = credits
                changed = True
            if c.description != description:
                c.description = description
                changed = True

            if changed:
                updates.append(c)

        hub_updates[key] = hub_units

    # Bulk create new courses
    if new_courses:
        Course.objects.bulk_create(new_courses)

    # Bulk update modified courses
    if updates:
        Course.objects.bulk_update(updates, ["name", "credits", "description"])

    course_map = get_current_db_content('course')
    # --- Fix M2M hubs ---
    for key, hub_codes in hub_updates.items():
        course_obj = course_map[key]
        valid_hubs = Hub.objects.filter(unit_name__in=hub_codes)
        course_obj.hubs.set(valid_hubs)

    for key, offered_codes in offered_updates.items():
        course_obj = course_map[key]
        valid_sems = Offered.objects.filter(semester_offered__in=offered_codes)
        course_obj.offered.set(valid_sems)

    #span.cf-course-id
    #span.cf-course-credits
    #span.cf-course-offered
    #span.cf-course-prereqs
    #p.cf-course-description
    #ul.cf-hub-offerings
    #h3.bu_collapsible#text

    #div.bu_collapsible_section

class Command(BaseCommand):
    help = "Populates the database with scraped hub classes"

    def handle(self, *args, **options):
        for url in urls:
            print(f'Parsing: {url.split(prefix, 1)[1]}...')
            hub_parser(url)
            print(f'Finished parsing: {url.split(prefix, 1)[1]}.')
