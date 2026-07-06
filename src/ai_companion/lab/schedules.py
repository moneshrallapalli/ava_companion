from datetime import datetime

class ScheduleContextGenerator:
    
    
    SCHEDULE = {
    "00:00-06:00": "Sleeping",
    "06:00-06:10": "Wake up, hydrate (500 mL water)",
    "06:10-06:30": "Morning hygiene & bath",
    "06:30-06:45": "Light stretching / mobility",
    "06:45-07:15": "Healthy breakfast (high protein, balanced carbs & fruits)",
    "07:15-08:00": "Prepare for work/study & planning",
    "08:00-10:30": "Work / Study",
    "10:30-10:45": "Healthy snack (nuts, yogurt, or fruit)",
    "10:45-13:00": "Work / Study",
    "13:00-13:30": "Healthy lunch (protein, vegetables, whole grains)",
    "13:30-14:00": "Short walk & relaxation",
    "14:00-17:00": "Work / Study",
    "17:00-18:15": "Gym (strength training + cardio)",
    "18:15-18:30": "Post-workout protein shake / snack",
    "18:30-19:00": "Evening walk",
    "19:00-19:20": "Second bath & freshen up",
    "19:20-20:00": "Healthy dinner (lean protein, vegetables, healthy fats)",
    "20:00-21:30": "Reading, hobbies, family time, or learning",
    "21:30-21:45": "Prepare meals/clothes for tomorrow",
    "21:45-22:15": "Light stretching, meditation, or journaling",
    "22:15-22:45": "Screen-free relaxation",
    "22:45-23:00": "Brush teeth, skincare, bedtime routine",
    "23:00-00:00": "Sleeping"
}
    @classmethod
    def get_current_activity(cls):
        now = datetime.now().time()
        for time_range, activity in cls.SCHEDULE.items():
            start_str, end_str = time_range.split("-")
            start = datetime.strptime(start_str,"%H:%M").time()
            end = datetime.strptime(end_str,"%H:%M").time()
            if start <= now <= end:
                return activity
        return None
