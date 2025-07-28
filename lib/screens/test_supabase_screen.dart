import 'package:flutter/material.dart';
import '../services/simple_database_service.dart';
import '../models/fighter.dart';
import '../models/fight.dart';
import '../models/event.dart';

class TestSupabaseScreen extends StatefulWidget {
  @override
  _TestSupabaseScreenState createState() => _TestSupabaseScreenState();
}

class _TestSupabaseScreenState extends State<TestSupabaseScreen> {
  List<Fighter> fighters = [];
  List<Fight> fights = [];
  List<Event> events = [];
  bool isLoading = true;
  String error = '';
  String currentTest = '';

  @override
  void initState() {
    super.initState();
    _runTests();
  }

  Future<void> _runTests() async {
    setState(() {
      isLoading = true;
      error = '';
    });

    try {
      // Test 1: Load fighters
      setState(() => currentTest = 'Testing fighters...');
      final fightersList = await SimpleDatabaseService.instance.getFighters(limit: 5);
      setState(() => fighters = fightersList);

      // Test 2: Load fights
      setState(() => currentTest = 'Testing fights...');
      final fightsList = await SimpleDatabaseService.instance.getFights(limit: 5);
      setState(() => fights = fightsList);

      // Test 3: Load events
      setState(() => currentTest = 'Testing events...');
      final eventsList = await SimpleDatabaseService.instance.getEvents(limit: 5);
      setState(() => events = eventsList);

      setState(() {
        isLoading = false;
        currentTest = 'All tests completed!';
      });
    } catch (e) {
      setState(() {
        error = e.toString();
        isLoading = false;
        currentTest = 'Test failed';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Supabase Connection Test'),
        backgroundColor: Colors.deepPurple,
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _runTests,
          ),
        ],
      ),
      body: isLoading
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text(currentTest),
                ],
              ),
            )
          : error.isNotEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.error, color: Colors.red, size: 64),
                      SizedBox(height: 16),
                      Text(
                        'Connection Error',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 8),
                      Text(
                        error,
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.red),
                      ),
                      SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _runTests,
                        child: Text('Retry'),
                      ),
                    ],
                  ),
                )
              : SingleChildScrollView(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Success Header
                      Container(
                        width: double.infinity,
                        padding: EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [Colors.green, Colors.greenAccent],
                          ),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Column(
                          children: [
                            Icon(Icons.check_circle, color: Colors.white, size: 48),
                            SizedBox(height: 8),
                            Text(
                              'Supabase Connection Successful!',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            SizedBox(height: 4),
                            Text(
                              currentTest,
                              style: TextStyle(color: Colors.white70),
                            ),
                          ],
                        ),
                      ),
                      SizedBox(height: 24),

                      // Test Results
                      _buildTestSection(
                        'Fighters Test',
                        fighters.length,
                        fighters.take(3).map((f) => '${f.name} (${f.weightClass ?? 'Unknown'})').toList(),
                        Icons.person,
                      ),
                      SizedBox(height: 16),

                      _buildTestSection(
                        'Fights Test',
                        fights.length,
                        fights.take(3).map((f) => '${f.fighter1?.name ?? 'Unknown'} vs ${f.fighter2?.name ?? 'Unknown'}').toList(),
                        Icons.sports_martial_arts,
                      ),
                      SizedBox(height: 16),

                      _buildTestSection(
                        'Events Test',
                        events.length,
                        events.take(3).map((e) => '${e.name} (${e.date?.toString().substring(0, 10) ?? 'No date'})').toList(),
                        Icons.event,
                      ),
                      SizedBox(height: 24),

                      // Connection Info
                      Card(
                        child: Padding(
                          padding: EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Connection Information',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              SizedBox(height: 8),
                              Text('Total Fighters: ${fighters.length}'),
                              Text('Total Fights: ${fights.length}'),
                              Text('Total Events: ${events.length}'),
                            ],
                          ),
                        ),
                      ),
                      SizedBox(height: 16),

                      // Next Steps
                      Card(
                        child: Padding(
                          padding: EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Next Steps',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              SizedBox(height: 8),
                              Text('• Navigate to other screens to test full functionality'),
                              Text('• Check real-time updates by modifying data in Supabase'),
                              Text('• Test offline functionality'),
                              Text('• Verify all CRUD operations work'),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
    );
  }

  Widget _buildTestSection(String title, int count, List<String> examples, IconData icon) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: Colors.deepPurple),
                SizedBox(width: 8),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Spacer(),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.green,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '$count items',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            SizedBox(height: 8),
            if (examples.isNotEmpty) ...[
              Text(
                'Examples:',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
              SizedBox(height: 4),
              ...examples.map((example) => Text(
                '• $example',
                style: TextStyle(fontSize: 12),
              )),
            ],
          ],
        ),
      ),
    );
  }
} 