"""
Seed tags and associate them with roundtables
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db_operations import add_tag, add_tag_to_roundtable, get_roundtable_insights

# Common TMT tags/topics
TAGS = [
    {"name": "AI Strategy", "category": "Technology"},
    {"name": "VR/AR Development", "category": "Technology"},
    {"name": "Content Moderation", "category": "Technology"},
    {"name": "Streaming Economics", "category": "Business Model"},
    {"name": "Content Investment", "category": "Business Model"},
    {"name": "International Growth", "category": "Market Expansion"},
    {"name": "5G Deployment", "category": "Infrastructure"},
    {"name": "Fiber Strategy", "category": "Infrastructure"},
    {"name": "Network Infrastructure", "category": "Infrastructure"},
    {"name": "Services Growth", "category": "Business Model"},
    {"name": "App Store Economics", "category": "Business Model"},
    {"name": "Subscription Strategy", "category": "Business Model"},
    {"name": "Cloud Competition", "category": "Competitive Landscape"},
    {"name": "AI Infrastructure", "category": "Technology"},
    {"name": "Enterprise Sales", "category": "Go-to-Market"},
    {"name": "Disney+ Strategy", "category": "Business Model"},
    {"name": "Content ROI", "category": "Business Model"},
    {"name": "Bundling Approach", "category": "Business Model"},
    {"name": "Wireless Competition", "category": "Competitive Landscape"},
    {"name": "Fixed Wireless", "category": "Technology"},
    {"name": "Customer Retention", "category": "Business Model"},
    {"name": "Azure Growth", "category": "Business Model"},
    {"name": "AI Integration", "category": "Technology"},
    {"name": "Enterprise Adoption", "category": "Go-to-Market"},
    {"name": "Podcasting Strategy", "category": "Business Model"},
    {"name": "Music Economics", "category": "Business Model"},
    {"name": "AI Features", "category": "Technology"},
    {"name": "Network Coverage", "category": "Infrastructure"},
    {"name": "Sprint Integration", "category": "M&A"},
    {"name": "5G Home Internet", "category": "Product"},
    {"name": "AI Chip Demand", "category": "Market Dynamics"},
    {"name": "Data Center Growth", "category": "Infrastructure"},
    {"name": "Competition", "category": "Competitive Landscape"},
    {"name": "Broadband Competition", "category": "Competitive Landscape"},
    {"name": "Streaming Strategy", "category": "Business Model"},
    {"name": "Cable Cord-Cutting", "category": "Market Trends"},
]

def seed_tags():
    """Seed tags and associate them with roundtables"""
    print("Seeding tags...")
    
    # Add all tags
    tag_map = {}
    for tag_data in TAGS:
        try:
            tag_id = add_tag(tag_data["name"], tag_data["category"])
            tag_map[tag_data["name"]] = tag_id
            print(f"Added tag: {tag_data['name']}")
        except Exception as e:
            print(f"Error adding tag {tag_data['name']}: {e}")
    
    print(f"\nTotal tags added: {len(tag_map)}")
    
    # Associate tags with roundtables based on their topics
    print("\nAssociating tags with roundtables...")
    roundtables = get_roundtable_insights()
    
    for roundtable in roundtables:
        if "id" in roundtable and "topics" in roundtable:
            roundtable_id = roundtable["id"]
            for topic in roundtable["topics"]:
                if topic in tag_map:
                    try:
                        add_tag_to_roundtable(roundtable_id, tag_map[topic])
                        print(f"Associated tag '{topic}' with roundtable {roundtable_id}")
                    except Exception as e:
                        print(f"Error associating tag: {e}")
    
    print("\nTag seeding complete!")

if __name__ == "__main__":
    seed_tags()
