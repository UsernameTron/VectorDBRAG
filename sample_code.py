"""
Sample Python Code for Testing Code Analysis Agents

This file contains various code patterns that agents can analyze,
debug, and suggest improvements for.
"""

import os
import sys
from typing import List, Dict, Optional

class DataProcessor:
    """Sample class for data processing operations."""
    
    def __init__(self, data_source: str):
        self.data_source = data_source
        self.processed_data = []
        
    def load_data(self) -> List[Dict]:
        """Load data from source file."""
        try:
            # Potential bug: No file validation
            with open(self.data_source, 'r') as f:
                data = f.read()
            return self.parse_data(data)
        except Exception as e:
            # Poor error handling
            print(f"Error: {e}")
            return []
    
    def parse_data(self, raw_data: str) -> List[Dict]:
        """Parse raw data into structured format."""
        # Inefficient parsing - room for improvement
        lines = raw_data.split('\n')
        result = []
        for line in lines:
            if line.strip():
                parts = line.split(',')
                # No error checking for malformed data
                result.append({
                    'id': parts[0],
                    'name': parts[1],  # IndexError possible here
                    'value': float(parts[2])  # ValueError possible here
                })
        return result
    
    def process_data(self) -> None:
        """Process the loaded data."""
        data = self.load_data()
        # Performance issue: inefficient loop
        for item in data:
            # Memory inefficient - could use generator
            processed_item = self.transform_item(item)
            self.processed_data.append(processed_item)
    
    def transform_item(self, item: Dict) -> Dict:
        """Transform a single data item."""
        # Business logic that could be improved
        return {
            'id': item['id'],
            'name': item['name'].upper(),
            'value': item['value'] * 1.1,
            'category': self.categorize_value(item['value'])
        }
    
    def categorize_value(self, value: float) -> str:
        """Categorize value into ranges."""
        # Could use more elegant approach
        if value < 10:
            return 'low'
        elif value < 50:
            return 'medium'
        else:
            return 'high'
    
    def get_summary(self) -> Dict:
        """Get summary statistics."""
        if not self.processed_data:
            self.process_data()
        
        # Inefficient calculations
        total = sum(item['value'] for item in self.processed_data)
        count = len(self.processed_data)
        average = total / count if count > 0 else 0
        
        categories = {}
        for item in self.processed_data:
            cat = item['category']
            if cat in categories:
                categories[cat] += 1
            else:
                categories[cat] = 1
                
        return {
            'total_items': count,
            'average_value': average,
            'categories': categories
        }

# Usage example with potential issues
def main():
    # Hard-coded file path - should be configurable
    processor = DataProcessor("data.csv")
    
    try:
        summary = processor.get_summary()
        print(f"Summary: {summary}")
    except Exception as e:
        # Generic error handling
        print(f"Failed to process data: {e}")

if __name__ == "__main__":
    main()
