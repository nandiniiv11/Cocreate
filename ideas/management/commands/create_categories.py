from django.core.management.base import BaseCommand
from ideas.models import Category

class Command(BaseCommand):
    help = 'Creates initial categories for ideas'

    def handle(self, *args, **kwargs):
        categories = [
            'Technology',
            'Business',
            'Education',
            'Health',
            'Environment',
            'Social',
            'Entertainment',
            'Art',
            'Science',
            'Other'
        ]
        
        for category_name in categories:
            Category.objects.get_or_create(name=category_name)
            
        self.stdout.write(self.style.SUCCESS('Successfully created categories!'))