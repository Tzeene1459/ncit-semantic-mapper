import json
import os
from datetime import datetime, date
import pandas as pd

class DataManager:
    def __init__(self, data_dir="training_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def get_filename(self, date_obj=None):
        """Get filename for training data based on date"""
        if date_obj is None:
            date_obj = date.today()
        return os.path.join(self.data_dir, f"training_data_{date_obj.strftime('%Y%m%d')}.json")
    
    def save_entry(self, data):
        """Save a single training data entry"""
        filename = self.get_filename()
        
        # Load existing data
        existing_data = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                existing_data = []
        
        # Append new data
        existing_data.append(data)
        
        # Save back to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, default=str)
    
    def load_data(self, date_obj=None):
        """Load training data for a specific date"""
        filename = self.get_filename(date_obj)
        
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def get_statistics(self):
        """Get training data statistics"""
        today_data = self.load_data()
        
        stats = {
            'entries_today': len(today_data),
            'total_queries': len(set(entry.get('query', '') for entry in today_data)),
            'avg_confidence': 0,
            'quality_distribution': {}
        }
        
        if today_data:
            # Calculate average confidence
            confidence_map = {
                'Very Confident': 4,
                'Confident': 3,
                'Somewhat Confident': 2,
                'Not Confident': 1
            }
            
            confidences = [confidence_map.get(entry.get('confidence', 'Not Confident'), 1) for entry in today_data]
            stats['avg_confidence'] = round(sum(confidences) / len(confidences), 2)
            
            # Quality distribution
            qualities = [entry.get('overall_quality', 'Unknown') for entry in today_data]
            stats['quality_distribution'] = {q: qualities.count(q) for q in set(qualities)}
        
        return stats

# Convenience function for backward compatibility
def save_training_data(data):
    """Save training data using DataManager"""
    manager = DataManager()
    manager.save_entry(data)