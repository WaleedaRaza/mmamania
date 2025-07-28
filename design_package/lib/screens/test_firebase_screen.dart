import 'package:flutter/material.dart';
import '../services/firebase_service.dart';
import '../models/ufc_rankings.dart';

class TestFirebaseScreen extends StatefulWidget {
  const TestFirebaseScreen({super.key});

  @override
  State<TestFirebaseScreen> createState() => _TestFirebaseScreenState();
}

class _TestFirebaseScreenState extends State<TestFirebaseScreen> {
  List<String> divisions = [];
  List<UFCRanking> rankings = [];
  bool isLoading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    _testFirebaseConnection();
  }

  Future<void> _testFirebaseConnection() async {
    try {
      setState(() {
        isLoading = true;
        error = null;
      });

      print('🧪 Testing Firebase connection...');

      // Test 1: Get available divisions
      print('📋 Test 1: Getting divisions...');
      final availableDivisions = await FirebaseService.getAvailableDivisions();
      print('✅ Divisions found: $availableDivisions');

      // Test 2: Get rankings for first division
      if (availableDivisions.isNotEmpty) {
        print('📊 Test 2: Getting rankings for ${availableDivisions.first}...');
        final rankingsData = await FirebaseService.getRankings(availableDivisions.first);
        print('✅ Rankings found: ${rankingsData.length}');

        setState(() {
          divisions = availableDivisions;
          rankings = rankingsData;
          isLoading = false;
        });
      } else {
        setState(() {
          error = 'No divisions found in Firestore';
          isLoading = false;
        });
      }
    } catch (e) {
      print('❌ Firebase test failed: $e');
      setState(() {
        error = 'Firebase connection failed: $e';
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Firebase Test'),
        backgroundColor: Colors.black,
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Test Results
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Firebase Connection Test',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 16),
                    if (isLoading)
                      const Row(
                        children: [
                          CircularProgressIndicator(),
                          SizedBox(width: 16),
                          Text('Testing connection...'),
                        ],
                      ),
                    if (error != null)
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.red[100],
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.error, color: Colors.red),
                            const SizedBox(width: 8),
                            Expanded(child: Text(error!)),
                          ],
                        ),
                      ),
                    if (!isLoading && error == null) ...[
                      Row(
                        children: [
                          const Icon(Icons.check_circle, color: Colors.green),
                          const SizedBox(width: 8),
                          Text('✅ Firebase connected successfully'),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text('📊 Divisions found: ${divisions.length}'),
                      Text('🥊 Rankings found: ${rankings.length}'),
                    ],
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Divisions List
            if (divisions.isNotEmpty) ...[
              Text(
                'Available Divisions:',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: divisions.map((division) {
                  return Chip(
                    label: Text(division),
                    backgroundColor: Colors.blue[100],
                  );
                }).toList(),
              ),
            ],
            
            const SizedBox(height: 16),
            
            // Rankings List
            if (rankings.isNotEmpty) ...[
              Text(
                'Sample Rankings:',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              Expanded(
                child: ListView.builder(
                  itemCount: rankings.take(10).length,
                  itemBuilder: (context, index) {
                    final ranking = rankings[index];
                    return ListTile(
                      leading: CircleAvatar(
                        backgroundColor: Colors.blue,
                        child: Text(
                          ranking.rank.toString(),
                          style: const TextStyle(color: Colors.white),
                        ),
                      ),
                      title: Text(ranking.name),
                      subtitle: Text(ranking.record ?? 'No record'),
                    );
                  },
                ),
              ),
            ],
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _testFirebaseConnection,
        child: const Icon(Icons.refresh),
      ),
    );
  }
} 