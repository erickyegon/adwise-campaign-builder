#!/usr/bin/env python3
"""
MongoDB Database Seeding Script for AdWise AI
Generates realistic campaign data for testing and demonstration
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import motor.motor_asyncio
from faker import Faker
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Faker for realistic data generation
fake = Faker()

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "adwise_ai"

# Realistic campaign data templates
CAMPAIGN_TEMPLATES = [
    {
        "name_template": "{season} {product} Campaign",
        "products": ["Fashion", "Electronics", "Home & Garden", "Sports", "Beauty", "Automotive"],
        "seasons": ["Spring", "Summer", "Fall", "Winter", "Holiday", "Back-to-School"],
        "objectives": ["Brand Awareness", "Lead Generation", "Sales", "App Installs", "Engagement"]
    },
    {
        "name_template": "{event} {action} Campaign",
        "events": ["Black Friday", "Cyber Monday", "Valentine's Day", "Mother's Day", "Father's Day"],
        "actions": ["Sale", "Promotion", "Special Offer", "Limited Time", "Exclusive Deal"],
        "objectives": ["Sales", "Revenue", "Conversions", "Traffic"]
    }
]

PLATFORMS = ["facebook", "instagram", "google_ads", "linkedin", "twitter", "tiktok", "snapchat"]
CAMPAIGN_STATUSES = ["draft", "review", "active", "paused", "completed"]
USER_ROLES = ["admin", "manager", "creator", "analyst"]

class DatabaseSeeder:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        
    async def seed_users(self, count: int = 100) -> List[str]:
        """Generate realistic user data"""
        print(f"🔄 Seeding {count} users...")
        
        users = []
        user_ids = []
        
        for i in range(count):
            profile = fake.profile()
            user = {
                "email": profile["mail"],
                "username": profile["username"],
                "password_hash": "$2b$12$LQv3c1yqBwEHxPuNY5Ynu.Are9xVQ5zQUH1Q5uQbtumy3gEap.Hha",  # "password123"
                "role": random.choice(USER_ROLES),
                "profile": {
                    "first_name": profile["name"].split()[0],
                    "last_name": profile["name"].split()[-1],
                    "avatar_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed={profile['username']}",
                    "timezone": random.choice(["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"]),
                    "phone": fake.phone_number(),
                    "company": fake.company(),
                    "job_title": fake.job()
                },
                "settings": {
                    "notifications": {
                        "email": random.choice([True, False]),
                        "push": random.choice([True, False]),
                        "sms": random.choice([True, False])
                    },
                    "theme": random.choice(["light", "dark", "auto"]),
                    "language": random.choice(["en", "es", "fr", "de", "ja"])
                },
                "created_at": fake.date_time_between(start_date="-2y", end_date="now"),
                "updated_at": fake.date_time_between(start_date="-30d", end_date="now"),
                "last_login": fake.date_time_between(start_date="-7d", end_date="now")
            }
            users.append(user)
        
        result = await self.db.users.insert_many(users)
        user_ids = [str(id) for id in result.inserted_ids]
        
        print(f"✅ Created {len(user_ids)} users")
        return user_ids
    
    async def seed_campaigns(self, user_ids: List[str], count: int = 10000) -> List[str]:
        """Generate realistic campaign data"""
        print(f"🔄 Seeding {count} campaigns...")
        
        campaigns = []
        campaign_ids = []
        
        for i in range(count):
            template = random.choice(CAMPAIGN_TEMPLATES)
            
            # Generate campaign name
            if "season" in template["name_template"]:
                name = template["name_template"].format(
                    season=random.choice(template["seasons"]),
                    product=random.choice(template["products"])
                )
            else:
                name = template["name_template"].format(
                    event=random.choice(template["events"]),
                    action=random.choice(template["actions"])
                )
            
            # Generate realistic budget
            budget_total = random.uniform(1000, 100000)
            budget_daily = budget_total / random.uniform(7, 90)  # 1 week to 3 months
            budget_spent = random.uniform(0, budget_total * 0.8)
            
            # Generate performance metrics
            impressions = random.randint(10000, 5000000)
            ctr = random.uniform(0.5, 8.0)  # Click-through rate
            clicks = int(impressions * (ctr / 100))
            conversion_rate = random.uniform(1.0, 15.0)
            conversions = int(clicks * (conversion_rate / 100))
            cpc = random.uniform(0.50, 5.00)  # Cost per click
            
            # Generate dates
            start_date = fake.date_time_between(start_date="-1y", end_date="+30d")
            end_date = start_date + timedelta(days=random.randint(7, 90))
            
            campaign = {
                "name": name,
                "description": fake.text(max_nb_chars=200),
                "status": random.choice(CAMPAIGN_STATUSES),
                "budget": {
                    "total": round(budget_total, 2),
                    "daily": round(budget_daily, 2),
                    "spent": round(budget_spent, 2),
                    "currency": "USD"
                },
                "targeting": {
                    "demographics": {
                        "age_min": random.randint(18, 35),
                        "age_max": random.randint(35, 65),
                        "genders": random.choice([["male"], ["female"], ["male", "female"]]),
                        "locations": random.sample([
                            "United States", "Canada", "United Kingdom", "Germany", 
                            "France", "Australia", "Japan", "Brazil"
                        ], random.randint(1, 4))
                    },
                    "interests": random.sample([
                        "Technology", "Fashion", "Sports", "Travel", "Food", "Music",
                        "Movies", "Books", "Gaming", "Fitness", "Art", "Business"
                    ], random.randint(2, 6)),
                    "behaviors": random.sample([
                        "Online Shoppers", "Frequent Travelers", "Tech Early Adopters",
                        "Luxury Shoppers", "Mobile Users", "Social Media Users"
                    ], random.randint(1, 3))
                },
                "platforms": random.sample(PLATFORMS, random.randint(1, 4)),
                "content": {
                    "headlines": [
                        fake.catch_phrase() for _ in range(random.randint(3, 8))
                    ],
                    "descriptions": [
                        fake.text(max_nb_chars=150) for _ in range(random.randint(2, 5))
                    ],
                    "call_to_actions": random.sample([
                        "Shop Now", "Learn More", "Sign Up", "Download", "Get Started",
                        "Book Now", "Try Free", "Contact Us", "Subscribe"
                    ], random.randint(1, 3))
                },
                "performance": {
                    "impressions": impressions,
                    "clicks": clicks,
                    "conversions": conversions,
                    "spend": round(budget_spent, 2),
                    "revenue": round(conversions * random.uniform(20, 200), 2),
                    "ctr": round(ctr, 2),
                    "cpc": round(cpc, 2),
                    "cpm": round(budget_spent / (impressions / 1000), 2),
                    "roas": round(random.uniform(2.0, 8.0), 2),
                    "conversion_rate": round(conversion_rate, 2)
                },
                "schedule": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "timezone": random.choice(["UTC", "America/New_York", "Europe/London"]),
                    "day_parting": {
                        "enabled": random.choice([True, False]),
                        "hours": list(range(9, 18)) if random.choice([True, False]) else list(range(24))
                    }
                },
                "team": {
                    "owner": random.choice(user_ids),
                    "collaborators": random.sample(user_ids, random.randint(1, 5)),
                    "approvers": random.sample(user_ids, random.randint(1, 3))
                },
                "tags": random.sample([
                    "Q1", "Q2", "Q3", "Q4", "Brand", "Performance", "Retargeting",
                    "Acquisition", "Retention", "Mobile", "Desktop", "Video", "Display"
                ], random.randint(1, 5)),
                "created_at": fake.date_time_between(start_date="-1y", end_date="now"),
                "updated_at": fake.date_time_between(start_date="-30d", end_date="now")
            }
            
            campaigns.append(campaign)
            
            # Progress indicator
            if (i + 1) % 1000 == 0:
                print(f"  Generated {i + 1}/{count} campaigns...")
        
        # Insert in batches for better performance
        batch_size = 1000
        for i in range(0, len(campaigns), batch_size):
            batch = campaigns[i:i + batch_size]
            result = await self.db.campaigns.insert_many(batch)
            campaign_ids.extend([str(id) for id in result.inserted_ids])
        
        print(f"✅ Created {len(campaign_ids)} campaigns")
        return campaign_ids
    
    async def seed_ads(self, campaign_ids: List[str], count: int = 50000):
        """Generate realistic ad data"""
        print(f"🔄 Seeding {count} ads...")
        
        ads = []
        
        for i in range(count):
            campaign_id = random.choice(campaign_ids)
            
            # Generate ad performance
            impressions = random.randint(1000, 500000)
            ctr = random.uniform(0.5, 12.0)
            clicks = int(impressions * (ctr / 100))
            conversions = int(clicks * random.uniform(0.01, 0.20))
            spend = random.uniform(50, 5000)
            
            ad = {
                "campaign_id": campaign_id,
                "name": f"{fake.catch_phrase()} - {random.choice(['Image', 'Video', 'Carousel'])} Ad",
                "type": random.choice(["image", "video", "carousel", "text", "collection"]),
                "platform": random.choice(PLATFORMS),
                "status": random.choice(["active", "paused", "draft", "archived"]),
                "content": {
                    "headline": fake.catch_phrase(),
                    "description": fake.text(max_nb_chars=125),
                    "call_to_action": random.choice([
                        "Shop Now", "Learn More", "Sign Up", "Download"
                    ]),
                    "image_url": f"https://picsum.photos/1200/630?random={i}",
                    "video_url": f"https://example.com/video_{i}.mp4" if random.choice([True, False]) else None
                },
                "targeting": {
                    "age_range": f"{random.randint(18, 35)}-{random.randint(35, 65)}",
                    "interests": random.sample([
                        "Technology", "Fashion", "Sports", "Travel", "Food"
                    ], random.randint(1, 3))
                },
                "performance": {
                    "impressions": impressions,
                    "clicks": clicks,
                    "conversions": conversions,
                    "spend": round(spend, 2),
                    "ctr": round(ctr, 2),
                    "cpc": round(spend / clicks if clicks > 0 else 0, 2),
                    "cpm": round(spend / (impressions / 1000), 2),
                    "conversion_rate": round((conversions / clicks * 100) if clicks > 0 else 0, 2)
                },
                "created_at": fake.date_time_between(start_date="-1y", end_date="now"),
                "updated_at": fake.date_time_between(start_date="-30d", end_date="now")
            }
            
            ads.append(ad)
            
            if (i + 1) % 5000 == 0:
                print(f"  Generated {i + 1}/{count} ads...")
        
        # Insert in batches
        batch_size = 1000
        for i in range(0, len(ads), batch_size):
            batch = ads[i:i + batch_size]
            await self.db.ads.insert_many(batch)
        
        print(f"✅ Created {count} ads")
    
    async def create_indexes(self):
        """Create database indexes for optimal performance"""
        print("🔄 Creating database indexes...")
        
        # Users indexes
        await self.db.users.create_index("email", unique=True)
        await self.db.users.create_index("username", unique=True)
        await self.db.users.create_index("role")
        
        # Campaigns indexes
        await self.db.campaigns.create_index([("status", 1), ("created_at", -1)])
        await self.db.campaigns.create_index("team.owner")
        await self.db.campaigns.create_index("platforms")
        await self.db.campaigns.create_index("tags")
        await self.db.campaigns.create_index([("performance.roas", -1)])
        
        # Ads indexes
        await self.db.ads.create_index("campaign_id")
        await self.db.ads.create_index([("platform", 1), ("status", 1)])
        await self.db.ads.create_index([("performance.ctr", -1)])
        
        print("✅ Database indexes created")
    
    async def seed_all(self, users_count=100, campaigns_count=10000, ads_count=50000):
        """Seed all collections with realistic data"""
        print("🚀 Starting database seeding process...")
        print(f"Target: {users_count} users, {campaigns_count} campaigns, {ads_count} ads")
        
        # Clear existing data
        await self.db.users.delete_many({})
        await self.db.campaigns.delete_many({})
        await self.db.ads.delete_many({})
        
        # Seed data
        user_ids = await self.seed_users(users_count)
        campaign_ids = await self.seed_campaigns(user_ids, campaigns_count)
        await self.seed_ads(campaign_ids, ads_count)
        
        # Create indexes
        await self.create_indexes()
        
        print("🎉 Database seeding completed successfully!")
        print(f"📊 Final counts:")
        print(f"  Users: {await self.db.users.count_documents({})}")
        print(f"  Campaigns: {await self.db.campaigns.count_documents({})}")
        print(f"  Ads: {await self.db.ads.count_documents({})}")

async def main():
    """Main seeding function"""
    seeder = DatabaseSeeder()
    
    # Seed with 1M+ records for realistic testing
    await seeder.seed_all(
        users_count=1000,      # 1K users
        campaigns_count=100000, # 100K campaigns  
        ads_count=1000000      # 1M ads
    )

if __name__ == "__main__":
    asyncio.run(main())
