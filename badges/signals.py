import django.dispatch

badge_awarded = django.dispatch.Signal(providing_args=['laureate', 'badge'])
