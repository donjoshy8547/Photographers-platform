from django.core.management.base import BaseCommand
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Debug template directory resolution'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Django Template Debugging Tool'))
        self.stdout.write(f"BASE_DIR: {settings.BASE_DIR}")
        
        for template_config in settings.TEMPLATES:
            self.stdout.write("\nTemplate Engine Configuration:")
            self.stdout.write(f"Backend: {template_config['BACKEND']}")
            self.stdout.write(f"APP_DIRS: {template_config['APP_DIRS']}")
            
            self.stdout.write("\nTemplate Directories:")
            for dir_path in template_config['DIRS']:
                self.stdout.write(f"- {dir_path}")
                if os.path.exists(dir_path):
                    self.stdout.write(self.style.SUCCESS(f"  EXISTS: {dir_path}"))
                    # List subdirectories 
                    for subdir in os.listdir(dir_path):
                        subpath = os.path.join(dir_path, subdir)
                        if os.path.isdir(subpath):
                            self.stdout.write(f"    └── {subdir}/")
                else:
                    self.stdout.write(self.style.ERROR(f"  DOES NOT EXIST: {dir_path}"))

        # Check common template paths
        template_paths = [
            os.path.join(settings.BASE_DIR, 'templates'),
            os.path.join(settings.BASE_DIR, 'Templates'),
            os.path.join(settings.BASE_DIR, 'app', 'templates'),
            os.path.join(settings.BASE_DIR, 'app', 'Templates'),
        ]
        
        self.stdout.write("\nChecking common template paths:")
        for path in template_paths:
            if os.path.exists(path):
                self.stdout.write(self.style.SUCCESS(f"EXISTS: {path}"))
            else:
                self.stdout.write(self.style.WARNING(f"Missing: {path}"))
