# MMA App Design System

## 🎨 Color Palette

### Primary Colors
```dart
// Main brand colors
Colors.red          // Primary brand color
Colors.black        // App bars, dark elements
Colors.white        // Background, text on dark surfaces
```

### Status Colors
```dart
// Event and fight status colors
Colors.blue         // Upcoming events
Colors.green        // Completed fights
Colors.orange       // Co-main events, updates
Colors.purple       // PPV events
Colors.grey         // Past events, disabled states
```

### Semantic Colors
```dart
// Success, warning, error states
Colors.green[700]   // Success indicators
Colors.orange[700]  // Warning/update indicators
Colors.red          // Error states
Colors.blue[700]    // Information
```

## 📏 Spacing System

### Padding & Margins
```dart
// Standard spacing values
const EdgeInsets.all(4)      // Small spacing
const EdgeInsets.all(8)      // Medium spacing
const EdgeInsets.all(12)     // Large spacing
const EdgeInsets.all(16)     // Extra large spacing
const EdgeInsets.all(20)     // Section spacing
const EdgeInsets.all(24)     // Screen margins
```

### Border Radius
```dart
// Consistent border radius
BorderRadius.circular(8)     // Small components
BorderRadius.circular(12)    // Cards, chips
BorderRadius.circular(16)    // Large components
```

## 🔤 Typography

### Text Styles
```dart
// Headings
Theme.of(context).textTheme.titleLarge?.copyWith(
  fontWeight: FontWeight.bold,
)

// Body text
Theme.of(context).textTheme.bodyMedium?.copyWith(
  color: Colors.grey[600],
)

// Small text (chips, labels)
TextStyle(
  fontSize: 12,
  fontWeight: FontWeight.bold,
)
```

## 🧩 Component Patterns

### Cards
```dart
Card(
  margin: const EdgeInsets.only(bottom: 12),
  child: InkWell(
    onTap: onTap,
    borderRadius: BorderRadius.circular(12),
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Card content
        ],
      ),
    ),
  ),
)
```

### Status Chips
```dart
Container(
  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
  decoration: BoxDecoration(
    color: chipColor.withOpacity(0.1),
    borderRadius: BorderRadius.circular(12),
    border: Border.all(color: chipColor),
  ),
  child: Row(
    mainAxisSize: MainAxisSize.min,
    children: [
      Icon(chipIcon, size: 14, color: chipColor),
      const SizedBox(width: 4),
      Text(
        chipText,
        style: TextStyle(
          color: chipColor,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
    ],
  ),
)
```

### Buttons
```dart
ElevatedButton(
  onPressed: onPressed,
  style: ElevatedButton.styleFrom(
    backgroundColor: Colors.red,
    foregroundColor: Colors.white,
    padding: EdgeInsets.symmetric(horizontal: 30, vertical: 15),
  ),
  child: Text(
    'Button Text',
    style: TextStyle(fontSize: 16),
  ),
)
```

## 🧭 Navigation Patterns

### Bottom Navigation
```dart
BottomNavigationBar(
  type: BottomNavigationBarType.fixed,
  currentIndex: _selectedIndex,
  onTap: _onItemTapped,
  selectedItemColor: Colors.red,
  unselectedItemColor: Colors.grey,
  items: const [
    BottomNavigationBarItem(
      icon: Icon(Icons.home),
      label: 'Home',
    ),
    // More items...
  ],
)
```

### Drawer Navigation
```dart
Drawer(
  child: ListView(
    padding: EdgeInsets.zero,
    children: <Widget>[
      DrawerHeader(
        decoration: BoxDecoration(
          color: Colors.red,
        ),
        child: Text(
          'Menu Title',
          style: TextStyle(
            color: Colors.white,
            fontSize: 24,
          ),
        ),
      ),
      ListTile(
        leading: Icon(Icons.home),
        title: Text('Menu Item'),
        onTap: () {
          // Navigation logic
        },
      ),
    ],
  ),
)
```

### Tab Navigation
```dart
TabBar(
  controller: _tabController,
  tabs: const [
    Tab(text: 'Tab 1'),
    Tab(text: 'Tab 2'),
    Tab(text: 'Tab 3'),
  ],
)
```

## 📱 Screen Layouts

### Standard Screen Structure
```dart
Scaffold(
  appBar: AppBar(
    title: Text('Screen Title'),
    backgroundColor: Colors.black,
    foregroundColor: Colors.white,
    actions: [
      IconButton(
        icon: Icon(Icons.refresh),
        onPressed: onRefresh,
      ),
    ],
  ),
  body: SingleChildScrollView(
    padding: const EdgeInsets.all(16),
    child: Column(
      children: [
        // Screen content
      ],
    ),
  ),
)
```

### Loading States
```dart
if (_isLoading) {
  return const Center(child: CircularProgressIndicator());
}
```

### Empty States
```dart
Center(
  child: Column(
    mainAxisAlignment: MainAxisAlignment.center,
    children: [
      Icon(Icons.event_busy, size: 64, color: Colors.grey),
      SizedBox(height: 16),
      Text(
        'No data available',
        style: TextStyle(fontSize: 18, color: Colors.grey[600]),
      ),
    ],
  ),
)
```

## 🎯 Interactive Elements

### Tap Effects
```dart
InkWell(
  onTap: onTap,
  borderRadius: BorderRadius.circular(12),
  child: Container(
    // Content
  ),
)
```

### Feedback Messages
```dart
// Success message
ScaffoldMessenger.of(context).showSnackBar(
  SnackBar(
    content: Text(message),
    backgroundColor: Colors.green,
  ),
)

// Error message
ScaffoldMessenger.of(context).showSnackBar(
  SnackBar(
    content: Text(message),
    backgroundColor: Colors.red,
  ),
)
```

## 🔄 State Management Patterns

### Loading States
```dart
bool _isLoading = false;

// Set loading
setState(() {
  _isLoading = true;
});

// Clear loading
setState(() {
  _isLoading = false;
});
```

### Data Refresh
```dart
Future<void> _refreshData() async {
  setState(() {
    _isLoading = true;
  });
  
  try {
    // Load data
    await _loadData();
    _showSuccessSnackBar('Data refreshed');
  } catch (e) {
    _showErrorSnackBar('Error refreshing: $e');
  } finally {
    setState(() {
      _isLoading = false;
    });
  }
}
```

## 🎨 Custom Widgets

### Event Cards
- Display event information with location and venue
- Color-coded status chips
- Special highlighting for main/co-main events
- Broadcast information display

### Fight Cards
- Show fight summaries with status indicators
- Update notifications for recently modified cards
- Fight count and completion status

### Analytics Components
- Charts and data visualization
- Performance metrics display
- Interactive data exploration

## 📐 Responsive Design

### Adaptive Layouts
```dart
// Use flexible layouts
Expanded(
  child: Column(
    children: [
      // Content that adapts to screen size
    ],
  ),
)
```

### Screen Size Considerations
- Use `MediaQuery` for screen dimensions
- Implement responsive breakpoints
- Test on different device sizes

## ♿ Accessibility

### Semantic Labels
```dart
Semantics(
  label: 'Event card for ${event.title}',
  child: EventCardWidget(event: event),
)
```

### Touch Targets
- Minimum 48x48dp touch targets
- Adequate spacing between interactive elements
- Clear visual feedback for interactions

### Color Contrast
- Ensure sufficient contrast ratios
- Don't rely solely on color for information
- Provide alternative text for images

## 🚀 Performance Considerations

### Efficient Rebuilding
```dart
// Use const constructors where possible
const EventCardWidget({Key? key, required this.event}) : super(key: key);
```

### Image Optimization
```dart
// Use cached network images
CachedNetworkImage(
  imageUrl: imageUrl,
  placeholder: (context, url) => Shimmer.fromColors(
    baseColor: Colors.grey[300]!,
    highlightColor: Colors.grey[100]!,
    child: Container(color: Colors.white),
  ),
  errorWidget: (context, url, error) => Icon(Icons.error),
)
```

### Lazy Loading
- Implement pagination for large lists
- Load images on demand
- Use `ListView.builder` for long lists

## 🔧 Customization Guide

### Theme Modification
```dart
// In main.dart
theme: ThemeData(
  primarySwatch: Colors.blue, // Change primary color
  visualDensity: VisualDensity.adaptivePlatformDensity,
  // Add custom theme data
  cardTheme: CardTheme(
    elevation: 2,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(12),
    ),
  ),
),
```

### Component Customization
1. Copy the widget file to your project
2. Modify colors, spacing, and typography
3. Update the widget to match your brand
4. Test across different screen sizes

### Adding New Components
1. Follow the existing naming conventions
2. Use the established design patterns
3. Include proper documentation
4. Test accessibility and performance 