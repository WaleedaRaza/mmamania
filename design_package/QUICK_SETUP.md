# Quick Setup Guide

## 🚀 Fast Integration Steps

### 1. Copy Design Files
```bash
# Copy the entire lib folder to your new app
cp -r /Users/waleedraza/Desktop/mmamania/design_package/lib/* your_new_app/lib/
```

### 2. Update Dependencies
Add these to your `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # Essential UI packages
  cupertino_icons: ^1.0.6
  flutter_svg: ^2.0.9
  cached_network_image: ^3.3.0
  shimmer: ^3.0.0
  
  # Navigation
  go_router: ^12.1.3
  
  # State Management
  provider: ^6.1.1
  
  # HTTP & API
  http: ^1.1.0
  
  # Charts & Analytics
  fl_chart: ^0.65.0
  
  # Date & Time
  intl: ^0.18.1
```

### 3. Update Main App
Replace your `main.dart` with the design package version, then customize:

```dart
// Change app name and colors
class YourAppName extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Your App Name',
      theme: ThemeData(
        primarySwatch: Colors.blue, // Change to your brand color
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: MainScaffold(),
    );
  }
}
```

### 4. Customize Navigation
Update the navigation items in `main.dart`:

```dart
static const List<Widget> _screens = <Widget>[
  YourHomeScreen(),
  YourRankingsScreen(),
  YourFeatureScreen(),
  // Add your screens here
];
```

### 5. Update Bottom Navigation
Modify the bottom navigation bar items:

```dart
items: const [
  BottomNavigationBarItem(
    icon: Icon(Icons.home),
    label: 'Home',
  ),
  BottomNavigationBarItem(
    icon: Icon(Icons.your_icon),
    label: 'Your Feature',
  ),
  // Add your navigation items
],
```

## 🎨 Quick Customization

### Change Primary Color
```dart
// In main.dart
theme: ThemeData(
  primarySwatch: Colors.blue, // Change this
  visualDensity: VisualDensity.adaptivePlatformDensity,
),
```

### Update App Bar
```dart
// In main.dart
AppBar(
  title: Text('Your App Name'), // Change this
  backgroundColor: Colors.black, // Or your brand color
  foregroundColor: Colors.white,
),
```

### Customize Cards
```dart
// In any widget file
Card(
  margin: const EdgeInsets.only(bottom: 12),
  child: InkWell(
    onTap: onTap,
    borderRadius: BorderRadius.circular(12), // Adjust radius
    child: Padding(
      padding: const EdgeInsets.all(16), // Adjust padding
      child: Column(
        // Your content
      ),
    ),
  ),
)
```

## 📱 Essential Widgets to Use

### Event Cards
```dart
import 'package:your_app/widgets/event_card_widget.dart';

EventCardWidget(
  event: yourEvent,
  onTap: () {
    // Handle tap
  },
)
```

### Fight Cards
```dart
import 'package:your_app/widgets/fight_card_widget.dart';

FightCardWidget(
  fightCard: yourFightCard,
  onTap: () {
    // Handle tap
  },
)
```

### Status Chips
```dart
Container(
  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
  decoration: BoxDecoration(
    color: Colors.blue.withOpacity(0.1),
    borderRadius: BorderRadius.circular(12),
    border: Border.all(color: Colors.blue),
  ),
  child: Row(
    mainAxisSize: MainAxisSize.min,
    children: [
      Icon(Icons.schedule, size: 14, color: Colors.blue),
      SizedBox(width: 4),
      Text(
        'Status',
        style: TextStyle(
          color: Colors.blue,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
    ],
  ),
)
```

## 🔧 Common Customizations

### Loading States
```dart
if (_isLoading) {
  return const Center(child: CircularProgressIndicator());
}
```

### Error Handling
```dart
void _showErrorSnackBar(String message) {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Text(message),
      backgroundColor: Colors.red,
    ),
  );
}
```

### Success Messages
```dart
void _showSuccessSnackBar(String message) {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Text(message),
      backgroundColor: Colors.green,
    ),
  );
}
```

## 📋 Checklist

- [ ] Copied all design files to your app
- [ ] Updated `pubspec.yaml` with required dependencies
- [ ] Customized app name and colors in `main.dart`
- [ ] Updated navigation items
- [ ] Tested the app runs without errors
- [ ] Customized branding elements
- [ ] Added your specific features
- [ ] Tested on different screen sizes

## 🆘 Troubleshooting

### Import Errors
Make sure all import paths are correct for your project structure.

### Missing Dependencies
Run `flutter pub get` after updating `pubspec.yaml`.

### Navigation Issues
Check that all screen classes exist and are properly imported.

### Styling Problems
Verify that the theme is properly applied in `main.dart`.

## 📞 Next Steps

1. **Customize Colors**: Update the color scheme to match your brand
2. **Add Your Features**: Integrate your specific functionality
3. **Test Navigation**: Ensure all navigation flows work correctly
4. **Optimize Performance**: Test on different devices and screen sizes
5. **Add Content**: Replace placeholder content with your actual data

For detailed customization options, see `DESIGN_SYSTEM.md`. 