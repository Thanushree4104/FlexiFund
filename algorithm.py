# Matching algorithm for finding connections between users

def calculate_match_score(user_profile, match_criteria):
    """
    Calculate a match score between a user profile and match criteria
    Returns a score between 0-100
    """
    score = 0
    
    # Calculate match based on values (most important)
    value_matches = len([value for value in user_profile['values'] if value in match_criteria['values']])
    score += (value_matches / max(len(user_profile['values']), len(match_criteria['values']))) * 40
    
    # Calculate match based on industry
    industry_matches = len([ind for ind in user_profile['industry'] if ind in match_criteria['industry']])
    score += (industry_matches / max(len(user_profile['industry']), len(match_criteria['industry']))) * 20
    
    # Calculate match based on skills
    skill_matches = len([skill for skill in user_profile['skills'] if skill in match_criteria['skills']])
    score += (skill_matches / max(len(user_profile['skills']), len(match_criteria['skills']))) * 20
    
    # Calculate match based on goals
    goal_matches = 0
    for goal in user_profile['goals']:
        for match_goal in match_criteria['goals']:
            if match_goal.lower() in goal.lower():
                goal_matches += 1
                break
    
    score += (goal_matches / max(len(user_profile['goals']), len(match_criteria['goals']))) * 20
    
    # Adjust score based on experience range
    if (user_profile['experience'] >= match_criteria['experience_min'] and 
            user_profile['experience'] <= match_criteria['experience_max']):
        score += 10
    else:
        score -= 10
    
    # Normalize score to be 0-100
    return min(max(round(score), 0), 100)

def find_matches(profile, criteria, all_users):
    """
    Find matches for a profile based on criteria
    Returns sorted list of profiles with match scores
    """
    # Filter users based on role and exclude the current user
    potential_matches = [user for user in all_users 
                        if user['id'] != profile['id'] and user['role'] == criteria['role']]
    
    # Calculate match scores
    matches_with_scores = []
    for user in potential_matches:
        user_copy = user.copy()
        user_copy['match_score'] = calculate_match_score(user, criteria)
        matches_with_scores.append(user_copy)
    
    # Sort by match score (highest first)
    return sorted(matches_with_scores, key=lambda x: x['match_score'], reverse=True)
