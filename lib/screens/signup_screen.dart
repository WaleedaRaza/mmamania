import 'package:flutter/material.dart';
import '../models/user.dart';

class SignupScreen extends StatefulWidget {
  @override
  _SignupScreenState createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  
  int _currentStep = 0;
  final int _totalSteps = 4;
  
  // Step 1: Basic Info
  String _username = '';
  String _email = '';
  String _password = '';
  
  // Step 2: Hot Takes
  final List<HotTake> _hotTakes = [];
  final _hotTakeController = TextEditingController();
  
  // Step 3: Favorite Fighters
  final List<String> _favoriteFighters = [];
  final List<String> _availableFighters = [
    'Islam Makhachev',
    'Charles Oliveira',
    'Alexander Volkanovski',
    'Ilia Topuria',
    'Sean O\'Malley',
    'Aljamain Sterling',
    'Leon Edwards',
    'Colby Covington',
    'Israel Adesanya',
    'Dricus Du Plessis',
    'Alex Pereira',
    'Jamahal Hill',
    'Tom Aspinall',
    'Jon Jones',
    'Stipe Miocic',
    'Francis Ngannou',
    'Khabib Nurmagomedov',
    'Conor McGregor',
    'Jorge Masvidal',
    'Nate Diaz',
  ];
  
  // Step 4: GOAT Selection
  String? _selectedGoat;
  final List<String> _goatCandidates = [
    'Jon Jones',
    'Georges St-Pierre',
    'Anderson Silva',
    'Khabib Nurmagomedov',
    'Demetrious Johnson',
    'Amanda Nunes',
    'Valentina Shevchenko',
    'Other',
  ];

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _hotTakeController.dispose();
    super.dispose();
  }

  void _nextStep() {
    if (_currentStep < _totalSteps - 1) {
      setState(() {
        _currentStep++;
      });
    } else {
      _completeSignup();
    }
  }

  void _previousStep() {
    if (_currentStep > 0) {
      setState(() {
        _currentStep--;
      });
    }
  }

  void _addHotTake() {
    if (_hotTakeController.text.trim().isNotEmpty) {
      setState(() {
        _hotTakes.add(HotTake(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          title: _hotTakeController.text.trim(),
          description: _hotTakeController.text.trim(),
          createdAt: DateTime.now(),
        ));
        _hotTakeController.clear();
      });
    }
  }

  void _removeHotTake(String id) {
    setState(() {
      _hotTakes.removeWhere((hotTake) => hotTake.id == id);
    });
  }

  void _toggleFavoriteFighter(String fighter) {
    setState(() {
      if (_favoriteFighters.contains(fighter)) {
        _favoriteFighters.remove(fighter);
      } else if (_favoriteFighters.length < 5) {
        _favoriteFighters.add(fighter);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('You can only select 5 favorite fighters')),
        );
      }
    });
  }

  void _completeSignup() {
    if (_formKey.currentState!.validate() && 
        _hotTakes.isNotEmpty && 
        _favoriteFighters.length >= 5 && 
        _selectedGoat != null) {
      
      // TODO: Create user and navigate to main app
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Account created successfully!')),
      );
      
      // Navigate to main app
      Navigator.of(context).pushReplacementNamed('/home');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please complete all required fields')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1A1A1A),
      appBar: AppBar(
        title: const Text('Create Your Profile'),
        backgroundColor: const Color(0xFF2D2D2D),
        elevation: 0,
        leading: _currentStep > 0 
            ? IconButton(
                icon: const Icon(Icons.arrow_back),
                onPressed: _previousStep,
              )
            : null,
      ),
      body: Column(
        children: [
          // Progress Indicator
          _buildProgressIndicator(),
          
          // Content
          Expanded(
            child: Form(
              key: _formKey,
              child: _buildCurrentStep(),
            ),
          ),
          
          // Navigation Buttons
          _buildNavigationButtons(),
        ],
      ),
    );
  }

  Widget _buildProgressIndicator() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Row(
            children: List.generate(_totalSteps, (index) {
              final isActive = index <= _currentStep;
              final isCompleted = index < _currentStep;
              
              return Expanded(
                child: Container(
                  height: 4,
                  margin: EdgeInsets.only(right: index < _totalSteps - 1 ? 8 : 0),
                  decoration: BoxDecoration(
                    color: isCompleted 
                        ? Colors.red 
                        : isActive 
                            ? Colors.red.withOpacity(0.5)
                            : Colors.grey.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              );
            }),
          ),
          const SizedBox(height: 8),
          Text(
            'Step ${_currentStep + 1} of $_totalSteps',
            style: const TextStyle(
              color: Colors.grey,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCurrentStep() {
    switch (_currentStep) {
      case 0:
        return _buildBasicInfoStep();
      case 1:
        return _buildHotTakesStep();
      case 2:
        return _buildFavoriteFightersStep();
      case 3:
        return _buildGoatSelectionStep();
      default:
        return const SizedBox();
    }
  }

  Widget _buildBasicInfoStep() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Basic Information',
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Tell us about yourself',
            style: TextStyle(
              color: Colors.grey,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 32),
          
          TextFormField(
            controller: _usernameController,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: 'Username',
              labelStyle: TextStyle(color: Colors.grey),
              border: OutlineInputBorder(),
              enabledBorder: OutlineInputBorder(
                borderSide: BorderSide(color: Colors.grey),
              ),
              focusedBorder: OutlineInputBorder(
                borderSide: BorderSide(color: Colors.red),
              ),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter a username';
              }
              if (value.length < 3) {
                return 'Username must be at least 3 characters';
              }
              return null;
            },
            onChanged: (value) => _username = value,
          ),
          
          const SizedBox(height: 16),
          
          TextFormField(
            controller: _emailController,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: 'Email',
              labelStyle: TextStyle(color: Colors.grey),
              border: OutlineInputBorder(),
              enabledBorder: OutlineInputBorder(
                borderSide: BorderSide(color: Colors.grey),
              ),
              focusedBorder: OutlineInputBorder(
                borderSide: BorderSide(color: Colors.red),
              ),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter an email';
              }
              if (!value.contains('@')) {
                return 'Please enter a valid email';
              }
              return null;
            },
            onChanged: (value) => _email = value,
          ),
          
          const SizedBox(height: 16),
          
          TextFormField(
            controller: _passwordController,
            style: const TextStyle(color: Colors.white),
            obscureText: true,
            decoration: const InputDecoration(
              labelText: 'Password',
              labelStyle: TextStyle(color: Colors.grey),
              border: OutlineInputBorder(),
              enabledBorder: OutlineInputBorder(
                borderSide: BorderSide(color: Colors.grey),
              ),
              focusedBorder: OutlineInputBorder(
                borderSide: BorderSide(color: Colors.red),
              ),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter a password';
              }
              if (value.length < 6) {
                return 'Password must be at least 6 characters';
              }
              return null;
            },
            onChanged: (value) => _password = value,
          ),
        ],
      ),
    );
  }

  Widget _buildHotTakesStep() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Your Hot Takes',
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Share your controversial MMA opinions',
            style: TextStyle(
              color: Colors.grey,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 32),
          
          // Add Hot Take
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _hotTakeController,
                  style: const TextStyle(color: Colors.white),
                  decoration: const InputDecoration(
                    hintText: 'Enter your hot take...',
                    hintStyle: TextStyle(color: Colors.grey),
                    border: OutlineInputBorder(),
                    enabledBorder: OutlineInputBorder(
                      borderSide: BorderSide(color: Colors.grey),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderSide: BorderSide(color: Colors.red),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton(
                onPressed: _addHotTake,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                ),
                child: const Text('Add'),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Hot Takes List
          Expanded(
            child: _hotTakes.isEmpty
                ? const Center(
                    child: Text(
                      'No hot takes yet. Add your first one!',
                      style: TextStyle(color: Colors.grey),
                    ),
                  )
                : ListView.builder(
                    itemCount: _hotTakes.length,
                    itemBuilder: (context, index) {
                      final hotTake = _hotTakes[index];
                      return Card(
                        color: const Color(0xFF2D2D2D),
                        margin: const EdgeInsets.only(bottom: 8),
                        child: ListTile(
                          title: Text(
                            hotTake.title,
                            style: const TextStyle(color: Colors.white),
                          ),
                          trailing: IconButton(
                            icon: const Icon(Icons.delete, color: Colors.red),
                            onPressed: () => _removeHotTake(hotTake.id),
                          ),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildFavoriteFightersStep() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Favorite Fighters',
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Select your top 5 fighters (${_favoriteFighters.length}/5)',
            style: const TextStyle(
              color: Colors.grey,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 32),
          
          // Selected Fighters
          if (_favoriteFighters.isNotEmpty) ...[
            const Text(
              'Selected:',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _favoriteFighters.map((fighter) {
                return Chip(
                  label: Text(fighter),
                  backgroundColor: Colors.red.withOpacity(0.2),
                  labelStyle: const TextStyle(color: Colors.red),
                  deleteIcon: const Icon(Icons.close, color: Colors.red, size: 18),
                  onDeleted: () => _toggleFavoriteFighter(fighter),
                );
              }).toList(),
            ),
            const SizedBox(height: 24),
          ],
          
          // Available Fighters
          const Text(
            'Available Fighters:',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          
          Expanded(
            child: GridView.builder(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 8,
                mainAxisSpacing: 8,
                childAspectRatio: 3,
              ),
              itemCount: _availableFighters.length,
              itemBuilder: (context, index) {
                final fighter = _availableFighters[index];
                final isSelected = _favoriteFighters.contains(fighter);
                final isDisabled = !isSelected && _favoriteFighters.length >= 5;
                
                return GestureDetector(
                  onTap: isDisabled ? null : () => _toggleFavoriteFighter(fighter),
                  child: Container(
                    decoration: BoxDecoration(
                      color: isSelected 
                          ? Colors.red.withOpacity(0.2)
                          : isDisabled
                              ? Colors.grey.withOpacity(0.1)
                              : const Color(0xFF2D2D2D),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: isSelected 
                            ? Colors.red 
                            : Colors.grey.withOpacity(0.3),
                      ),
                    ),
                    child: Center(
                      child: Text(
                        fighter,
                        style: TextStyle(
                          color: isSelected 
                              ? Colors.red 
                              : isDisabled
                                  ? Colors.grey.withOpacity(0.5)
                                  : Colors.white,
                          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGoatSelectionStep() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Who is the GOAT?',
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Select your pick for Greatest of All Time',
            style: const TextStyle(
              color: Colors.grey,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 32),
          
          Expanded(
            child: ListView.builder(
              itemCount: _goatCandidates.length,
              itemBuilder: (context, index) {
                final candidate = _goatCandidates[index];
                final isSelected = _selectedGoat == candidate;
                
                return Card(
                  color: isSelected 
                      ? Colors.red.withOpacity(0.2)
                      : const Color(0xFF2D2D2D),
                  margin: const EdgeInsets.only(bottom: 8),
                  child: ListTile(
                    title: Text(
                      candidate,
                      style: TextStyle(
                        color: isSelected ? Colors.red : Colors.white,
                        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                      ),
                    ),
                    trailing: isSelected 
                        ? const Icon(Icons.check_circle, color: Colors.red)
                        : const Icon(Icons.radio_button_unchecked, color: Colors.grey),
                    onTap: () {
                      setState(() {
                        _selectedGoat = candidate;
                      });
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNavigationButtons() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          if (_currentStep > 0)
            Expanded(
              child: OutlinedButton(
                onPressed: _previousStep,
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.white,
                  side: const BorderSide(color: Colors.grey),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: const Text('Previous'),
              ),
            ),
          if (_currentStep > 0) const SizedBox(width: 16),
          Expanded(
            child: ElevatedButton(
              onPressed: _currentStep == _totalSteps - 1 ? _completeSignup : _nextStep,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: Text(_currentStep == _totalSteps - 1 ? 'Create Account' : 'Next'),
            ),
          ),
        ],
      ),
    );
  }
} 