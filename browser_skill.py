import webbrowser
import json
import os
import subprocess
from typing import Dict, Any, List

class ApplicationSkill:
    """A skill for opening URLs in Chrome browser and launching applications"""
    
    def __init__(self, config_file: str = "skills_config/applications.json"):
        self.config_file = config_file
        self.skills = {}
        self._load_skills()
    
    def _load_skills(self) -> None:
        """Load all skills from configuration file"""
        if not os.path.exists(os.path.dirname(self.config_file)):
            os.makedirs(os.path.dirname(self.config_file))
            
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    configs = json.load(f)
                    self._register_configs(configs)
            except Exception as e:
                print(f"Error loading skills configuration: {e}")
    
    def _register_configs(self, configs: List[Dict[str, Any]]) -> None:
        """Register skills from configuration list"""
        for config in configs:
            skill_type = config.get('type', '')
            name = config.get('name', '')
            
            if not name:
                continue
                
            if skill_type == 'chrome' and 'url' in config:
                self.skills[name] = {
                    'type': 'chrome',
                    'url': config['url'],
                    'description': config.get('description', f"Opens {name} in Chrome"),
                    'keywords': config.get('keywords', [name])
                }
            elif skill_type == 'launch' and 'executable' in config:
                self.skills[name] = {
                    'type': 'launch',
                    'executable': config['executable'],
                    'arguments': config.get('arguments', []),
                    'description': config.get('description', f"Launches {name}"),
                    'keywords': config.get('keywords', [name])
                }
    
    def execute_skill(self, name: str) -> bool:
        """Execute a skill by its name"""
        if name not in self.skills:
            return False
            
        skill_info = self.skills[name]
        skill_type = skill_info.get('type', '')
        
        if skill_type == 'chrome':
            return self._open_url(skill_info['url'])
        elif skill_type == 'launch':
            return self._launch_application(
                skill_info['executable'], 
                skill_info.get('arguments', [])
            )
        
        return False
    
    def _open_url(self, url: str) -> bool:
        """Open a URL in Chrome browser"""
        try:
            # Try to use Chrome browser
            browser = webbrowser.get('chrome %s')
            browser.open(url)
            return True
        except webbrowser.Error:
            # Fall back to default browser if Chrome is not available
            try:
                webbrowser.open(url)
                return True
            except Exception as e:
                print(f"Error opening URL: {e}")
                return False
    
    def _launch_application(self, executable: str, arguments: List[str] = None) -> bool:
        """Launch an application with optional arguments"""
        try:
            # Process environment variables in arguments
            if arguments:
                processed_args = []
                for arg in arguments:
                    if isinstance(arg, str) and '%' in arg:
                        # Replace environment variables
                        for env_var, env_val in os.environ.items():
                            placeholder = f"%{env_var}%"
                            if placeholder in arg:
                                arg = arg.replace(placeholder, env_val)
                    processed_args.append(arg)
            else:
                processed_args = []
                
            # Launch the application
            subprocess.Popen([executable] + processed_args)
            return True
        except Exception as e:
            print(f"Error launching application: {e}")
            return False
    
    def get_all_skills(self) -> Dict[str, Dict[str, Any]]:
        """Return all available skills"""
        return self.skills
    
    def register_with_skills_manager(self, skills_manager) -> None:
        """Register all skills with the skills manager"""
        for name, skill_info in self.skills.items():
            # Create a lambda that captures the current name
            action = lambda n=name: self.execute_skill(n)
            
            # Register with the skills manager
            skills_manager.register_skill(
                f"open_{name.lower().replace(' ', '_')}",
                skill_info['description'],
                action,
                skill_info['keywords']
            )

# Example usage
if __name__ == "__main__":
    app_skill = ApplicationSkill()
    print("Available skills:", app_skill.get_all_skills())
    
    # Test executing a skill
    skill_name = next(iter(app_skill.get_all_skills()), None)
    if skill_name:
        print(f"Executing {skill_name}...")
        app_skill.execute_skill(skill_name)

