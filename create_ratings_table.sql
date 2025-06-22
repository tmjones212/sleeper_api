-- Create the missing ratings table
CREATE TABLE IF NOT EXISTS ratings (
    id SERIAL PRIMARY KEY,
    trade_id TEXT NOT NULL,
    user_name TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    FOREIGN KEY (trade_id) REFERENCES trade_ratings(trade_id) ON DELETE CASCADE,
    UNIQUE(trade_id, user_name)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_ratings_trade_id ON ratings(trade_id);
CREATE INDEX IF NOT EXISTS idx_ratings_user_name ON ratings(user_name);

-- Enable Row Level Security (RLS)
ALTER TABLE ratings ENABLE ROW LEVEL SECURITY;

-- Create policies for anonymous access
CREATE POLICY "Allow anonymous read access to ratings" ON ratings
    FOR SELECT TO anon USING (true);

CREATE POLICY "Allow anonymous insert to ratings" ON ratings
    FOR INSERT TO anon WITH CHECK (true);

CREATE POLICY "Allow anonymous update to ratings" ON ratings
    FOR UPDATE TO anon USING (true) WITH CHECK (true);

CREATE POLICY "Allow anonymous delete from ratings" ON ratings
    FOR DELETE TO anon USING (true);

-- Also ensure trade_ratings has all needed policies
CREATE POLICY IF NOT EXISTS "Allow anonymous update to trade_ratings" ON trade_ratings
    FOR UPDATE TO anon USING (true) WITH CHECK (true);