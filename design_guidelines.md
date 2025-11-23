# SmartFinanceAI Design Guidelines

## Design Approach
**System-Based Approach**: Drawing from Material Design principles and financial app leaders (Mint, YNAB, Stripe Dashboard) for clarity and trust. Focus on data legibility, hierarchical information display, and professional credibility.

## Core Design Elements

### Typography
- **Primary Font**: Inter (Google Fonts) - clean, highly legible for data
- **Headings**: 
  - H1: text-3xl font-bold (Dashboard titles, page headers)
  - H2: text-2xl font-semibold (Section headers)
  - H3: text-xl font-medium (Card titles, sub-sections)
- **Body**: text-base (Transaction descriptions, form labels)
- **Data/Numbers**: text-lg font-semibold (Financial amounts, stats)
- **Small Text**: text-sm (Helper text, timestamps)

### Layout System
**Spacing Primitives**: Consistent use of p-4, p-6, p-8 for padding; gap-4, gap-6 for grids; mb-4, mb-6, mb-8 for margins.
- **Container**: max-w-7xl mx-auto px-4
- **Dashboard Grid**: 3-column stats cards on desktop (grid-cols-1 md:grid-cols-3 gap-6)
- **Content Cards**: Rounded corners (rounded-lg), subtle shadows (shadow-md)

### Component Library

**Navigation**
- Top navbar with logo left, user menu right
- Includes: Dashboard, Transactions, Add Transaction, Insights, Logout
- Fixed position with subtle bottom border

**Authentication Pages (Login/Register)**
- Centered card layout (max-w-md mx-auto)
- Clean form with generous spacing between fields
- Primary CTA button prominent at bottom
- Link to alternate auth page below

**Dashboard Components**
1. **Stats Cards** (Income/Expense/Balance)
   - Large number display (text-3xl font-bold)
   - Icon + label above number
   - Subtle background treatment
   - Green for income, red for expense, blue for balance indicators

2. **Transaction List**
   - Table format with alternating row backgrounds
   - Columns: Date, Category, Description, Amount, Type
   - Amount right-aligned with income/expense color coding
   - Recent 10 transactions shown with "View All" link

3. **Charts Section**
   - 2-column layout on desktop (Pie chart + Line chart)
   - Chart.js with clean, minimal styling
   - Pie chart: Category breakdown with legend
   - Line chart: Monthly spending trends

4. **AI Insights Panel**
   - Prominent card with icon
   - Bullet list of insights with icons
   - Distinct visual treatment (subtle border accent)

**Add Transaction Form**
- Single-column centered form (max-w-2xl)
- Clear field labels above inputs
- Dropdown for type (Income/Expense) and category
- Date picker, amount input (with currency symbol)
- Text area for description
- Large "Add Transaction" button

**Forms & Inputs**
- Consistent padding (px-4 py-2)
- Border treatment with focus states
- Labels above inputs (font-medium mb-2)
- Helper text below when needed (text-sm text-gray-600)
- Error states with red accent

**Buttons**
- Primary: Solid fill, rounded-md, px-6 py-2
- Secondary: Outline style
- Hover states with subtle transform

### Visual Hierarchy
- Financial amounts are ALWAYS prominent (larger, bolder)
- Category badges use pill shapes (rounded-full px-3 py-1)
- Icons consistently 20px or 24px
- Critical actions (Add Transaction) use larger buttons

### Data Visualization
- Chart.js with consistent color palette across all charts
- Tooltips enabled for interactive data exploration
- Responsive sizing - charts scale with container
- Legend positioned for clarity without clutter

### Images
**No hero images required** - This is a dashboard-focused application prioritizing functionality and data clarity over visual storytelling. All pages lead directly to functional content.

### Trust & Credibility Elements
- Consistent spacing creates professional feel
- Data precision (show 2 decimal places for amounts)
- Clear visual separation between sections
- Timestamp visibility for transaction records

## Animations
**Minimal approach**: Smooth transitions on hover states only (transition-all duration-200). No distracting animations that interfere with data reading.