import re
import difflib

class CommandProcessor:
    def __init__(self, skills_manager):
        self.skills_manager = skills_manager
    
    def process_command(self, command_text):
        """
        Process the voice command and return the appropriate skill
        
        Returns:
        tuple: (skill_name, skill_function) or (None, None) if no match
        """
        command_text = command_text.lower()
        
        # First try direct skill name matching
        for name, skill in self.skills_manager.get_all_skills().items():
            if name.lower() in command_text:
                print(f"Direct match found for skill: {name}")
                return name, skill.action
        
        # Then try keyword matching
        best_match = None
        best_score = 0
        
        for name, skill in self.skills_manager.get_all_skills().items():
            # Check for keyword matches
            for keyword in skill.keywords:
                if keyword.lower() in command_text:
                    # Calculate match score based on keyword length and position
                    score = len(keyword) / len(command_text)
                    if score > best_score:
                        best_score = score
                        best_match = (name, skill.action)
        
        if best_match and best_score > 0.1:  # Threshold to avoid false positives
            print(f"Keyword match found for skill: {best_match[0]} (score: {best_score})")
            return best_match
        
        # If no direct or keyword match, try fuzzy matching
        command_words = set(re.findall(r'\b\w+\b', command_text))
        best_match = None
        best_score = 0
        
        for name, skill in self.skills_manager.get_all_skills().items():
            # Create a set of words from skill name, description and keywords
            skill_words = set(re.findall(r'\b\w+\b', f"{name} {skill.description}"))
            skill_words.update(skill.keywords)
            
            # Calculate similarity score
            common_words = command_words.intersection(skill_words)
            if common_words:
                score = len(common_words) / len(command_words)
                if score > best_score:
                    best_score = score
                    best_match = (name, skill.action)
        
        if best_match and best_score > 0.3:  # Higher threshold for fuzzy matching
            print(f"Fuzzy match found for skill: {best_match[0]} (score: {best_score})")
            return best_match
            
        print("No matching skill found")
        return None, None