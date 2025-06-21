/**
 * Draft Data Module
 * Contains draft data for multiple years
 * NOTE: This is a placeholder with the structure. The full data should be loaded from a JSON file.
 */

export const draftData = {
    "available_years": [2025, 2024, 2023, 2022],
    "current_year": "2025",
    "drafts_by_year": {
        "2022": [
            {
                "draft_id": "839251412071321600",
                "picks": [
                    // This would contain the full array of picks
                    // In production, load this from a JSON file
                ]
            }
        ],
        "2023": [
            // Draft data for 2023
        ],
        "2024": [
            // Draft data for 2024
        ],
        "2025": [
            // Draft data for 2025
        ]
    }
};

// In production, you would load this data from an API or JSON file:
// export async function loadDraftData() {
//     const response = await fetch('/data/draft_data.json');
//     return await response.json();
// }