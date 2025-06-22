-- Fix missing policies for Supabase

-- Add UPDATE policy for trade_ratings table
CREATE POLICY "Allow anonymous update to trade_ratings" ON trade_ratings
    FOR UPDATE TO anon USING (true) WITH CHECK (true);

-- Also ensure we have DELETE policies if needed
CREATE POLICY "Allow anonymous delete from ratings" ON ratings
    FOR DELETE TO anon USING (true);

CREATE POLICY "Allow anonymous delete from trade_ratings" ON trade_ratings  
    FOR DELETE TO anon USING (true);

-- Alternative: If policies are still causing issues, you can temporarily disable RLS
-- (not recommended for production but useful for debugging)
-- ALTER TABLE trade_ratings DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE ratings DISABLE ROW LEVEL SECURITY;