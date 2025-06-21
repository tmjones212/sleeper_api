/**
 * Firebase Module
 * Handles Firebase initialization and database operations
 */

// Firebase Configuration
const firebaseConfig = {
    apiKey: "AIzaSyCyPZgFFjuWcjop2MkhqUeE70iH9WBvsVQ",
    authDomain: "easypickens-95989.firebaseapp.com",
    projectId: "easypickens-95989",
    storageBucket: "easypickens-95989.firebasestorage.app",
    messagingSenderId: "732973559000",
    appId: "1:732973559000:web:6c1da5da08ce39ed3d3bad"
};

// Initialize Firebase (only if config is provided)
let db = null;

export function initializeFirebase() {
    console.log('🔍 Initializing Firebase with config:', firebaseConfig);
    if (firebaseConfig.apiKey) {
        try {
            firebase.initializeApp(firebaseConfig);
            db = firebase.firestore();
            const statusEl = document.getElementById('firebase-status');
            if (statusEl) statusEl.textContent = '🔗 Real-time sync enabled';
            console.log('✅ Firebase initialized successfully, db =', db);
        } catch (error) {
            console.error('❌ Firebase initialization failed:', error);
            const statusEl = document.getElementById('firebase-status');
            if (statusEl) statusEl.textContent = '❌ Firebase connection failed';
        }
    } else {
        const statusEl = document.getElementById('firebase-status');
        if (statusEl) statusEl.textContent = '💾 Local storage only';
    }
}

export function saveTradeGradeToFirebase(tradeIndex, gradeValue, userName) {
    console.log('🔍 saveTradeGradeToFirebase called with:', { tradeIndex, gradeValue, userName, dbExists: !!db });
    if (!db) {
        console.log('❌ Firebase not configured, using localStorage only');
        return;
    }

    try {
        // Get trade info
        const tradeItem = document.querySelector(`#trade-grade-${tradeIndex}`)?.closest('.trade-item');
        const dateElement = tradeItem?.querySelector('.trade-date');
        const summaryElement = tradeItem?.querySelector('.trade-summary strong');
        
        const tradeId = `${dateElement?.textContent.trim()}_${summaryElement?.textContent.trim()}`.replace(/[^a-zA-Z0-9]/g, '_');
        
        console.log(`💾 Saving to Firebase: Trade ${tradeIndex}, User: ${userName}, Rating: ${gradeValue}`);
        
        // Create user rating document
        const userRatingRef = db.collection('trade_ratings').doc(tradeId).collection('user_ratings').doc(userName);
        
        userRatingRef.set({
            rating: parseInt(gradeValue),
            timestamp: firebase.firestore.FieldValue.serverTimestamp(),
            userName: userName
        }).then(() => {
            console.log('✅ User rating saved to Firebase');
            
            // Update the aggregated ratings
            return updateAggregatedRating(tradeId);
        }).then(() => {
            console.log('✅ Aggregated rating updated');
            
            // Reload average ratings to update displays
            loadAverageRatings();
        }).catch((error) => {
            console.error('❌ Error saving to Firebase:', error);
        });
    } catch (error) {
        console.error('❌ Error in saveTradeGradeToFirebase:', error);
    }
}

export function loadAverageRatings() {
    console.log('📊 Loading average ratings from Firebase, db =', db);
    if (!db) {
        console.log('❌ Firebase not configured');
        return;
    }

    try {
        db.collection('trade_ratings').get().then((querySnapshot) => {
            console.log(`📊 Found ${querySnapshot.size} trades with ratings`);
            querySnapshot.forEach((doc) => {
                const data = doc.data();
                if (data.averageRating !== undefined && data.numRatings > 0) {
                    // Find the corresponding trade grade slider by trade ID pattern
                    const tradeElements = document.querySelectorAll('.trade-item');
                    tradeElements.forEach((tradeEl, index) => {
                        const dateEl = tradeEl.querySelector('.trade-date');
                        const summaryEl = tradeEl.querySelector('.trade-summary strong');
                        const tradeId = `${dateEl?.textContent.trim()}_${summaryEl?.textContent.trim()}`.replace(/[^a-zA-Z0-9]/g, '_');
                        
                        if (tradeId === doc.id) {
                            // Use display-only function to avoid infinite loop
                            updateTradeGradeDisplay(Object.keys(document.querySelectorAll('.trade-grade-slider'))[index]?.replace('trade-grade-', '') || index, data.averageRating, data.numRatings);
                        }
                    });
                }
            });
        }).catch((error) => {
            console.error('❌ Error loading average ratings:', error);
        });
    } catch (error) {
        console.error('❌ Error in loadAverageRatings:', error);
    }
}

export function updateTradeGradeDisplay(tradeIndex, averageValue, numRatings) {
    const slider = document.getElementById(`trade-grade-${tradeIndex}`);
    const resultDiv = document.getElementById(`trade-result-${tradeIndex}`);
    
    if (!slider || !resultDiv) return;
    
    // Get teams from the trade item
    const tradeItem = slider.closest('.trade-item');
    const teams = tradeItem.querySelectorAll('.team-side h4');
    const team1 = teams[0]?.textContent || 'Team 1';
    const team2 = teams[1]?.textContent || 'Team 2';
    
    // Determine result based on average value
    let resultText = '';
    let resultColor = '';
    
    if (averageValue < 40) {
        resultText = `League says: ${team1} won`;
        resultColor = '#66ff66';
    } else if (averageValue > 60) {
        resultText = `League says: ${team2} won`;
        resultColor = '#ff6666';
    } else {
        resultText = 'League says: Even trade';
        resultColor = '#ffcc66';
    }
    
    // Add number of ratings if available
    if (numRatings !== undefined) {
        resultText += ` (${numRatings} ${numRatings === 1 ? 'vote' : 'votes'})`;
    }
    
    resultDiv.innerHTML = `<span style="color: ${resultColor};">${resultText}</span>`;
}

async function updateAggregatedRating(tradeId) {
    if (!db) return;
    
    try {
        // Get all user ratings for this trade
        const userRatingsSnapshot = await db.collection('trade_ratings').doc(tradeId).collection('user_ratings').get();
        
        if (userRatingsSnapshot.empty) {
            console.log('No ratings found for trade:', tradeId);
            return;
        }
        
        let totalRating = 0;
        let numRatings = 0;
        
        userRatingsSnapshot.forEach((doc) => {
            const data = doc.data();
            if (data.rating !== undefined) {
                totalRating += data.rating;
                numRatings++;
            }
        });
        
        const averageRating = numRatings > 0 ? totalRating / numRatings : 50;
        
        // Update the main trade rating document
        await db.collection('trade_ratings').doc(tradeId).set({
            averageRating: averageRating,
            numRatings: numRatings,
            lastUpdated: firebase.firestore.FieldValue.serverTimestamp()
        }, { merge: true });
        
        console.log(`✅ Updated aggregated rating for ${tradeId}: ${averageRating} (${numRatings} ratings)`);
    } catch (error) {
        console.error('❌ Error updating aggregated rating:', error);
    }
}

export function manualRefreshRatings(silent = false) {
    if (!silent) {
        console.log('🔄 Manually refreshing ratings from Firebase...');
    }
    
    if (!db) {
        if (!silent) {
            alert('Firebase is not connected. Cannot refresh ratings.');
        }
        return;
    }
    
    // Load average ratings from Firebase
    loadAverageRatings();
    
    // Also update the trading summary
    if (typeof updateSummaryWithAverages === 'function') {
        // Get all ratings for summary calculation
        db.collection('trade_ratings').get().then((querySnapshot) => {
            const allRatings = {};
            querySnapshot.forEach((doc) => {
                const data = doc.data();
                if (data.averageRating !== undefined && data.numRatings > 0) {
                    allRatings[doc.id] = {
                        average: data.averageRating,
                        count: data.numRatings
                    };
                }
            });
            updateSummaryWithAverages(allRatings);
        }).catch((error) => {
            console.error('❌ Error fetching ratings for summary:', error);
        });
    }
    
    if (!silent) {
        // Visual feedback
        const statusEl = document.getElementById('firebase-status');
        if (statusEl) {
            const originalText = statusEl.textContent;
            statusEl.textContent = '🔄 Refreshing...';
            setTimeout(() => {
                statusEl.textContent = originalText;
            }, 1000);
        }
    }
}

// Export database reference
export function getDb() {
    return db;
}