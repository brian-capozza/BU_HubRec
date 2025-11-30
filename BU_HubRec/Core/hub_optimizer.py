# hub_optimizer.py
# This script contains the core logic for recommending course schedules.
# It uses a randomized greedy algorithm combined with the OpenAI API for intelligent filtering.

import random
import json
from typing import List, Dict, Tuple, Any

# Required for communicating with the AI service
import openai

# Import your Django models
from .models import Course, Hub 

# ====================================================================
# API CONFIGURATION & COST TRACKING
# ====================================================================

# ⚠️ SECURITY WARNING: In a real application, load this from environment variables or Django settings!
OPENAI_API_KEY = "" 
AI_MODEL_NAME = "gpt-3.5-turbo" 

# Current approximate pricing for gpt-3.5-turbo (per 1,000 tokens)
GPT_3_5_TURBO_PRICING = {
    "input_cost_per_k_token": 0.0005,  # Cost to send the prompt (input)
    "output_cost_per_k_token": 0.0015, # Cost for the AI's response (output)
}

# Initialize the OpenAI client once when the script loads
try:
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    print(f"ERROR: OpenAI client initialization failed. Check API key. Error: {e}")
    openai_client = None


# HELPER FUNCTION FOR BATCHING
def chunk_list(data: list, chunk_size: int):
    """
    Splits a large list into smaller chunks (batches). 
    This is necessary to keep API requests under the OpenAI token limit.
    """
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


# ====================================================================
# AI CLASSIFICATION FUNCTION (BATCHED WITH COST TRACKING)
# ====================================================================

def classify_courses_by_interest(interests_text: str, courses: List[Course]) -> List[Course]:
    """
    Filters a list of courses by calling the OpenAI API. Courses are sent 
    in batches to prevent exceeding the token limit. Tracks and prints the cost.
    """
    if not openai_client:
        print("AI CLASSIFICATION FAILED: Client not initialized. Returning all courses.")
        return courses # Fallback: return original list if API setup failed

    if not courses:
        print("AI CLASSIFICATION: No courses available for evaluation.")
        return []
        
    print(f"AI CLASSIFICATION STARTED for {len(courses)} courses.")
    
    # Variables to track token usage across all batches
    total_input_tokens = 0
    total_output_tokens = 0
    
    # 1. Prepare Course Data for the AI
    course_data_for_ai = []
    for course in courses:
        description = getattr(course, 'description', 'No description available.')
        course_data_for_ai.append({
            'id': course.id,
            'name': course.name,
            # Truncate descriptions to save tokens. 500 characters is a safe limit.
            'description': description[:1500] + '...' if len(description) > 500 else description,
        })
        
    # 2. Set Batch Size
    BATCH_SIZE = 100 # Sending 100 courses per API call
    
    all_matched_course_ids = set()
    num_batches = (len(course_data_for_ai) + BATCH_SIZE - 1) // BATCH_SIZE
    
    # 3. Process in Batches and Call API
    for i, batch in enumerate(chunk_list(course_data_for_ai, BATCH_SIZE)):
        print(f"Processing Batch {i+1} of {num_batches} ({len(batch)} courses)...")
        
        system_prompt = (
            "You are an expert course selection assistant. Evaluate the courses against the user's specified interests, be careful and make sure the course descriptions align with the interests. "
            "Do not include courses with significant prerequisites, often indicated in the description by prereqs: . . ., if it is just an early writing class like wr 120 0r 150 that is ok include those classes."
            "Only return the results as a single JSON array with 'id' (integer) and 'classification' ('match' or 'no_match')."
        )
        
        user_prompt = (
            f"User's Interests: '{interests_text}'\n\n"
            "Evaluate the following courses:\n"
            f"{json.dumps(batch, indent=2)}"
        )
        
        try:
            response = openai_client.chat.completions.create(
                model=AI_MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0 # Use 0.0 for deterministic classification
            )
            
            # Record the token usage for cost calculation
            if response.usage:
                total_input_tokens += response.usage.prompt_tokens
                total_output_tokens += response.usage.completion_tokens
            
            ai_output_text = response.choices[0].message.content
            ai_json = json.loads(ai_output_text)
            
            # Safely get the list of classifications from the JSON response
            classifications = ai_json.get('results', []) or ai_json.get('data', [])
            if not classifications and isinstance(ai_json, list):
                classifications = ai_json
            
            # 4. Collect matched IDs from this batch
            matched_ids_in_batch = {
                str(c.get('id')) for c in classifications 
                if c.get('classification', '').lower() == 'match'
            }
            all_matched_course_ids.update(matched_ids_in_batch)

        except Exception as e:
            print(f"API Error processing batch {i+1}: {e}. Skipping this batch.")
            continue # Move to the next batch even if this one fails

    # 5. Final Cost Calculation and Output
    input_cost = (total_input_tokens / 1000) * GPT_3_5_TURBO_PRICING["input_cost_per_k_token"]
    output_cost = (total_output_tokens / 1000) * GPT_3_5_TURBO_PRICING["output_cost_per_k_token"]
    total_cost = input_cost + output_cost

    print("\n💸 API COST SUMMARY 💸")
    print(f"Model Used: {AI_MODEL_NAME}")
    print(f"Total Input Tokens: {total_input_tokens}")
    print(f"Total Output Tokens: {total_output_tokens}")
    print(f"Estimated Cost (Input): ${input_cost:,.6f}")
    print(f"Estimated Cost (Output): ${output_cost:,.6f}")
    print(f"TOTAL ESTIMATED API COST: ${total_cost:,.6f}")
    print("--------------------------\n")

    # 6. Final Filtering: return Course objects that matched any ID
    matched_courses = [
        course for course in courses 
        if str(course.id) in all_matched_course_ids
    ]
    
    print(f"AI CLASSIFICATION COMPLETE: {len(matched_courses)} courses matched user interests.")
    return matched_courses


# ====================================================================
# CORE LOGIC: Data Structures
# ====================================================================

class CoursePath:
    """
    Represents a complete, valid schedule path (a list of courses). 
    Used to store and compare potential schedules based on the number of courses (fewer is better).
    """
    def __init__(self, courses: List[Course], total_credits: int):
        self.courses = courses
        self.total_credits = total_credits
        self.num_courses = len(courses)
        # Use a sorted tuple of IDs for reliable comparison and hashing in a set
        self.course_ids = tuple(sorted([c.id for c in courses]))

    # Methods for sorting the list (prioritizing fewer courses)
    def __lt__(self, other):
        return self.num_courses < other.num_courses

    def __eq__(self, other):
        return self.course_ids == other.course_ids

    def __hash__(self):
        return hash(self.course_ids)

# Data Preparation and Caching
def preprocess_courses(
    all_courses: List[Course],
) -> Tuple[Dict[int, List[str]], List[Course]]:
    """
    Efficiently builds a map from Course ID to the Hubs it satisfies. 
    Queries the M2M table directly to avoid complex ORM issues.
    """
    
    available_courses = all_courses
    course_ids = [c.id for c in available_courses]
    course_hubs_map = {cid: [] for cid in course_ids} 
    
    # 1. Get the Hub IDs and Names
    hub_data = Hub.objects.filter(course__in=course_ids).values('pk', 'unit_name')
    hub_id_to_name = {data['pk']: data['unit_name'] for data in hub_data}
    
    # 2. Get the M2M linkages (course_id, hub_id) using the intermediate table
    try:
        m2m_linkages = Course.hubs.through.objects.filter(course_id__in=course_ids).values('course_id', 'hub_id')
    except Exception as e:
        print(f"ERROR: Failed to query M2M linkages: {e}")
        return course_hubs_map, available_courses 

    # 3. Build the final map in Python memory
    for linkage in m2m_linkages:
        course_id = linkage['course_id']
        hub_id = linkage['hub_id']
        hub_code = hub_id_to_name.get(hub_id)
        
        if hub_code:
            course_hubs_map[course_id].append(hub_code)
        
    return course_hubs_map, available_courses


# Randomized Greedy Algorithm
def run_randomized_greedy(
    required_hubs: Dict[str, int], 
    available_courses: List[Course],
    course_hubs_map: Dict[int, List[str]],
) -> CoursePath | None:
    """
    Runs one iteration of the randomized greedy search. It iteratively selects the course 
    that covers the most *remaining* Hub requirements to find a minimum-course solution.
    """
    
    remaining_hubs = required_hubs.copy()
    current_path_courses = []
    available_course_ids = {c.id for c in available_courses} 
    current_credits = 0 
    course_id_to_obj = {c.id: c for c in available_courses}
    
    # Loop until all required Hub counts are satisfied
    while any(remaining_hubs.values()):
        candidates = []
        max_score = -1000.0 
        
        # Scoring phase: Find the best course to take next
        for course_id in available_course_ids:
            course_obj = course_id_to_obj[course_id]
            hubs_covered = 0
            for hub_code in course_hubs_map[course_id]:
                # Check if this course covers a Hub we still need
                if remaining_hubs.get(hub_code, 0) > 0:
                    hubs_covered += 1
            
            # Score is based purely on coverage of remaining requirements
            total_score = hubs_covered * 100 

            # Maintain a list of candidates that are top-scoring
            if total_score >= max_score:
                if total_score > max_score:
                    max_score = total_score
                    candidates = [(course_obj, total_score)]
                else:
                    candidates.append((course_obj, total_score))
                
        if not candidates:
            # Failed to cover all requirements with remaining courses
            return None 

        # Randomized Selection: Choose from the top candidates to explore different paths (simulated annealing)
        TOLERANCE = 15 
        top_candidates = [c for c, s in candidates if s >= (max_score - TOLERANCE)] 
        chosen_course = random.choice(top_candidates) 

        # Update state after selection
        course_id = chosen_course.id
        available_course_ids.remove(course_id)
        current_path_courses.append(chosen_course)
        
        # Calculate credits safely
        try:
            credits_int = int(chosen_course.credits)
        except (ValueError, TypeError):
            credits_int = 4
        current_credits += credits_int

        # Decrement the required count for the Hubs covered by the chosen course
        for hub_code in course_hubs_map[course_id]:
            if remaining_hubs.get(hub_code, 0) > 0:
                remaining_hubs[hub_code] -= 1
        
    return CoursePath(current_path_courses, current_credits)


# Main Optimization Function
def optimize_schedule(context: Dict[str, Any], num_paths: int = 6, max_iterations: int = 1500) -> List[Dict]:
    """
    The central function that runs the entire pipeline: filtering, AI classification, and optimization.
    It takes user input (Hubs, Interests) and returns a list of recommended schedules.
    """
    print("HUB OPTIMIZER FUNCTION EXECUTED")
    
    required_hubs_map = {h['code']: h['count'] for h in context.get('selected_hubs', [])}
    interests_text = context.get('interests', '') 

    if not required_hubs_map:
        return []

    # 1. Load all courses from the database efficiently
    try:
        all_courses = list(
            Course.objects.all().select_related('class_data') 
        )
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to fetch all courses: {e}")
        return []

    required_hub_names = set(required_hubs_map.keys())
    
    # Preprocess all data by building the Hub map
    course_hubs_map, _ = preprocess_courses(all_courses)

    # 2. Python-based filtering: keep only courses relevant to the required Hubs
    hub_relevant_courses = []
    for course in all_courses:
        course_hubs = course_hubs_map.get(course.id, [])
        if required_hub_names.intersection(course_hubs):
            hub_relevant_courses.append(course)

    print(f"Filter 1 (Hub Relevance): Course count is {len(hub_relevant_courses)}")
    
    # 3. AI-based filtering: use the batched OpenAI function to filter by user interests
    if interests_text:
        relevance_filtered_courses = classify_courses_by_interest(
            interests_text, 
            hub_relevant_courses 
        )
    else:
        relevance_filtered_courses = hub_relevant_courses
    
    print(f"Filter 2 (AI Relevance): Course count is {len(relevance_filtered_courses)}")
    
    if not relevance_filtered_courses:
        print("No relevant courses found after all filters. Returning empty schedule.")
        return []

    # 4. Optimization Setup and Execution
    available_courses = relevance_filtered_courses
    
    # Run Randomized Greedy Iterations to find optimal paths
    all_paths = set()
    for i in range(max_iterations):
        path = run_randomized_greedy(
            required_hubs_map, 
            available_courses, 
            course_hubs_map, 
        )
        if path:
            all_paths.add(path)
            
    # 5. Select, Rank, and Filter Paths
    # Sort paths (fewest courses first)
    ranked_paths = sorted(list(all_paths)) 
    final_paths_objects = []
    max_courses = context.get('num_courses')

    for path in ranked_paths:
        # Respect user's constraint on max number of courses
        if max_courses is not None and path.num_courses > max_courses:
            continue
        final_paths_objects.append(path)
        if len(final_paths_objects) >= num_paths:
            break
            
    # 6. Final Conversion from internal CoursePath objects to output dictionaries
    final_paths_dicts = []
    for path_obj in final_paths_objects:
        final_paths_dicts.append({
            'num_courses': path_obj.num_courses,
            'total_credits': path_obj.total_credits, 
            'courses': [{
                'name': c.name, 
                'credits': c.credits, 
                'subject': c.class_data.subject, 
                'catalog_number': c.class_data.catalog_number,
                'hubs': course_hubs_map.get(c.id, [])
            } for c in path_obj.courses]
        })
    
    print(f"Optimization finished. Found {len(final_paths_dicts)} optimal paths.")
    return final_paths_dicts