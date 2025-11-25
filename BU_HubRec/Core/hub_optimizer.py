# hub_optimizer.py
print("$$$$$$$$$$HUB OPTIMIZER FILE LOADED (FINAL FIX)$$$$$$$$$$")
import random
from typing import List, Dict, Tuple, Any

# Import the necessary models from your Django app
from .models import Course, Hub 

# --- 1. Data Structure for Path Result ---

class CoursePath:
    """Represents a potential schedule path optimized for minimum courses (credit part commented out)."""
    
    # NOTE: total_credits is kept for reporting purposes but is NOT used for comparison/sorting.
    def __init__(self, courses: List[Course], total_credits: int):
        self.courses = courses
        self.total_credits = total_credits
        self.num_courses = len(courses)
        # Unique identifier for de-duplication
        self.course_ids = tuple(sorted([c.id for c in courses]))

    def __lt__(self, other):
        """Allows sorting based ONLY on: Fewest Courses.
        # COMMENTED OUT: The secondary sort by Fewest Credits.
        return (self.num_courses, self.total_credits) < \
               (other.num_courses, other.total_credits)
        """
        return self.num_courses < other.num_courses

    def __eq__(self, other):
        """Hashing based on course IDs for set operations."""
        return self.course_ids == other.course_ids

    def __hash__(self):
        """Hashing based on course IDs for set operations."""
        return hash(self.course_ids)

# --- 2. Data Preparation and Caching (OPTIMIZED) ---

def preprocess_courses(
    all_courses: List[Course],
) -> Tuple[Dict[int, List[str]], List[Course]]:
    """Caches course Hub attributes efficiently."""
    
    available_courses = all_courses

    # Cache Hubs only: {course_id: [hub_code, ...]}
    course_hubs_map = {}  
    processed_count = 0

    for course in available_courses:
        try:
            # This is fast because the Hub objects were prefetched in the main query.
            hub_codes = list(course.hubs.all().values_list('unit_name', flat=True))
            course_hubs_map[course.id] = hub_codes
            processed_count += 1
        except Exception as e:
            # Catch bad data gracefully
            # print(f"DEBUG_ERROR: Skipping Course ID {course.id} due to error: {e}")
            course_hubs_map[course.id] = []
        
    # print(f"DEBUG_PREPROCESS: Successfully mapped {len(course_hubs_map)} courses using optimized fetching.")
        
    return course_hubs_map, available_courses


# --- 3. Randomized Greedy Algorithm (Credit Penalty Removed) ---

def run_randomized_greedy(
    required_hubs: Dict[str, int], 
    available_courses: List[Course],
    course_hubs_map: Dict[int, List[str]],
) -> CoursePath | None:
    """Runs one iteration of the randomized greedy search, prioritizing Hub coverage only."""
    
    remaining_hubs = required_hubs.copy()
    current_path_courses = []
    available_course_ids = {c.id for c in available_courses} 
    current_credits = 0 # Kept for final reporting
    
    # Create a quick ID to Object map (slow to do this inside the loop)
    course_id_to_obj = {c.id: c for c in available_courses}
    
    while any(remaining_hubs.values()):
        
        candidates = [] # Stores: (Course_Object, Score)
        max_score = -1000.0 
        
        # 1. Score all remaining available courses
        for course_id in available_course_ids:
            course_obj = course_id_to_obj[course_id]
            
            hubs_covered = 0
            for hub_code in course_hubs_map[course_id]:
                if remaining_hubs.get(hub_code, 0) > 0:
                    hubs_covered += 1
            
            # Score Calculation: Prioritize Hub coverage, MINIMIZE credits part removed.
            
            # try:
            #     credits = float(course_obj.credits)
            # except (ValueError, TypeError):
            #     credits = 4.0 # Default if data is bad
                
            # total_score = (hubs_covered * 100) - (credits * 0.1) 

            # NEW SCORE: Only focus on Hubs Covered
            total_score = hubs_covered * 100 

            if total_score > max_score:
                max_score = total_score
                candidates = [(course_obj, total_score)]
            elif total_score == max_score:
                candidates.append((course_obj, total_score))
                
        if not candidates:
            # Cannot satisfy all remaining requirements
            return None 

        # 2. Probabilistic Selection
        TOLERANCE = 15 
        
        # top_candidates extracts only the Course objects from the list of (Course, Score) tuples
        # Note: Since the score is just (hubs_covered * 100), the tolerance is essentially for the number of hubs covered.
        top_candidates = [c for c, s in candidates if s >= (max_score - TOLERANCE)] 

        # *** CRITICAL FIX: This line was causing the unpacking error (cannot unpack non-iterable Course object) ***
        chosen_course = random.choice(top_candidates) 

        # 3. Update state
        course_id = chosen_course.id
        available_course_ids.remove(course_id)
        current_path_courses.append(chosen_course)
        
        # Update total credits (kept for reporting only)
        try:
            credits_int = int(chosen_course.credits)
        except (ValueError, TypeError):
            credits_int = 4
            
        current_credits += credits_int

        # Update remaining Hub requirements
        for hub_code in course_hubs_map[course_id]:
            if remaining_hubs.get(hub_code, 0) > 0:
                remaining_hubs[hub_code] -= 1
        
    return CoursePath(current_path_courses, current_credits)


# --- 4. Main Optimization Function ---

def optimize_schedule(context: Dict[str, Any], num_paths: int = 6, max_iterations: int = 1500) -> List[Dict]:
    """
    Coordinates the randomized greedy search and selects the top optimal paths 
    (now solely based on fewest courses).
    """
    print("--- HUB OPTIMIZER FUNCTION EXECUTED SUCCESSFULLY ---")
    
    # 1. Data Preparation and Fetching
    required_hubs_map = {h['code']: h['count'] for h in context.get('selected_hubs', [])}
    
    # CRITICAL: Use prefetch_related to load all Hubs efficiently
    all_courses = list(Course.objects.all().prefetch_related('hubs'))
    
    # print(f"DEBUG_DATA: Total courses fetched and prefetched from DB: {len(all_courses)}") 
    
    if not required_hubs_map or not all_courses:
        return []

    # Preprocess and cache data (now fast due to prefetch)
    course_hubs_map, available_courses = preprocess_courses(all_courses)
    
    # 2. Run Randomized Greedy Iterations
    all_paths = set()
    # print(f"DEBUG_OPTIMIZER: Starting {max_iterations} randomized iterations...")
    for i in range(max_iterations):
        path = run_randomized_greedy(
            required_hubs_map, 
            available_courses, 
            course_hubs_map, 
        )
        if path:
            all_paths.add(path)
            
    # 3. Select, Rank, and Filter Paths
    
    # Ranking is now purely by fewest courses due to the change in __lt__ in CoursePath
    ranked_paths = sorted(list(all_paths)) 
    
    final_paths_objects = []
    
    # Apply constraint (Max Courses)
    max_courses = context.get('num_courses')

    for path in ranked_paths:
        if max_courses is not None and path.num_courses > max_courses:
            continue

        final_paths_objects.append(path)
        if len(final_paths_objects) >= num_paths:
            break
            
    # 4. Final Conversion (CoursePath objects to Dictionaries for Template)
    final_paths_dicts = []
    for path_obj in final_paths_objects:
        final_paths_dicts.append({
            'num_courses': path_obj.num_courses,
            'total_credits': path_obj.total_credits, # Still reported
            'courses': [{
                'name': c.name, 
                'credits': c.credits, 
                'subject': c.class_data.subject, 
                'catalog_number': c.class_data.catalog_number,
                'hubs': course_hubs_map.get(c.id, []) # Use the cached map
            } for c in path_obj.courses]
        })
    
    # print(f"DEBUG_RETURN: Optimization finished. Found {len(final_paths_dicts)} optimal paths.")
    return final_paths_dicts