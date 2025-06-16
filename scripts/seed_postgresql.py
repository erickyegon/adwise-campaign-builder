#!/usr/bin/env python3
"""
PostgreSQL Analytics Database Seeding Script for AdWise AI
Generates realistic analytics and performance data for comprehensive testing
"""

import asyncio
import random
from datetime import datetime, timedelta, date
from typing import List, Dict, Any
import asyncpg
import os
from dotenv import load_dotenv
from faker import Faker
import uuid

load_dotenv()

# PostgreSQL connection
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://adwise:secure_password@localhost:5432/adwise_analytics")
fake = Faker()

PLATFORMS = ["facebook", "instagram", "google_ads", "linkedin", "twitter", "tiktok", "snapchat"]
DEVICE_TYPES = ["desktop", "mobile", "tablet"]
COUNTRIES = ["US", "CA", "GB", "DE", "FR", "AU", "JP", "BR", "IN", "MX"]
AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
GENDERS = ["male", "female", "unknown"]

class PostgreSQLSeeder:
    def __init__(self):
        self.connection = None
    
    async def connect(self):
        """Establish database connection"""
        self.connection = await asyncpg.connect(POSTGRES_URL)
        print("✅ Connected to PostgreSQL")
    
    async def disconnect(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            print("✅ Disconnected from PostgreSQL")
    
    async def create_tables(self):
        """Create analytics tables with proper schema"""
        print("🔄 Creating analytics tables...")
        
        # Campaign Performance Table
        await self.connection.execute("""
            DROP TABLE IF EXISTS campaign_performance CASCADE;
            CREATE TABLE campaign_performance (
                id SERIAL PRIMARY KEY,
                campaign_id VARCHAR(24) NOT NULL,
                date DATE NOT NULL,
                platform VARCHAR(50) NOT NULL,
                device_type VARCHAR(20) NOT NULL,
                country VARCHAR(5) NOT NULL,
                age_group VARCHAR(10) NOT NULL,
                gender VARCHAR(10) NOT NULL,
                impressions BIGINT DEFAULT 0,
                clicks BIGINT DEFAULT 0,
                conversions BIGINT DEFAULT 0,
                spend DECIMAL(10,2) DEFAULT 0,
                revenue DECIMAL(10,2) DEFAULT 0,
                video_views BIGINT DEFAULT 0,
                video_completions BIGINT DEFAULT 0,
                link_clicks BIGINT DEFAULT 0,
                post_engagements BIGINT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(campaign_id, date, platform, device_type, country, age_group, gender)
            );
        """)
        
        # User Activity Table
        await self.connection.execute("""
            DROP TABLE IF EXISTS user_activity CASCADE;
            CREATE TABLE user_activity (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(24) NOT NULL,
                session_id VARCHAR(36) NOT NULL,
                action VARCHAR(100) NOT NULL,
                resource_type VARCHAR(50) NOT NULL,
                resource_id VARCHAR(24),
                metadata JSONB,
                ip_address INET,
                user_agent TEXT,
                country VARCHAR(5),
                city VARCHAR(100),
                duration_seconds INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Campaign Hourly Performance
        await self.connection.execute("""
            DROP TABLE IF EXISTS campaign_hourly_performance CASCADE;
            CREATE TABLE campaign_hourly_performance (
                id SERIAL PRIMARY KEY,
                campaign_id VARCHAR(24) NOT NULL,
                datetime TIMESTAMP NOT NULL,
                platform VARCHAR(50) NOT NULL,
                impressions INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0,
                spend DECIMAL(8,2) DEFAULT 0,
                ctr DECIMAL(5,2) DEFAULT 0,
                cpc DECIMAL(5,2) DEFAULT 0,
                cpm DECIMAL(5,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(campaign_id, datetime, platform)
            );
        """)
        
        # Audience Insights Table
        await self.connection.execute("""
            DROP TABLE IF EXISTS audience_insights CASCADE;
            CREATE TABLE audience_insights (
                id SERIAL PRIMARY KEY,
                campaign_id VARCHAR(24) NOT NULL,
                date DATE NOT NULL,
                platform VARCHAR(50) NOT NULL,
                audience_segment VARCHAR(100) NOT NULL,
                segment_size BIGINT DEFAULT 0,
                reach BIGINT DEFAULT 0,
                frequency DECIMAL(3,2) DEFAULT 0,
                engagement_rate DECIMAL(5,2) DEFAULT 0,
                conversion_rate DECIMAL(5,2) DEFAULT 0,
                avg_session_duration INTEGER DEFAULT 0,
                bounce_rate DECIMAL(5,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(campaign_id, date, platform, audience_segment)
            );
        """)
        
        # Attribution Data Table
        await self.connection.execute("""
            DROP TABLE IF EXISTS attribution_data CASCADE;
            CREATE TABLE attribution_data (
                id SERIAL PRIMARY KEY,
                conversion_id VARCHAR(36) NOT NULL,
                campaign_id VARCHAR(24) NOT NULL,
                user_id VARCHAR(36),
                touchpoint_sequence JSONB NOT NULL,
                conversion_value DECIMAL(10,2) DEFAULT 0,
                conversion_type VARCHAR(50) NOT NULL,
                attribution_model VARCHAR(50) NOT NULL,
                first_touch_campaign VARCHAR(24),
                last_touch_campaign VARCHAR(24),
                conversion_timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        print("✅ Analytics tables created")
    
    async def create_indexes(self):
        """Create performance indexes"""
        print("🔄 Creating performance indexes...")
        
        indexes = [
            "CREATE INDEX idx_campaign_performance_date ON campaign_performance(date);",
            "CREATE INDEX idx_campaign_performance_campaign ON campaign_performance(campaign_id);",
            "CREATE INDEX idx_campaign_performance_platform ON campaign_performance(platform);",
            "CREATE INDEX idx_campaign_performance_composite ON campaign_performance(campaign_id, date, platform);",
            
            "CREATE INDEX idx_user_activity_user ON user_activity(user_id);",
            "CREATE INDEX idx_user_activity_date ON user_activity(created_at);",
            "CREATE INDEX idx_user_activity_action ON user_activity(action);",
            "CREATE INDEX idx_user_activity_session ON user_activity(session_id);",
            
            "CREATE INDEX idx_campaign_hourly_datetime ON campaign_hourly_performance(datetime);",
            "CREATE INDEX idx_campaign_hourly_campaign ON campaign_hourly_performance(campaign_id);",
            
            "CREATE INDEX idx_audience_insights_date ON audience_insights(date);",
            "CREATE INDEX idx_audience_insights_campaign ON audience_insights(campaign_id);",
            
            "CREATE INDEX idx_attribution_conversion ON attribution_data(conversion_timestamp);",
            "CREATE INDEX idx_attribution_campaign ON attribution_data(campaign_id);",
        ]
        
        for index in indexes:
            await self.connection.execute(index)
        
        print("✅ Performance indexes created")
    
    async def seed_campaign_performance(self, campaign_count: int = 100000, days_back: int = 365):
        """Generate realistic campaign performance data"""
        print(f"🔄 Seeding campaign performance data for {campaign_count} campaigns over {days_back} days...")
        
        # Generate campaign IDs (simulating MongoDB ObjectIds)
        campaign_ids = [str(uuid.uuid4()).replace('-', '')[:24] for _ in range(campaign_count)]
        
        batch_size = 1000
        total_records = 0
        
        for batch_start in range(0, len(campaign_ids), batch_size):
            batch_campaigns = campaign_ids[batch_start:batch_start + batch_size]
            records = []
            
            for campaign_id in batch_campaigns:
                # Generate data for random date range within the period
                campaign_start = fake.date_between(start_date=f'-{days_back}d', end_date='-30d')
                campaign_end = campaign_start + timedelta(days=random.randint(7, 90))
                
                current_date = campaign_start
                while current_date <= min(campaign_end, date.today()):
                    # Generate multiple records per day (different segments)
                    for platform in random.sample(PLATFORMS, random.randint(1, 3)):
                        for device in DEVICE_TYPES:
                            for country in random.sample(COUNTRIES, random.randint(1, 3)):
                                for age_group in random.sample(AGE_GROUPS, random.randint(1, 3)):
                                    for gender in GENDERS:
                                        # Skip some combinations to make data more realistic
                                        if random.random() < 0.7:  # 70% chance to include this combination
                                            continue
                                        
                                        # Generate realistic performance metrics
                                        impressions = random.randint(100, 50000)
                                        ctr = random.uniform(0.5, 8.0)
                                        clicks = int(impressions * (ctr / 100))
                                        conversion_rate = random.uniform(1.0, 15.0)
                                        conversions = int(clicks * (conversion_rate / 100))
                                        cpc = random.uniform(0.50, 5.00)
                                        spend = clicks * cpc
                                        revenue = conversions * random.uniform(20, 200)
                                        
                                        # Video metrics (for video platforms)
                                        video_views = int(impressions * random.uniform(0.1, 0.6)) if platform in ['facebook', 'instagram', 'tiktok'] else 0
                                        video_completions = int(video_views * random.uniform(0.2, 0.8))
                                        
                                        record = (
                                            campaign_id, current_date, platform, device, country,
                                            age_group, gender, impressions, clicks, conversions,
                                            round(spend, 2), round(revenue, 2), video_views,
                                            video_completions, int(clicks * random.uniform(0.8, 1.0)),
                                            int(impressions * random.uniform(0.02, 0.1))
                                        )
                                        records.append(record)
                    
                    current_date += timedelta(days=1)
            
            # Insert batch
            if records:
                await self.connection.executemany("""
                    INSERT INTO campaign_performance 
                    (campaign_id, date, platform, device_type, country, age_group, gender,
                     impressions, clicks, conversions, spend, revenue, video_views,
                     video_completions, link_clicks, post_engagements)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                    ON CONFLICT (campaign_id, date, platform, device_type, country, age_group, gender) 
                    DO NOTHING
                """, records)
                
                total_records += len(records)
                print(f"  Inserted batch {batch_start//batch_size + 1}, Total records: {total_records}")
        
        print(f"✅ Created {total_records} campaign performance records")
    
    async def seed_user_activity(self, user_count: int = 1000, days_back: int = 90):
        """Generate realistic user activity data"""
        print(f"🔄 Seeding user activity data for {user_count} users over {days_back} days...")
        
        user_ids = [str(uuid.uuid4()).replace('-', '')[:24] for _ in range(user_count)]
        
        actions = [
            "login", "logout", "create_campaign", "edit_campaign", "delete_campaign",
            "view_dashboard", "generate_content", "export_report", "view_analytics",
            "invite_user", "change_settings", "upload_creative", "pause_campaign",
            "resume_campaign", "create_ad", "edit_ad", "view_performance"
        ]
        
        resource_types = ["campaign", "ad", "user", "report", "dashboard", "settings"]
        
        records = []
        for user_id in user_ids:
            # Generate sessions for this user
            session_count = random.randint(10, 100)
            
            for _ in range(session_count):
                session_id = str(uuid.uuid4())
                session_date = fake.date_time_between(start_date=f'-{days_back}d', end_date='now')
                
                # Generate activities within this session
                activity_count = random.randint(1, 20)
                session_duration = 0
                
                for i in range(activity_count):
                    action = random.choice(actions)
                    resource_type = random.choice(resource_types)
                    duration = random.randint(5, 300)  # 5 seconds to 5 minutes
                    session_duration += duration
                    
                    activity_time = session_date + timedelta(seconds=session_duration)
                    
                    record = (
                        user_id, session_id, action, resource_type,
                        str(uuid.uuid4()).replace('-', '')[:24],  # resource_id
                        f'{{"page": "{fake.uri_path()}", "referrer": "{fake.uri()}"}}',  # metadata
                        fake.ipv4(), fake.user_agent(),
                        random.choice(COUNTRIES), fake.city(),
                        duration, activity_time
                    )
                    records.append(record)
        
        # Insert in batches
        batch_size = 5000
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            await self.connection.executemany("""
                INSERT INTO user_activity 
                (user_id, session_id, action, resource_type, resource_id, metadata,
                 ip_address, user_agent, country, city, duration_seconds, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """, batch)
            
            print(f"  Inserted user activity batch {i//batch_size + 1}")
        
        print(f"✅ Created {len(records)} user activity records")
    
    async def seed_hourly_performance(self, campaign_count: int = 10000, days_back: int = 30):
        """Generate hourly performance data for recent campaigns"""
        print(f"🔄 Seeding hourly performance data...")
        
        campaign_ids = [str(uuid.uuid4()).replace('-', '')[:24] for _ in range(campaign_count)]
        
        records = []
        start_date = datetime.now() - timedelta(days=days_back)
        
        for campaign_id in campaign_ids[:1000]:  # Limit for performance
            current_datetime = start_date
            
            while current_datetime <= datetime.now():
                for platform in random.sample(PLATFORMS, random.randint(1, 2)):
                    # Generate hourly metrics
                    impressions = random.randint(10, 5000)
                    ctr = random.uniform(0.5, 8.0)
                    clicks = int(impressions * (ctr / 100))
                    conversions = int(clicks * random.uniform(0.01, 0.15))
                    cpc = random.uniform(0.50, 5.00)
                    spend = clicks * cpc
                    cpm = spend / (impressions / 1000) if impressions > 0 else 0
                    
                    record = (
                        campaign_id, current_datetime, platform,
                        impressions, clicks, conversions,
                        round(spend, 2), round(ctr, 2),
                        round(cpc, 2), round(cpm, 2)
                    )
                    records.append(record)
                
                current_datetime += timedelta(hours=1)
        
        # Insert in batches
        batch_size = 5000
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            await self.connection.executemany("""
                INSERT INTO campaign_hourly_performance 
                (campaign_id, datetime, platform, impressions, clicks, conversions,
                 spend, ctr, cpc, cpm)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (campaign_id, datetime, platform) DO NOTHING
            """, batch)
        
        print(f"✅ Created {len(records)} hourly performance records")
    
    async def seed_all(self):
        """Seed all analytics tables"""
        print("🚀 Starting PostgreSQL analytics seeding...")
        
        await self.create_tables()
        await self.create_indexes()
        
        # Seed with realistic volumes
        await self.seed_campaign_performance(campaign_count=50000, days_back=365)
        await self.seed_user_activity(user_count=5000, days_back=90)
        await self.seed_hourly_performance(campaign_count=10000, days_back=30)
        
        # Get final counts
        counts = {}
        tables = ['campaign_performance', 'user_activity', 'campaign_hourly_performance']
        
        for table in tables:
            count = await self.connection.fetchval(f"SELECT COUNT(*) FROM {table}")
            counts[table] = count
        
        print("🎉 PostgreSQL seeding completed!")
        print("📊 Final counts:")
        for table, count in counts.items():
            print(f"  {table}: {count:,}")

async def main():
    """Main seeding function"""
    seeder = PostgreSQLSeeder()
    await seeder.connect()
    
    try:
        await seeder.seed_all()
    finally:
        await seeder.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
