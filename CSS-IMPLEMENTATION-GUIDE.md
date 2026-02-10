═══════════════════════════════════════════════════════════════════════════════
SATID WEBSITE - CSS IMPLEMENTATION GUIDE
For Creating New Pages with Consistent Styling
═══════════════════════════════════════════════════════════════════════════════

MASTER CSS FILE: SATID-COMPLETE-MASTER-STYLES.css
This file contains ALL tested and verified styling rules.
Use this as your reference for creating new pages.

═══════════════════════════════════════════════════════════════════════════════
APPROACH: EMBEDDED CSS (RECOMMENDED)
═══════════════════════════════════════════════════════════════════════════════

WHY EMBEDDED CSS:
✓ Self-contained - everything in one file
✓ No file path issues
✓ Can't lose the CSS file
✓ Portable - works anywhere
✓ No confusion about CSS versions

HOW TO USE:
1. Copy entire contents of SATID-COMPLETE-MASTER-STYLES.css
2. Paste between <style> tags in your HTML <head> section
3. Done!

═══════════════════════════════════════════════════════════════════════════════
HTML TEMPLATE STRUCTURE
═══════════════════════════════════════════════════════════════════════════════

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SATID - [PAGE NAME]</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        /* PASTE ENTIRE CSS FROM SATID-COMPLETE-MASTER-STYLES.css HERE */
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="nav-container">
            <ul class="nav-menu">
                <li><a href="index.html">Index</a></li>
                <li><a href="Philosophy.html">Philosophy</a></li>
                <li><a href="Methodology.html">Methodology</a></li>
                <li><a href="Support_Levels_Interactive.html">Risk Level Setting</a></li>
                <li><a href="Portfolio_Risk_Exposure.html">Risk Exposure</a></li>
                <li><a href="SATID_Risk_Score.html">Risk Score</a></li>
                <li><a href="Portfolio_Risk_Dashboard.html">Risk Dashboard</a></li>
                <li class="dropdown">
                    <a href="#" class="dropbtn">Market Views</a>
                    <div class="dropdown-content">
                        <a href="Market_Views.html">About Market Views</a>
                        <a href="SATID_Relative_Performance.html">Cross Asset Validations</a>
                    </div>
                </li>
                <li class="dropdown">
                    <a href="#" class="dropbtn">Appendix</a>
                    <div class="dropdown-content">
                        <a href="Portfolios_Performance.html">Portfolio Performance Analysis</a>
                        <a href="Conventional_Portfolio_Profiles.html">Conventional Portfolio Profiles</a>
                        <a href="model_portfolios.html">Model Portfolios</a>
                        <a href="Portfolio_Statistics.html">Portfolio Statistics</a>
                    </div>
                </li>
            </ul>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
        <div class="hero-content">
            <h1>[PAGE TITLE]</h1>
            <p class="hero-subtitle">[Page Subtitle]</p>
        </div>
    </section>

    <!-- Main Content Container -->
    <div class="container">
        <div class="content-page">
            
            <!-- Content Section -->
            <section class="content-section">
                <h2>[SECTION TITLE]</h2>
                <p>[Your content here]</p>
                
                <h3>[Subsection Title]</h3>
                <p>[Your content here]</p>
            </section>

        </div>
    </div>

    <!-- Footer -->
    <footer>
        <p>&copy; 2024 SATID Investment Management. All rights reserved.</p>
    </footer>
</body>
</html>

═══════════════════════════════════════════════════════════════════════════════
CSS CLASSES REFERENCE
═══════════════════════════════════════════════════════════════════════════════

NAVIGATION:
.navbar              - Navigation bar container
.nav-container       - Centers navigation content
.nav-menu           - Horizontal menu list
.dropdown           - Dropdown menu container
.dropdown-content   - Dropdown menu items

HERO SECTION:
.hero               - Full-width colored header
.hero-content       - Centered hero content
.hero h1            - Main title (3.5rem)
.hero-subtitle      - Subtitle text (1.6rem)

CONTENT LAYOUT:
.container          - Outer wrapper (full width, 100%)
.content-page       - White content box (max-width: 850px, centered)

CONTENT SECTIONS:
.content-section    - Section wrapper
.content-section h2 - Centered section title with underline
.content-section h3 - Left-aligned subsection title with underline
.content-section p  - Body text (1.1rem)

SPECIAL ELEMENTS:
.highlight-box      - Shaded box for important content
.key-point          - Hover-enabled highlight box
.chart-container    - Container for charts/graphs

TABLES:
.comparison-table-wrapper  - Table wrapper with shadow
.comparison-table         - Styled table
.comparison-table th      - Blue gradient header
.comparison-table td      - Table cells with hover

═══════════════════════════════════════════════════════════════════════════════
COMMON PATTERNS
═══════════════════════════════════════════════════════════════════════════════

1. LINKED SECTION TITLES (like in Methodology page):
   <h3><a href="target_page.html">Your Title Here</a></h3>
   - Automatically styled with blue underline
   - Hover changes to lighter blue
   - No inline styles needed!

2. HIGHLIGHT BOX:
   <div class="highlight-box">
       <p>Important content here</p>
   </div>

3. KEY POINT BOX (with hover effect):
   <div class="key-point">
       <p>Important content with hover effect</p>
   </div>

4. COMPARISON TABLE:
   <div class="comparison-table-wrapper">
       <table class="comparison-table">
           <thead>
               <tr>
                   <th>Column 1</th>
                   <th>Column 2</th>
               </tr>
           </thead>
           <tbody>
               <tr>
                   <td>Data 1</td>
                   <td>Data 2</td>
               </tr>
           </tbody>
       </table>
   </div>

═══════════════════════════════════════════════════════════════════════════════
KEY STYLING SPECIFICATIONS
═══════════════════════════════════════════════════════════════════════════════

COLORS:
- Primary Blue: #1e3c72
- Secondary Blue: #2a5298
- Light Blue: #3d6cb9
- Text Gray: #4a5568
- Background Gray: #f8f9fa

TYPOGRAPHY:
- Font Family: 'Inter'
- Hero H1: 3.5rem (56px)
- Hero Subtitle: 1.6rem (25.6px)
- Section H2: 2rem (32px)
- Subsection H3: 1.4rem (22.4px)
- Body Text: 1.1rem (17.6px)
- Navigation: 17px

LAYOUT:
- Content Box Max Width: 850px
- Content Box Padding: 50px 30px 70px 30px
- Section Margin Bottom: 50px
- Responsive Breakpoints: 1400px, 768px

═══════════════════════════════════════════════════════════════════════════════
CRITICAL RULES (DON'T CHANGE THESE!)
═══════════════════════════════════════════════════════════════════════════════

1. CONTAINER MUST BE 100% WIDTH:
   .container {
       max-width: 100% !important;
       padding: 0 10px !important;
   }

2. CONTENT-PAGE MUST HAVE 850PX MAX-WIDTH:
   .content-page {
       max-width: 850px;
       margin-left: auto;
       margin-right: auto;
   }

3. NAVIGATION FONT SIZE:
   .nav-menu a {
       font-size: 17px;
   }

4. LINKED H3 TITLES:
   Don't add inline styles!
   Just use: <h3><a href="...">Title</a></h3>

═══════════════════════════════════════════════════════════════════════════════
TESTING CHECKLIST
═══════════════════════════════════════════════════════════════════════════════

Before considering a page complete, verify:

☐ Navigation menu is horizontal (not vertical)
☐ Navigation text is readable size (17px)
☐ Content is centered with white space on sides
☐ White content box is ~850px wide
☐ Hero title is 3.5rem (large)
☐ Section titles (h2) are centered with blue underline
☐ Subsection titles (h3) are left-aligned with blue underline
☐ Body text is 1.1rem (readable)
☐ Linked titles have visible underlines
☐ Highlight boxes have correct font size
☐ Footer is blue gradient
☐ All links work (navigation, h3 links)
☐ Page looks good on mobile (test at 768px width)

═══════════════════════════════════════════════════════════════════════════════
WORKFLOW FOR NEW PAGES
═══════════════════════════════════════════════════════════════════════════════

1. Copy the HTML template above
2. Open SATID-COMPLETE-MASTER-STYLES.css
3. Copy ALL CSS content
4. Paste into <style> tags in HTML <head>
5. Update page-specific content:
   - Title in <title> tag
   - Hero h1 and subtitle
   - Content sections
6. Update navigation (mark current page with class="active")
7. Test in browser
8. Verify against checklist above
9. Save and deploy

═══════════════════════════════════════════════════════════════════════════════
TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

PROBLEM: Navigation is vertical
→ Check .nav-menu has display: flex

PROBLEM: Content spans full width
→ Check .content-page has max-width: 850px and margin: auto

PROBLEM: Navigation text too small
→ Check .nav-menu a has font-size: 17px

PROBLEM: Linked titles don't have underlines
→ Remove any inline styles from <a> tags

PROBLEM: Highlight box text too small
→ Check .highlight-box p has font-size: 1.1rem

═══════════════════════════════════════════════════════════════════════════════

Questions? Reference the working Methodology.html file as your example!
