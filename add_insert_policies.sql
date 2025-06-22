-- Add INSERT policies for both tables
CREATE POLICY "Allow anonymous insert to trade_ratings" ON trade_ratings
    FOR INSERT TO anon WITH CHECK (true);

CREATE POLICY "Allow anonymous insert to ratings" ON ratings
    FOR INSERT TO anon WITH CHECK (true);

-- To see all existing policies for debugging
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies 
WHERE tablename IN ('trade_ratings', 'ratings')
ORDER BY tablename, cmd;