-- Media Feed Database Schema
-- Run this in Supabase SQL Editor

-- Main media posts table
CREATE TABLE media_posts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Platform info
  source text NOT NULL, -- 'youtube', 'twitter', 'tiktok', 'podcast', 'instagram'
  platform_id text, -- original post ID from platform (for deduplication)
  url text NOT NULL UNIQUE,
  
  -- Content metadata
  title text,
  description text,
  thumbnail_url text,
  duration_seconds integer, -- for videos/audio
  
  -- Author info
  author_name text,
  author_handle text,
  author_avatar_url text,
  author_verified boolean DEFAULT false,
  
  -- Timing
  published_at timestamptz,
  scraped_at timestamptz DEFAULT now(),
  
  -- Engagement metrics (scraped)
  view_count integer DEFAULT 0,
  like_count integer DEFAULT 0,
  comment_count integer DEFAULT 0,
  share_count integer DEFAULT 0,
  
  -- Our scoring system
  relevance_score decimal DEFAULT 0,
  quality_score decimal DEFAULT 0, -- based on engagement ratio
  
  -- Content classification
  tags text[] DEFAULT '{}', -- ['knockout', 'ufc', 'interview']
  content_type text, -- 'highlight', 'interview', 'news', 'analysis', 'meme'
  fighters_mentioned text[] DEFAULT '{}', -- ['Jon Jones', 'Daniel Cormier']
  events_mentioned text[] DEFAULT '{}', -- ['UFC 309', 'UFC 310']
  
  -- Moderation
  is_approved boolean DEFAULT true,
  is_flagged boolean DEFAULT false,
  flag_reason text,
  
  -- Timestamps
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Indexes for performance
CREATE INDEX idx_media_posts_relevance ON media_posts(relevance_score DESC, published_at DESC);
CREATE INDEX idx_media_posts_source ON media_posts(source, published_at DESC);
CREATE INDEX idx_media_posts_published ON media_posts(published_at DESC);
CREATE INDEX idx_media_posts_platform_id ON media_posts(source, platform_id);
CREATE INDEX idx_media_posts_fighters ON media_posts USING GIN(fighters_mentioned);
CREATE INDEX idx_media_posts_tags ON media_posts USING GIN(tags);

-- Source configuration table (for managing our scraping targets)
CREATE TABLE media_sources (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Source identification
  platform text NOT NULL, -- 'youtube', 'twitter', 'tiktok'
  source_type text NOT NULL, -- 'channel', 'user', 'hashtag', 'search'
  identifier text NOT NULL, -- channel ID, username, hashtag, search term
  display_name text,
  
  -- Scraping config
  is_active boolean DEFAULT true,
  scrape_frequency_hours integer DEFAULT 6, -- how often to check
  max_posts_per_scrape integer DEFAULT 20,
  
  -- Quality filters
  min_engagement integer DEFAULT 0, -- minimum likes/views to include
  keywords_required text[] DEFAULT '{}', -- must contain these terms
  keywords_excluded text[] DEFAULT '{}', -- must NOT contain these
  
  -- Metadata
  last_scraped_at timestamptz,
  total_posts_found integer DEFAULT 0,
  
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  
  UNIQUE(platform, source_type, identifier)
);

-- Insert some initial high-quality sources
INSERT INTO media_sources (platform, source_type, identifier, display_name, scrape_frequency_hours) VALUES
('youtube', 'channel', 'UC2jmxZ3jbIpuHyajXzEqHiQ', 'UFC Official', 2),
('youtube', 'search', 'UFC highlights', 'UFC Highlights Search', 4),
('twitter', 'user', 'ufc', 'UFC Official Twitter', 1),
('twitter', 'user', 'danawhite', 'Dana White', 2),
('tiktok', 'hashtag', 'ufc', 'UFC TikTok', 6);

-- Create users table if it doesn't exist (basic structure)
CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  auth0_sub text UNIQUE,
  email text,
  username text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- User engagement tracking (for our own users)
CREATE TABLE media_post_interactions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  media_post_id uuid REFERENCES media_posts(id) ON DELETE CASCADE,
  
  interaction_type text NOT NULL, -- 'view', 'like', 'share', 'save'
  created_at timestamptz DEFAULT now(),
  
  UNIQUE(user_id, media_post_id, interaction_type)
);

CREATE INDEX idx_interactions_user ON media_post_interactions(user_id, created_at DESC);
CREATE INDEX idx_interactions_post ON media_post_interactions(media_post_id, interaction_type);

-- Comments on media posts (our own comment system)
CREATE TABLE media_post_comments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  media_post_id uuid REFERENCES media_posts(id) ON DELETE CASCADE,
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  
  content text NOT NULL,
  parent_comment_id uuid REFERENCES media_post_comments(id) ON DELETE CASCADE,
  
  like_count integer DEFAULT 0,
  is_pinned boolean DEFAULT false,
  is_deleted boolean DEFAULT false,
  
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE INDEX idx_comments_post ON media_post_comments(media_post_id, created_at DESC);
CREATE INDEX idx_comments_user ON media_post_comments(user_id, created_at DESC);

-- Enable Row Level Security
ALTER TABLE media_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE media_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE media_post_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE media_post_comments ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- Media posts: everyone can read, only service role can write
CREATE POLICY "Anyone can view media posts" ON media_posts
  FOR SELECT USING (is_approved = true);

CREATE POLICY "Service role can manage media posts" ON media_posts
  FOR ALL USING (auth.role() = 'service_role');

-- Media sources: only service role can manage
CREATE POLICY "Service role can manage sources" ON media_sources
  FOR ALL USING (auth.role() = 'service_role');

-- Interactions: users can manage their own
CREATE POLICY "Users can manage their interactions" ON media_post_interactions
  FOR ALL USING (auth.uid() = user_id);

-- Comments: users can read all, manage their own
CREATE POLICY "Anyone can view comments" ON media_post_comments
  FOR SELECT USING (is_deleted = false);

CREATE POLICY "Users can manage their comments" ON media_post_comments
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their comments" ON media_post_comments
  FOR UPDATE USING (auth.uid() = user_id);