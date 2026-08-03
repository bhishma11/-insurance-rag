// src/utils/formatResponse.ts

export const formatResponse = (text: string): string => {
  let formatted = text;

  // === STEP 1: Add a main title if none exists ===
  if (!formatted.includes('# ')) {
    // Try to find a title from the first sentence
    const firstSentence = formatted.match(/^[^.!?]+[.!?]/);
    if (firstSentence) {
      const title = firstSentence[0].replace(/^[^a-zA-Z]*/, '').trim();
      formatted = formatted.replace(firstSentence[0], `# ${title}\n\n`);
    } else {
      formatted = `# Insurance Claim Guidance\n\n${formatted}`;
    }
  }

  // === STEP 2: Convert numbered sections to headings ===
  // "1. Relevant Policies" -> "## 1. Relevant Policies"
  formatted = formatted.replace(/^(\d+\.\s*[A-Z][^\n]+)/gm, '\n\n## $1\n\n');

  // === STEP 3: Convert policy names to sub-headings ===
  // "Auto Policy" at start of line -> "### Auto Policy"
  formatted = formatted.replace(/^(Auto Policy|Renters Policy|Health Policy|Renter's Policy)(\s*\([^)]+\))?/gm, '\n\n### $1$2\n\n');

  // === STEP 4: Convert common section names ===
  const sectionNames = [
    'Coverage Summary',
    'Next Steps',
    'Important Warnings',
    'Final Answer',
    'Recommended Next Steps',
    'Summary of Your Situation',
    'What to Do Next',
    'Key Findings'
  ];
  for (const name of sectionNames) {
    const regex = new RegExp(`^${name}`, 'gm');
    formatted = formatted.replace(regex, `\n\n## ${name}\n\n`);
  }

  // === STEP 5: Convert Key Finding, Insurer, Vehicle, Policy Number to bold ===
  const boldLabels = [
    'Key Finding',
    'Important Warning',
    'Insurer',
    'Vehicle',
    'Policy Number',
    'Coverage Period',
    'Covers',
    'Excludes',
    'Deductible',
    'Final Answer',
    'Recommendation',
    'Notes'
  ];
  for (const label of boldLabels) {
    const regex = new RegExp(`(${label}):`, 'g');
    formatted = formatted.replace(regex, '**$1:**');
  }

  // === STEP 6: Fix tables - add the separator line ===
  const lines = formatted.split('\n');
  let inTable = false;
  let fixedLines = [];
  let tableContent = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();
    
    // Check if this is a table row (starts and ends with |)
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      if (!inTable) {
        // Start of a new table
        inTable = true;
        tableContent = [];
      }
      tableContent.push(trimmed);
    } else {
      if (inTable) {
        // End of table - add separator if needed
        if (tableContent.length > 0) {
          // Check if separator already exists
          const hasSeparator = tableContent.some(row => row.includes('---'));
          if (!hasSeparator && tableContent.length > 0) {
            // Add separator after first row
            const parts = tableContent[0].split('|').filter(p => p.trim() !== '');
            const separator = parts.map(() => '---').join('|');
            fixedLines.push(tableContent[0]);
            fixedLines.push(`|${separator}|`);
            for (let j = 1; j < tableContent.length; j++) {
              fixedLines.push(tableContent[j]);
            }
          } else {
            fixedLines.push(...tableContent);
          }
        }
        inTable = false;
        tableContent = [];
      }
      fixedLines.push(line);
    }
  }

  // Handle any remaining table
  if (inTable && tableContent.length > 0) {
    const hasSeparator = tableContent.some(row => row.includes('---'));
    if (!hasSeparator && tableContent.length > 0) {
      const parts = tableContent[0].split('|').filter(p => p.trim() !== '');
      const separator = parts.map(() => '---').join('|');
      fixedLines.push(tableContent[0]);
      fixedLines.push(`|${separator}|`);
      for (let j = 1; j < tableContent.length; j++) {
        fixedLines.push(tableContent[j]);
      }
    } else {
      fixedLines.push(...tableContent);
    }
  }

  formatted = fixedLines.join('\n');

  // === STEP 7: Add horizontal rules between major sections ===
  formatted = formatted.replace(/\n## /g, '\n\n---\n\n## ');
  formatted = formatted.replace(/\n### /g, '\n\n### ');

  // === STEP 8: Fix double spacing ===
  formatted = formatted.replace(/\n{4,}/g, '\n\n');
  formatted = formatted.replace(/\n{3,}/g, '\n\n');

  // === STEP 9: Ensure blank lines after headings ===
  formatted = formatted.replace(/(#+ [^\n]+)([^\n#])/g, '$1\n\n$2');
  formatted = formatted.replace(/\*\*([^\n]+)\*\*([^\n])/g, '**$1**\n\n$2');

  // === STEP 10: Clean up ===
  formatted = formatted.replace(/[ \t]+\n/g, '\n');
  formatted = formatted.replace(/^\s+/, '');
  formatted = formatted.replace(/\s+$/, '');

  return formatted;
};