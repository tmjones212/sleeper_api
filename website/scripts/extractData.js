/**
 * Script to extract data from index.html
 * This extracts large data structures and saves them as JSON files
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Read the index.html file
const indexPath = path.join(__dirname, '../../index.html');
const htmlContent = fs.readFileSync(indexPath, 'utf-8');

// Extract data between script tags
const scriptRegex = /<script[^>]*>([\s\S]*?)<\/script>/g;
let match;
const extractedData = {};

while ((match = scriptRegex.exec(htmlContent)) !== null) {
    const scriptContent = match[1];
    
    // Look for const declarations of large data structures
    const dataPatterns = [
        { name: 'networkData', regex: /const networkData = (\{[\s\S]*?\});(?=\s*const|$)/m },
        { name: 'timelineData', regex: /const timelineData = (\{[\s\S]*?\});(?=\s*const|$)/m },
        { name: 'draftData', regex: /const draftData = (\{[\s\S]*?\});(?=\s*const|$)/m },
        { name: 'matchupBreakdowns', regex: /const matchupBreakdowns = (\{[\s\S]*?\});(?=\s*const|$)/m }
    ];
    
    dataPatterns.forEach(pattern => {
        const dataMatch = pattern.regex.exec(scriptContent);
        if (dataMatch) {
            try {
                // Try to parse the JSON-like JavaScript object
                // Note: This is a simplified approach and might need adjustment for complex objects
                const jsonString = dataMatch[1]
                    .replace(/(\w+):/g, '"$1":') // Quote keys
                    .replace(/'/g, '"') // Replace single quotes with double
                    .replace(/,\s*}/g, '}') // Remove trailing commas
                    .replace(/,\s*]/g, ']'); // Remove trailing commas in arrays
                
                extractedData[pattern.name] = JSON.parse(jsonString);
                console.log(`✅ Extracted ${pattern.name}`);
            } catch (e) {
                console.error(`❌ Failed to extract ${pattern.name}:`, e.message);
            }
        }
    });
}

// Save extracted data
const outputDir = path.join(__dirname, '../src/data');
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

Object.entries(extractedData).forEach(([name, data]) => {
    const outputPath = path.join(outputDir, `${name}.json`);
    fs.writeFileSync(outputPath, JSON.stringify(data, null, 2));
    console.log(`💾 Saved ${name} to ${outputPath}`);
});

console.log('✨ Data extraction complete!');