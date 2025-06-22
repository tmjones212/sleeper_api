-- Supabase Schema for Trade Ratings

-- Create trade_ratings table
CREATE TABLE trade_ratings (
    id SERIAL PRIMARY KEY,
    trade_id TEXT NOT NULL UNIQUE,
    trade_index INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Create ratings table with foreign key to trade_ratings
CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    trade_id TEXT NOT NULL,
    user_name TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    FOREIGN KEY (trade_id) REFERENCES trade_ratings(trade_id) ON DELETE CASCADE,
    UNIQUE(trade_id, user_name)
);

-- Create indexes for better query performance
CREATE INDEX idx_ratings_trade_id ON ratings(trade_id);
CREATE INDEX idx_ratings_user_name ON ratings(user_name);
CREATE INDEX idx_trade_ratings_trade_id ON trade_ratings(trade_id);

-- Enable Row Level Security (RLS)
ALTER TABLE trade_ratings ENABLE ROW LEVEL SECURITY;
ALTER TABLE ratings ENABLE ROW LEVEL SECURITY;

-- Create policies for anonymous access (since your app doesn't have auth)
CREATE POLICY "Allow anonymous read access to trade_ratings" ON trade_ratings
    FOR SELECT TO anon USING (true);

CREATE POLICY "Allow anonymous insert to trade_ratings" ON trade_ratings
    FOR INSERT TO anon WITH CHECK (true);

CREATE POLICY "Allow anonymous read access to ratings" ON ratings
    FOR SELECT TO anon USING (true);

CREATE POLICY "Allow anonymous insert to ratings" ON ratings
    FOR INSERT TO anon WITH CHECK (true);

CREATE POLICY "Allow anonymous update to ratings" ON ratings
    FOR UPDATE TO anon USING (true) WITH CHECK (true);

-- Create a view for aggregated ratings (optional but useful)
CREATE VIEW trade_rating_summary AS
SELECT 
    tr.trade_id,
    tr.trade_index,
    COUNT(r.id) as total_ratings,
    AVG(r.rating)::DECIMAL(3,2) as average_rating,
    JSON_AGG(
        JSON_BUILD_OBJECT(
            'user_name', r.user_name,
            'rating', r.rating,
            'timestamp', r.timestamp
        ) ORDER BY r.timestamp DESC
    ) as ratings_list
FROM trade_ratings tr
LEFT JOIN ratings r ON tr.trade_id = r.trade_id
GROUP BY tr.trade_id, tr.trade_index;

-- Grant access to the view
GRANT SELECT ON trade_rating_summary TO anon;