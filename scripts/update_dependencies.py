
import os
import re
from pathlib import Path

def update_router_file(file_path):
    """Update a router file to use universal dependencies"""
    try:
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
    
    original_content = content
    
    
    old_imports = [
        "from app.auth.security import get_current_active_user",
        "from ..auth.security import get_current_active_user",
        "from ...auth.security import get_current_active_user",
        "from .auth.security import get_current_active_user"
    ]
    
    for old_import in old_imports:
        if old_import in content:
            content = content.replace(old_import, "from app.auth.security import get_current_active_user_or_admin")
    
    
    
    content = re.sub(
        r'(current_\w+)\s*:\s*User\s*=\s*Depends\s*\(\s*get_current_active_user\s*\)',
        r'current: Union[User, Admin] = Depends(get_current_active_user_or_admin)',
        content
    )
    
    
    content = re.sub(
        r'(\w+)\s*:\s*User\s*=\s*Depends\s*\(\s*get_current_active_user\s*\)',
        r'current: Union[User, Admin] = Depends(get_current_active_user_or_admin)',
        content
    )
    
    
    old_dep = "current_user: User = Depends(get_current_active_user)"
    if old_dep in content:
        content = content.replace(old_dep, "current: Union[User, Admin] = Depends(get_current_active_user_or_admin)")
    
    
    if "Union[User, Admin]" in content and "from typing import Union" not in content:
        
        if "from typing import" in content:
            
            content = re.sub(
                r'from typing import (.*)',
                r'from typing import Union, \1',
                content
            )
        else:
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('import') or line.startswith('from'):
                    
                    lines.insert(i, 'from typing import Union')
                    break
            else:
                
                lines.insert(0, 'from typing import Union')
            content = '\n'.join(lines)
    
    
    if "from typing import" in content and "Union" not in content and "Union[User, Admin]" in content:
        content = re.sub(
            r'from typing import (?!.*Union)(.*)',
            r'from typing import Union, \1',
            content
        )
    
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {file_path}")
    else:
        print(f"No changes needed: {file_path}")

def update_dependencies_py():
    """Update the dependencies.py file to include the new function"""
    deps_path = "app/dependencies.py"
    if os.path.exists(deps_path):
        try:
            with open(deps_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(deps_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        
        if "get_current_active_user_or_admin" not in content:
            
            new_import = "from app.auth.security import get_current_active_user_or_admin"
            if new_import not in content:
                
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith("from app.auth.security import"):
                        
                        lines[i] = line.rstrip() + ", get_current_active_user_or_admin"
                        break
                else:
                    
                    for i, line in enumerate(lines):
                        if "import" in line and "app.auth.security" in content:
                            
                            for j in range(i, len(lines)):
                                if lines[j].strip() == "":
                                    lines.insert(j, new_import)
                                    break
                            break
                    else:
                        lines.insert(1, new_import)
                
                content = '\n'.join(lines)
            
            
            if "__all__" in content:
                content = content.replace(
                    '__all__ = [',
                    '__all__ = [\n    "get_current_active_user_or_admin",'
                )
            
            with open(deps_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated dependencies.py")
    else:
        print(f"Warning: {deps_path} not found")


router_files = [
    "app/routers/users.py",
    "app/routers/health.py", 
    "app/routers/notifications.py",
    "app/routers/caregivers.py",
    "app/routers/leaderboard.py",
]


update_dependencies_py()


for file in router_files:
    if os.path.exists(file):
        update_router_file(file)
    else:
        print(f"Warning: {file} not found")

print("\nUpdate completed!")
