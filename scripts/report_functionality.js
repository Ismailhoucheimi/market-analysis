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
    tabContents.forEach(content => content.classList.remove('active'));
    
    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab content
    const targetTab = document.getElementById(tabId);
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    // Add active class to clicked button
    if (buttonElement) {
        buttonElement.classList.add('active');
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
        section.className = 'category-section';
        section.innerHTML = `
            <div class="category-header" onclick="toggleCategory('${categoryKey}')">
                <div>
                    <h3>${category.name}</h3>
                </div>
                <div class="category-info">
                    <div class="category-stats">
                        <span>📊 ${category.count} posts</span>
                        <span>📈 ${category.percentage.toFixed(1)}%</span>
                        <span>⭐ Avg Score: ${category.avg_score.toFixed(1)}</span>
                        <span>💬 Avg Comments: ${category.avg_comments.toFixed(1)}</span>
                    </div>
                    <span class="toggle-icon" id="toggle-${categoryKey}">▼</span>
                </div>
            </div>
            <div class="posts-container" id="posts-${categoryKey}" style="display: block;">
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
        
        return `
            <div class="post-card">
                <div class="post-title">${escapeHtml(post.title)}</div>
                <div class="post-meta">
                    <span>👤 ${escapeHtml(post.author)}</span>
                    <span>⭐ ${post.score}</span>
                    <span>💬 ${post.num_comments}</span>
                    <span>📅 ${new Date(post.created_utc).toLocaleDateString()}</span>
                    ${post.flair_text ? `<span>🏷️ ${escapeHtml(post.flair_text)}</span>` : ''}
                </div>
                ${post.selftext ? `
                    <div class="post-content" id="content-${postId}">
                        ${escapeHtml(shortContent)}
                    </div>
                    ${hasLongContent ? `
                        <button class="expand-btn" onclick="toggleContent('${postId}', ${JSON.stringify(post.selftext).replace(/'/g, "\\'")})">
                            Show More
                        </button>
                    ` : ''}
                ` : ''}
                ${post.key_insights || post.competitive_intelligence || post.user_persona ? `
                    <div class="post-insights">
                        <h4>🤖 AI Insights</h4>
                        ${post.sentiment_score !== undefined ? `<p><strong>Sentiment:</strong> ${post.sentiment_score > 0.1 ? '😊 Positive' : post.sentiment_score < -0.1 ? '😞 Negative' : '😐 Neutral'} (${post.sentiment_score.toFixed(2)})</p>` : ''}
                        ${post.urgency_level ? `<p><strong>Urgency:</strong> ${post.urgency_level}/5</p>` : ''}
                        ${post.business_impact ? `<p><strong>Business Impact:</strong> ${post.business_impact}/5</p>` : ''}
                        ${post.user_persona ? `<p><strong>User Persona:</strong> ${escapeHtml(post.user_persona)}</p>` : ''}
                        ${post.key_insights ? `<p><strong>Key Insights:</strong> ${escapeHtml(post.key_insights)}</p>` : ''}
                        ${post.competitive_intelligence ? `<p><strong>Competitive Intel:</strong> ${escapeHtml(post.competitive_intelligence)}</p>` : ''}
                    </div>
                ` : ''}
                <div style="margin-top: 10px;">
                    <a href="${post.permalink}" target="_blank" style="color: #667eea; text-decoration: none; font-size: 0.9rem;">
                        🔗 View on Reddit
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
        const isVisible = postsContainer.style.display !== 'none';
        postsContainer.style.display = isVisible ? 'none' : 'block';
        toggleIcon.textContent = isVisible ? '▶' : '▼';
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
    
    const isHidden = section.style.display === 'none';
    console.log('Section is hidden:', isHidden);
    
    if (isHidden) {
        section.style.display = 'block';
        console.log('Section shown, content populated');
    } else {
        section.style.display = 'none';
        console.log('Section hidden');
    }
}

// Populate comprehensive report with markdown content
function populateComprehensiveReport() {
    const content = document.getElementById('comprehensive-content');
    const reportMarkdown = currentData.comprehensive_report;
    
    console.log('Report markdown length:', reportMarkdown ? reportMarkdown.length : 'undefined');
    
    if (!reportMarkdown) {
        content.innerHTML = '<p>Comprehensive report not available.</p>';
        return;
    }
    
    // Simple markdown to HTML conversion
    let html = reportMarkdown
        // Convert headers
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')  
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        // Convert bold and italic
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        // Convert code
        .replace(/`(.+?)`/g, '<code>$1</code>')
        // Convert line breaks
        .replace(/\n/g, '<br>')
        // Handle lists
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        .replace(/^\* (.+)$/gm, '<li>$1</li>');
    
    // Wrap consecutive <li> elements in <ul>
    html = html.replace(/((<li>.*?<\/li>\s*)+)/g, '<ul>$1</ul>');
    
    // Handle tables (simple pattern)
    html = html.replace(/\|(.+?)\|/g, (match, content) => {
        const cells = content.split('|').map(cell => cell.trim()).filter(cell => cell);
        return '<tr>' + cells.map(cell => `<td>${cell}</td>`).join('') + '</tr>';
    });
    html = html.replace(/((<tr>.*?<\/tr>\s*)+)/g, '<table>$1</table>');
    
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