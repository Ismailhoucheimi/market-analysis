// Global variables
let currentData = null;

// Initialize the report
function initializeReport(data) {
    console.log('Initializing report with data:', data);
    currentData = JSON.parse(JSON.stringify(data)); // Deep copy
    
    // Populate category filter options
    populateCategoryFilter();
    
    // Initialize posts view
    renderCategories(currentData.categories);
    
    // Setup event listeners
    setupEventListeners();
    
    // Populate comprehensive report if it exists
    if (data.comprehensive_report) {
        populateComprehensiveReport();
    }
    
    console.log('Report initialized successfully');
}

// Tab switching functionality
function switchTab(tabId, buttonElement) {
    // Hide all tab content
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.add('hidden');
    });
    
    // Remove active classes from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.classList.remove('text-primary-500', 'border-primary-500');
        btn.classList.add('text-gray-600', 'border-transparent');
    });
    
    // Show selected tab content
    const targetTab = document.getElementById(tabId);
    if (targetTab) {
        targetTab.classList.remove('hidden');
    }
    
    // Add active class to clicked button
    if (buttonElement) {
        buttonElement.classList.remove('text-gray-600', 'border-transparent');
        buttonElement.classList.add('text-primary-500', 'border-primary-500');
    }
    
    console.log('Switched to tab:', tabId);
}

// Populate category filter dropdown
function populateCategoryFilter() {
    const categoryFilter = document.getElementById('category-filter');
    if (!categoryFilter || !currentData) return;
    
    // Clear existing options except "All Categories"
    categoryFilter.innerHTML = '<option value="">All Categories</option>';
    
    // Add category options
    Object.keys(currentData.categories).forEach(categoryKey => {
        const category = currentData.categories[categoryKey];
        const option = document.createElement('option');
        option.value = categoryKey;
        option.textContent = `${category.name} (${category.count})`;
        categoryFilter.appendChild(option);
    });
}

// Setup event listeners
function setupEventListeners() {
    const categoryFilter = document.getElementById('category-filter');
    const sortFilter = document.getElementById('sort-filter');
    const searchFilter = document.getElementById('search-filter');
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', applyFilters);
    }
    
    if (sortFilter) {
        sortFilter.addEventListener('change', applyFilters);
    }
    
    if (searchFilter) {
        searchFilter.addEventListener('input', debounce(applyFilters, 300));
    }
}

// Debounce function for search input
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Apply filters and sorting
function applyFilters() {
    if (!currentData) return;
    
    const categoryFilter = document.getElementById('category-filter').value;
    const sortFilter = document.getElementById('sort-filter').value;
    const searchFilter = document.getElementById('search-filter').value.toLowerCase();
    
    console.log('Applying filters:', { categoryFilter, sortFilter, searchFilter });
    
    // Start with original data
    let filteredData = JSON.parse(JSON.stringify(currentData.categories));
    
    // Apply category filter
    if (categoryFilter) {
        const selectedCategory = {};
        selectedCategory[categoryFilter] = filteredData[categoryFilter];
        filteredData = selectedCategory;
    }
    
    // Apply search filter and sorting
    Object.keys(filteredData).forEach(categoryKey => {
        let posts = filteredData[categoryKey].posts;
        
        // Search filter
        if (searchFilter) {
            posts = posts.filter(post => 
                post.title.toLowerCase().includes(searchFilter) ||
                (post.selftext && post.selftext.toLowerCase().includes(searchFilter))
            );
        }
        
        // Sorting
        posts.sort((a, b) => {
            switch (sortFilter) {
                case 'score-desc':
                    return b.score - a.score;
                case 'score-asc':
                    return a.score - b.score;
                case 'comments-desc':
                    return b.num_comments - a.num_comments;
                case 'comments-asc':
                    return a.num_comments - b.num_comments;
                case 'date-desc':
                    return new Date(b.created_utc) - new Date(a.created_utc);
                case 'date-asc':
                    return new Date(a.created_utc) - new Date(b.created_utc);
                default:
                    return b.score - a.score;
            }
        });
        
        // Update filtered data
        filteredData[categoryKey] = {
            ...filteredData[categoryKey],
            posts: posts,
            count: posts.length,
            percentage: posts.length / currentData.summary.total_posts * 100
        };
    });
    
    // Remove empty categories
    Object.keys(filteredData).forEach(categoryKey => {
        if (filteredData[categoryKey].posts.length === 0) {
            delete filteredData[categoryKey];
        }
    });
    
    renderCategories(filteredData);
}

// Render categories and posts
function renderCategories(categoriesData) {
    const container = document.getElementById('categories-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    Object.entries(categoriesData).forEach(([categoryKey, category]) => {
        const section = document.createElement('div');
        section.className = 'bg-white rounded-xl shadow-md overflow-hidden';
        section.innerHTML = `
            <div class="bg-gradient-to-r from-primary-500 to-secondary-500 text-white p-6 cursor-pointer hover:from-primary-600 hover:to-secondary-600 transition-all duration-200" 
                 onclick="toggleCategory('${categoryKey}')">
                <div class="flex justify-between items-center">
                    <div>
                        <h3 class="text-xl font-bold">${escapeHtml(category.name)}</h3>
                    </div>
                    <div class="flex items-center gap-6 text-sm opacity-90">
                        <span class="flex items-center gap-1">
                            <span>📊</span>
                            <span>${category.count} posts</span>
                        </span>
                        <span class="flex items-center gap-1">
                            <span>📈</span>
                            <span>${category.percentage.toFixed(1)}%</span>
                        </span>
                        <span class="flex items-center gap-1">
                            <span>⭐</span>
                            <span>Avg: ${category.avg_score.toFixed(1)}</span>
                        </span>
                        <span class="flex items-center gap-1">
                            <span>💬</span>
                            <span>Avg: ${category.avg_comments.toFixed(1)}</span>
                        </span>
                        <span class="text-xl transition-transform duration-200" id="toggle-${categoryKey}">▼</span>
                    </div>
                </div>
            </div>
            <div class="p-6 space-y-4" id="posts-${categoryKey}">
                ${renderPosts(category.posts)}
            </div>
        `;
        container.appendChild(section);
    });
}

// Render individual posts
function renderPosts(posts) {
    return posts.map(post => {
        const hasLongContent = post.selftext && post.selftext.length > 300;
        const shortContent = hasLongContent ? post.selftext.substring(0, 300) + '...' : post.selftext;
        const postId = post.id;
        
        // Sentiment badge
        let sentimentBadge = '';
        if (post.sentiment_score !== undefined) {
            if (post.sentiment_score > 0.1) {
                sentimentBadge = '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">😊 Positive</span>';
            } else if (post.sentiment_score < -0.1) {
                sentimentBadge = '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">😞 Negative</span>';
            } else {
                sentimentBadge = '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">😐 Neutral</span>';
            }
        }
        
        return `
            <div class="border border-gray-200 rounded-lg p-5 bg-gray-50 hover:shadow-md transition-shadow duration-200">
                <div class="mb-3">
                    <h4 class="text-lg font-semibold text-gray-900 mb-2">${escapeHtml(post.title)}</h4>
                    <div class="flex flex-wrap gap-3 text-sm text-gray-600">
                        <span class="flex items-center gap-1">
                            <span>👤</span>
                            <span>${escapeHtml(post.author)}</span>
                        </span>
                        <span class="flex items-center gap-1">
                            <span>⭐</span>
                            <span>${post.score}</span>
                        </span>
                        <span class="flex items-center gap-1">
                            <span>💬</span>
                            <span>${post.num_comments}</span>
                        </span>
                        <span class="flex items-center gap-1">
                            <span>📅</span>
                            <span>${new Date(post.created_utc).toLocaleDateString()}</span>
                        </span>
                        ${post.flair_text ? `
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                🏷️ ${escapeHtml(post.flair_text)}
                            </span>
                        ` : ''}
                        ${sentimentBadge}
                    </div>
                </div>
                
                ${post.selftext ? `
                    <div class="mb-4">
                        <div class="text-gray-700 leading-relaxed" id="content-${postId}">
                            ${escapeHtml(shortContent)}
                        </div>
                        ${hasLongContent ? `
                            <button 
                                class="mt-2 text-primary-500 hover:text-primary-600 text-sm font-medium"
                                onclick="toggleContent('${postId}', ${JSON.stringify(post.selftext).replace(/'/g, "\\'")})">
                                Show More
                            </button>
                        ` : ''}
                    </div>
                ` : ''}
                
                ${post.key_insights || post.competitive_intelligence || post.user_persona ? `
                    <div class="bg-blue-50 border-l-4 border-primary-500 p-4 rounded-r-lg">
                        <h5 class="flex items-center gap-2 text-primary-700 font-semibold text-sm mb-3">
                            🤖 AI Insights
                        </h5>
                        <div class="space-y-2 text-sm">
                            ${post.sentiment_score !== undefined ? `
                                <div class="flex justify-between">
                                    <span class="font-medium text-gray-600">Sentiment Score:</span>
                                    <span class="text-gray-900">${post.sentiment_score.toFixed(2)}</span>
                                </div>
                            ` : ''}
                            ${post.urgency_level ? `
                                <div class="flex justify-between">
                                    <span class="font-medium text-gray-600">Urgency Level:</span>
                                    <div class="flex">
                                        ${Array.from({length: 5}, (_, i) => 
                                            `<span class="${i < post.urgency_level ? 'text-yellow-400' : 'text-gray-300'}">⭐</span>`
                                        ).join('')}
                                    </div>
                                </div>
                            ` : ''}
                            ${post.business_impact ? `
                                <div class="flex justify-between">
                                    <span class="font-medium text-gray-600">Business Impact:</span>
                                    <div class="flex">
                                        ${Array.from({length: 5}, (_, i) => 
                                            `<span class="${i < post.business_impact ? 'text-red-400' : 'text-gray-300'}">🔥</span>`
                                        ).join('')}
                                    </div>
                                </div>
                            ` : ''}
                            ${post.user_persona ? `
                                <div>
                                    <span class="font-medium text-gray-600">User Persona:</span>
                                    <p class="text-gray-800 mt-1">${escapeHtml(post.user_persona)}</p>
                                </div>
                            ` : ''}
                            ${post.key_insights ? `
                                <div>
                                    <span class="font-medium text-gray-600">Key Insights:</span>
                                    <p class="text-gray-800 mt-1">${escapeHtml(post.key_insights)}</p>
                                </div>
                            ` : ''}
                            ${post.competitive_intelligence ? `
                                <div>
                                    <span class="font-medium text-gray-600">Competitive Intelligence:</span>
                                    <p class="text-gray-800 mt-1">${escapeHtml(post.competitive_intelligence)}</p>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                ` : ''}
                
                <div class="mt-4 pt-3 border-t border-gray-200">
                    <a 
                        href="${post.permalink}" 
                        target="_blank" 
                        class="inline-flex items-center gap-1 text-primary-500 hover:text-primary-600 text-sm font-medium transition-colors duration-200"
                    >
                        🔗 View on Reddit
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                        </svg>
                    </a>
                </div>
            </div>
        `;
    }).join('');
}

// Toggle category visibility
function toggleCategory(categoryKey) {
    const postsContainer = document.getElementById(`posts-${categoryKey}`);
    const toggleIcon = document.getElementById(`toggle-${categoryKey}`);
    
    if (postsContainer && toggleIcon) {
        const isVisible = !postsContainer.classList.contains('hidden');
        
        if (isVisible) {
            postsContainer.classList.add('hidden');
            toggleIcon.textContent = '▶';
            toggleIcon.style.transform = 'rotate(-90deg)';
        } else {
            postsContainer.classList.remove('hidden');
            toggleIcon.textContent = '▼';
            toggleIcon.style.transform = 'rotate(0deg)';
        }
    }
}

// Toggle post content expansion
function toggleContent(postId, fullContent) {
    const contentElement = document.getElementById(`content-${postId}`);
    const button = event.target;
    
    if (contentElement && button) {
        const isExpanded = button.textContent === 'Show Less';
        
        if (isExpanded) {
            // Show short content
            const shortContent = fullContent.length > 300 ? fullContent.substring(0, 300) + '...' : fullContent;
            contentElement.innerHTML = escapeHtml(shortContent);
            button.textContent = 'Show More';
        } else {
            // Show full content
            contentElement.innerHTML = escapeHtml(fullContent);
            button.textContent = 'Show Less';
        }
    }
}

// Toggle comprehensive report section
function toggleSection(sectionId) {
    console.log('toggleSection called with:', sectionId);
    const section = document.getElementById(sectionId);
    
    if (!section) {
        console.error('Section not found:', sectionId);
        return;
    }
    
    const content = section.querySelector('.report-content');
    const button = section.querySelector('button');
    
    if (content && button) {
        const isHidden = content.classList.contains('hidden');
        
        if (isHidden) {
            content.classList.remove('hidden');
            button.textContent = 'Hide Report';
        } else {
            content.classList.add('hidden');
            button.textContent = 'Show Report';
        }
    }
}

// Populate comprehensive report with markdown content
function populateComprehensiveReport() {
    const content = document.getElementById('comprehensive-content');
    const reportMarkdown = currentData.comprehensive_report;
    
    console.log('Report markdown length:', reportMarkdown ? reportMarkdown.length : 'undefined');
    
    if (!reportMarkdown) {
        content.innerHTML = '<p class="text-gray-500">Comprehensive report not available.</p>';
        return;
    }
    
    // Simple markdown to HTML conversion with Tailwind classes
    let html = reportMarkdown
        // Convert headers
        .replace(/^# (.+)$/gm, '<h1 class="text-3xl font-bold text-gray-900 mt-8 mb-4 first:mt-0">$1</h1>')
        .replace(/^## (.+)$/gm, '<h2 class="text-2xl font-bold text-primary-600 mt-6 mb-3">$1</h2>')  
        .replace(/^### (.+)$/gm, '<h3 class="text-xl font-semibold text-gray-800 mt-4 mb-2">$1</h3>')
        // Convert bold and italic
        .replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
        .replace(/\*(.+?)\*/g, '<em class="italic text-gray-800">$1</em>')
        // Convert code
        .replace(/`(.+?)`/g, '<code class="bg-gray-100 text-gray-800 px-2 py-1 rounded text-sm font-mono">$1</code>')
        // Convert line breaks to paragraphs
        .replace(/\n\n/g, '</p><p class="mb-4">')
        .replace(/\n/g, '<br>')
        // Handle lists
        .replace(/^- (.+)$/gm, '<li class="ml-4 mb-1">$1</li>')
        .replace(/^\* (.+)$/gm, '<li class="ml-4 mb-1">$1</li>');
    
    // Wrap in paragraph tags
    html = '<p class="mb-4">' + html + '</p>';
    
    // Wrap consecutive <li> elements in <ul>
    html = html.replace(/((<li class="ml-4 mb-1">.*?<\/li>\s*)+)/g, '<ul class="list-disc list-inside space-y-1 mb-4 ml-4">$1</ul>');
    
    // Handle tables (enhanced with Tailwind classes) - improved parsing
    let tableRows = [];
    let isInTable = false;
    const lines = html.split('<br>');
    let processedLines = [];
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        // Check if line is a table row (contains |)
        if (line.includes('|') && line.split('|').length > 2) {
            const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell);
            if (cells.length > 0) {
                // Check if this is a header separator line (contains dashes)
                if (line.includes('---') || line.includes('----')) {
                    continue; // Skip separator lines
                }
                
                const isHeader = !isInTable && cells.some(cell => cell.includes('Feature Request') || cell.includes('Recommendation') || cell.includes('Business Impact'));
                
                const rowClass = isHeader ? '' : 'hover:bg-gray-50';
                const cellClass = isHeader 
                    ? 'px-4 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider bg-gradient-to-r from-primary-500 to-secondary-500'
                    : 'px-4 py-2 text-sm text-gray-700 border-b border-gray-200';
                
                const row = '<tr class="' + rowClass + '">' + 
                    cells.map(cell => `<td class="${cellClass}">${cell}</td>`).join('') + 
                    '</tr>';
                
                if (!isInTable) {
                    tableRows = [row];
                    isInTable = true;
                } else {
                    tableRows.push(row);
                }
            }
        } else {
            // End of table - flush accumulated rows
            if (isInTable && tableRows.length > 0) {
                const table = '<div class="overflow-x-auto mb-6"><table class="min-w-full bg-white border border-gray-200 rounded-lg shadow-sm">' + 
                    tableRows.join('') + 
                    '</table></div>';
                processedLines.push(table);
                tableRows = [];
                isInTable = false;
            }
            processedLines.push(line);
        }
    }
    
    // Handle any remaining table at the end
    if (isInTable && tableRows.length > 0) {
        const table = '<div class="overflow-x-auto mb-6"><table class="min-w-full bg-white border border-gray-200 rounded-lg shadow-sm">' + 
            tableRows.join('') + 
            '</table></div>';
        processedLines.push(table);
    }
    
    html = processedLines.join('<br>');
    
    console.log('Processed HTML length:', html.length);
    content.innerHTML = html;
}

// Utility function to escape HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text ? text.replace(/[&<>"']/g, m => map[m]) : '';
}

// Test function for debugging
function testReportData() {
    console.log('Testing report data access...');
    console.log('Data object exists:', typeof currentData !== 'undefined');
    console.log('Comprehensive report exists:', !!currentData.comprehensive_report);
    console.log('Report length:', currentData.comprehensive_report ? currentData.comprehensive_report.length : 'N/A');
    if (currentData.comprehensive_report) {
        console.log('First 200 chars:', currentData.comprehensive_report.substring(0, 200));
    }
    return currentData;
}