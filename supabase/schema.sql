-- Sermonopedia – Supabase SQL Schema
-- Run this in the Supabase SQL Editor to set up the database

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Profiles table (synced with Supabase Auth)
CREATE TABLE IF NOT EXISTS profiles (
    id SERIAL PRIMARY KEY,
    auth_uid VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(320) NOT NULL,
    full_name VARCHAR(255) DEFAULT '',
    avatar_url TEXT DEFAULT '',
    role VARCHAR(50) DEFAULT 'viewer',
    denomination VARCHAR(100) DEFAULT '',
    bio TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_profiles_auth_uid ON profiles(auth_uid);

-- Sermons table
CREATE TABLE IF NOT EXISTS sermons (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    preacher VARCHAR(255) DEFAULT '',
    date_preached VARCHAR(20) DEFAULT '',
    denomination VARCHAR(100) DEFAULT '',
    source_url TEXT DEFAULT '',
    audio_url TEXT DEFAULT '',
    transcript TEXT DEFAULT '',
    summary TEXT DEFAULT '',
    outline TEXT DEFAULT '',
    themes TEXT DEFAULT '',
    status VARCHAR(50) DEFAULT 'draft',
    sermonaudio_id VARCHAR(100) DEFAULT '',
    embedding vector(1536),
    author_id INTEGER REFERENCES profiles(id),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_sermons_title ON sermons(title);
CREATE INDEX idx_sermons_sermonaudio_id ON sermons(sermonaudio_id);
CREATE INDEX idx_sermons_embedding ON sermons USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- User sermons (personal workspace)
CREATE TABLE IF NOT EXISTS user_sermons (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES profiles(id),
    title VARCHAR(500) NOT NULL,
    content TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Scriptures table
CREATE TABLE IF NOT EXISTS scriptures (
    id SERIAL PRIMARY KEY,
    book VARCHAR(50) NOT NULL,
    chapter INTEGER NOT NULL,
    verse_start INTEGER NOT NULL,
    verse_end INTEGER,
    text TEXT DEFAULT '',
    translation VARCHAR(20) DEFAULT 'KJV',
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_scriptures_book ON scriptures(book);

-- Many-to-many: sermons <-> scriptures
CREATE TABLE IF NOT EXISTS sermon_scriptures (
    id SERIAL PRIMARY KEY,
    sermon_id INTEGER NOT NULL REFERENCES sermons(id) ON DELETE CASCADE,
    scripture_id INTEGER NOT NULL REFERENCES scriptures(id) ON DELETE CASCADE,
    context TEXT DEFAULT ''
);

-- Sermon links (semantic connections)
CREATE TABLE IF NOT EXISTS sermon_links (
    id SERIAL PRIMARY KEY,
    source_sermon_id INTEGER NOT NULL REFERENCES sermons(id) ON DELETE CASCADE,
    target_sermon_id INTEGER NOT NULL REFERENCES sermons(id) ON DELETE CASCADE,
    link_type VARCHAR(50) NOT NULL,
    score FLOAT DEFAULT 0.0,
    reason TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Courses
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT DEFAULT '',
    author_id INTEGER REFERENCES profiles(id),
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Course modules
CREATE TABLE IF NOT EXISTS course_modules (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content TEXT DEFAULT '',
    sermon_id INTEGER REFERENCES sermons(id),
    "order" INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Row Level Security (RLS)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE sermons ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sermons ENABLE ROW LEVEL SECURITY;

-- Profiles: users can read all, but only update their own
CREATE POLICY "Profiles are viewable by everyone" ON profiles FOR SELECT USING (true);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid()::text = auth_uid);

-- Sermons: published sermons are public, drafts only visible to author
CREATE POLICY "Published sermons are viewable by everyone" ON sermons FOR SELECT USING (status = 'published' OR author_id IN (SELECT id FROM profiles WHERE auth_uid = auth.uid()::text));
CREATE POLICY "Users can manage own sermons" ON sermons FOR ALL USING (author_id IN (SELECT id FROM profiles WHERE auth_uid = auth.uid()::text));

-- User sermons: only the owner
CREATE POLICY "Users can manage own user_sermons" ON user_sermons FOR ALL USING (profile_id IN (SELECT id FROM profiles WHERE auth_uid = auth.uid()::text));

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables
CREATE TRIGGER set_profiles_updated_at BEFORE UPDATE ON profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_sermons_updated_at BEFORE UPDATE ON sermons FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_user_sermons_updated_at BEFORE UPDATE ON user_sermons FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_scriptures_updated_at BEFORE UPDATE ON scriptures FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_sermon_links_updated_at BEFORE UPDATE ON sermon_links FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_courses_updated_at BEFORE UPDATE ON courses FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_course_modules_updated_at BEFORE UPDATE ON course_modules FOR EACH ROW EXECUTE FUNCTION update_updated_at();
