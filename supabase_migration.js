// Supabase Migration Code
// Replace the Firebase section in your index.html with this code

// 1. Replace Firebase SDK scripts with Supabase:
// <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>

// 2. Replace Firebase config and initialization with:
const SUPABASE_URL = 'YOUR_SUPABASE_PROJECT_URL'; // e.g., https://xxxxx.supabase.co
const SUPABASE_ANON_KEY = 'YOUR_SUPABASE_ANON_KEY'; // Your public anon key

// Initialize Supabase
let supabase = null;
console.log('🔍 Initializing Supabase...');
if (SUPABASE_URL && SUPABASE_ANON_KEY && SUPABASE_URL !== 'YOUR_SUPABASE_PROJECT_URL') {
    try {
        supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        const statusEl = document.getElementById('firebase-status');
        if (statusEl) statusEl.textContent = '🔗 Real-time sync enabled';
        console.log('✅ Supabase initialized successfully');
    } catch (error) {
        console.error('❌ Supabase initialization failed:', error);
        const statusEl = document.getElementById('firebase-status');
        if (statusEl) statusEl.textContent = '❌ Database connection failed';
    }
} else {
    const statusEl = document.getElementById('firebase-status');
    if (statusEl) statusEl.textContent = '💾 Local storage only';
}

// 3. Replace the saveRating function:
async function saveRating(tradeId, userName, rating, tradeIndex) {
    if (!supabase) {
        console.log('No database connection, using local storage only');
        return;
    }

    try {
        // First, ensure the trade exists in trade_ratings table
        const { data: existingTrade, error: checkError } = await supabase
            .from('trade_ratings')
            .select('trade_id')
            .eq('trade_id', tradeId)
            .single();

        if (!existingTrade && !checkError) {
            // Insert the trade if it doesn't exist
            const { error: insertTradeError } = await supabase
                .from('trade_ratings')
                .insert({ 
                    trade_id: tradeId,
                    trade_index: tradeIndex
                });
            
            if (insertTradeError && insertTradeError.code !== '23505') { // Ignore duplicate key errors
                console.error('Error inserting trade:', insertTradeError);
            }
        }

        // Now save/update the rating
        const { data, error } = await supabase
            .from('ratings')
            .upsert({
                trade_id: tradeId,
                user_name: userName,
                rating: rating,
                timestamp: new Date().toISOString()
            }, {
                onConflict: 'trade_id,user_name'
            });

        if (error) {
            console.error('Error saving rating:', error);
        } else {
            console.log('Rating saved successfully');
        }
    } catch (error) {
        console.error('Error in saveRating:', error);
    }
}

// 4. Replace the loadRatings function:
async function loadRatings(tradeId) {
    if (!supabase) {
        return { ratings: [], average: 0 };
    }

    try {
        const { data, error } = await supabase
            .from('ratings')
            .select('*')
            .eq('trade_id', tradeId);

        if (error) {
            console.error('Error loading ratings:', error);
            return { ratings: [], average: 0 };
        }

        const ratings = data || [];
        const average = ratings.length > 0 
            ? ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length 
            : 0;

        return { ratings, average };
    } catch (error) {
        console.error('Error in loadRatings:', error);
        return { ratings: [], average: 0 };
    }
}

// 5. Replace the real-time subscription setup:
function setupRealtimeSubscription(tradeId, callback) {
    if (!supabase) return null;

    const subscription = supabase
        .channel(`ratings:${tradeId}`)
        .on(
            'postgres_changes',
            {
                event: '*',
                schema: 'public',
                table: 'ratings',
                filter: `trade_id=eq.${tradeId}`
            },
            (payload) => {
                console.log('Real-time update:', payload);
                callback(payload);
            }
        )
        .subscribe();

    return subscription;
}

// 6. Replace the getAllRatings function (for consensus calculations):
async function getAllRatings() {
    if (!supabase) {
        return [];
    }

    try {
        const { data, error } = await supabase
            .from('trade_rating_summary')
            .select('*');

        if (error) {
            console.error('Error loading all ratings:', error);
            return [];
        }

        return data || [];
    } catch (error) {
        console.error('Error in getAllRatings:', error);
        return [];
    }
}

// 7. Update the grade button click handler:
// Find and replace the existing Firebase code with Supabase calls
// The structure remains the same, just use the new functions above