from browser_skill import ApplicationSkill

class Skill:
    def __init__(self, name, description, action, keywords=None):
        self.name = name
        self.description = description
        self.action = action
        self.keywords = keywords or []

class SkillsManager:
    def __init__(self):
        self.skills = {}
        self._load_skills_from_config()
    
    def _load_skills_from_config(self):
        """Load all skills from configuration files"""
        # Create application skill manager and register skills
        app_skill = ApplicationSkill()
        app_skill.register_with_skills_manager(self)
        
        # Register built-in utility skills
        self.register_skill(
            "list_skills", 
            "Lists all available skills", 
            self.list_all_skills,
            ["list", "skills", "commands", "help", "what can you do"]
        )
    
    def register_skill(self, name, description, action, keywords=None):
        """Register a new skill"""
        self.skills[name] = Skill(name, description, action, keywords)
    
    def get_skill(self, name):
        """Get a skill by name"""
        return self.skills.get(name)
    
    def get_all_skills(self):
        """Get all registered skills"""
        return self.skills
    
    def list_all_skills(self):
        """List all available skills"""
        print("\nAvailable Skills:")
        print("-----------------")
        for name, skill in self.skills.items():
            print(f"{name}: {skill.description}")
            if skill.keywords:
                print(f"  Keywords: {', '.join(skill.keywords)}")
        print()
        return True

