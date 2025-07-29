import 'package:flutter/material.dart';
import '../models/event.dart';
import '../models/fight.dart';
import '../models/fighter.dart';
import '../models/prediction.dart';
import '../models/user_stats.dart';
import '../services/simple_database_service.dart';

class FightCardsScreen extends StatefulWidget {
  @override
  _FightCardsScreenState createState() => _FightCardsScreenState();
}

class _FightCardsScreenState extends State<FightCardsScreen>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  
  final List<String> _tabs = ['Upcoming', 'Past', 'All'];
  int _selectedTab = 0;
  
  List<Event> _events = [];
  List<Fight> _fights = [];
  Map<String, List<Fight>> _eventFights = {};
  bool _isLoading = false;
  String? _error;
  
  // Mock user ID for now
  final String _currentUserId = 'mock-user-id';

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: Duration(milliseconds: 300),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );
    _loadData();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final upcoming = _selectedTab == 0;
      print('🔍 Loading data for tab: ${_tabs[_selectedTab]} (upcoming: $upcoming)');

      // Load events
      final events = await SimpleDatabaseService.instance.getEvents();
      print('📊 Loaded ${events.length} events');

      // Load fights
      final allFights = await SimpleDatabaseService.instance.getFights();
      print('🥊 Loaded ${allFights.length} total fights');

      // Map fights to events
      final eventFights = <String, List<Fight>>{};
      for (final event in events) {
        final eventFightsList = allFights.where((fight) => fight.eventId == event.id).toList();
        eventFights[event.id] = eventFightsList;
      }

      print('📋 Event-fight mapping:');
      for (final event in events) {
        final eventFightsList = eventFights[event.id] ?? [];
        print('  ${event.title}: ${eventFightsList.length} fights');
      }

      setState(() {
        _events = events;
        _fights = allFights;
        _eventFights = eventFights;
        _isLoading = false;
      });

      _animationController.forward();
    } catch (e) {
      print('❌ Error loading data: $e');
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFF1A1A1A),
      body: Column(
        children: [
          // Custom Header
          Container(
            padding: EdgeInsets.only(top: 50, left: 20, right: 20, bottom: 20),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [Colors.red.shade900, Colors.red.shade700],
              ),
            ),
            child: Column(
              children: [
                Row(
                  children: [
                    Icon(Icons.sports_mma, color: Colors.white, size: 28),
                    SizedBox(width: 12),
                    Text(
                      'Fight Cards',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 20),
                // Tab Selector
                Container(
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(25),
                  ),
                  child: Row(
                    children: _tabs.asMap().entries.map((entry) {
                      final index = entry.key;
                      final tab = entry.value;
                      final isSelected = _selectedTab == index;
                      
                      return Expanded(
                        child: GestureDetector(
                          onTap: () {
                            setState(() {
                              _selectedTab = index;
                            });
                            _loadData();
                          },
                          child: AnimatedContainer(
                            duration: Duration(milliseconds: 200),
                            padding: EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                            decoration: BoxDecoration(
                              color: isSelected ? Colors.white : Colors.transparent,
                              borderRadius: BorderRadius.circular(25),
                            ),
                            child: Text(
                              tab,
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                color: isSelected ? Colors.red.shade900 : Colors.white,
                                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                              ),
                            ),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ],
            ),
          ),
          
          // Content
          Expanded(
            child: FadeTransition(
              opacity: _fadeAnimation,
              child: _buildFightCardsList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFightCardsList() {
    if (_isLoading) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: Colors.red.shade600),
            SizedBox(height: 16),
            Text(
              'Loading fight cards...',
              style: TextStyle(color: Colors.white70),
            ),
          ],
        ),
      );
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, color: Colors.red.shade400, size: 48),
            SizedBox(height: 16),
            Text(
              'Error loading data',
              style: TextStyle(color: Colors.white, fontSize: 18),
            ),
            SizedBox(height: 8),
            Text(
              _error!,
              style: TextStyle(color: Colors.white70),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadData,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red.shade600,
                foregroundColor: Colors.white,
              ),
              child: Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_events.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.sports_mma, color: Colors.white54, size: 64),
            SizedBox(height: 16),
            Text(
              'No events available',
              style: TextStyle(color: Colors.white, fontSize: 18),
            ),
            SizedBox(height: 8),
            Text(
              'Check back later for upcoming events',
              style: TextStyle(color: Colors.white70),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: EdgeInsets.only(bottom: 20),
      itemCount: _events.length,
      itemBuilder: (context, index) {
        final event = _events[index];
        final eventFights = _eventFights[event.id] ?? [];
        return _buildEventCard(event, eventFights);
      },
    );
  }

  Widget _buildEventCard(Event event, List<Fight> eventFights) {
    final isUpcoming = event.status == 'scheduled';
    final isMainEvent = event.type == 'numbered';
    
    return GestureDetector(
      onTap: () => _showEventDetails(event, eventFights),
      child: Container(
        margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 8,
              offset: Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          children: [
            // Event Header
            Container(
              padding: EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [Colors.red.shade900, Colors.red.shade700],
                ),
                borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
              ),
              child: Row(
                children: [
                  Icon(
                    isMainEvent ? Icons.star : Icons.sports_mma,
                    color: Colors.white,
                    size: 24,
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          event.title,
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        SizedBox(height: 4),
                        Text(
                          '${event.venue} • ${event.location}',
                          style: TextStyle(
                            color: Colors.white70,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: isUpcoming ? Colors.orange : Colors.green,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      isUpcoming ? 'UPCOMING' : 'COMPLETED',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            
            // Event Details
            Padding(
              padding: EdgeInsets.all(16),
              child: Row(
                children: [
                  Icon(Icons.calendar_today, color: Colors.red.shade600, size: 16),
                  SizedBox(width: 8),
                  Text(
                    _formatDate(event.date),
                    style: TextStyle(
                      color: Colors.grey.shade700,
                      fontSize: 14,
                    ),
                  ),
                  Spacer(),
                  Icon(Icons.sports_mma, color: Colors.red.shade600, size: 16),
                  SizedBox(width: 8),
                  Text(
                    '${eventFights.length} fights',
                    style: TextStyle(
                      color: Colors.grey.shade700,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
            
            // Preview of main fights
            if (eventFights.isNotEmpty) ...[
              Container(
                padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Column(
                  children: eventFights.take(3).map((fight) => _buildFightPreview(fight)).toList(),
                ),
              ),
            ],
            
            // Action Button
            Container(
              padding: EdgeInsets.all(16),
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () => _showEventDetails(event, eventFights),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red.shade600,
                    foregroundColor: Colors.white,
                    padding: EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: Text(
                    isUpcoming ? 'View Event & Predict' : 'View Results',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFightPreview(Fight fight) {
    final isUpcoming = fight.status == 'scheduled';
    final hasWinner = fight.winnerId != null;
    
    return Container(
      padding: EdgeInsets.symmetric(vertical: 8, horizontal: 12),
      margin: EdgeInsets.only(bottom: 4),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Expanded(
            child: Text(
              fight.fighter1?.name ?? 'TBD',
              style: TextStyle(
                color: hasWinner && fight.winnerId == fight.fighter1Id 
                    ? Colors.green.shade700 
                    : hasWinner && fight.winnerId == fight.fighter2Id 
                        ? Colors.red.shade700 
                        : Colors.grey.shade700,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Container(
            padding: EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: isUpcoming ? Colors.blue.shade100 : Colors.grey.shade200,
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              isUpcoming ? 'VS' : hasWinner ? 'W' : 'D',
              style: TextStyle(
                color: isUpcoming ? Colors.blue.shade700 : Colors.grey.shade600,
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          Expanded(
            child: Text(
              fight.fighter2?.name ?? 'TBD',
              textAlign: TextAlign.end,
              style: TextStyle(
                color: hasWinner && fight.winnerId == fight.fighter2Id 
                    ? Colors.green.shade700 
                    : hasWinner && fight.winnerId == fight.fighter1Id 
                        ? Colors.red.shade700 
                        : Colors.grey.shade700,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showEventDetails(Event event, List<Fight> eventFights) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.9,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          children: [
            // Handle
            Container(
              margin: EdgeInsets.only(top: 8),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            
            // Event Header
            Container(
              padding: EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [Colors.red.shade900, Colors.red.shade700],
                ),
              ),
              child: Column(
                children: [
                  Text(
                    event.title,
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  SizedBox(height: 8),
                  Text(
                    '${event.venue} • ${event.location}',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 16,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  SizedBox(height: 8),
                  Text(
                    _formatDate(event.date),
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
            
            // Event Stats
            Container(
              padding: EdgeInsets.all(20),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildStatCard('Total Fights', '${eventFights.length}', Icons.sports_mma),
                  _buildStatCard('Main Events', '${eventFights.where((f) => f.isMainEvent).length}', Icons.star),
                  _buildStatCard('Status', event.status.toUpperCase(), Icons.info),
                ],
              ),
            ),
            
            // Fight Card
            Expanded(
              child: Container(
                padding: EdgeInsets.symmetric(horizontal: 20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Fight Card',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey.shade800,
                      ),
                    ),
                    SizedBox(height: 16),
                    Expanded(
                      child: ListView.builder(
                        itemCount: eventFights.length,
                        itemBuilder: (context, index) {
                          return _buildEventFightCard(eventFights[index]);
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            // Make Predictions for All Fights button (if upcoming)
            if (event.status == 'scheduled')
              Container(
                padding: EdgeInsets.all(20),
                child: SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () {
                      // TODO: Implement bulk prediction
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red.shade600,
                      foregroundColor: Colors.white,
                      padding: EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    child: Text(
                      'Make Predictions for All Fights',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(icon, color: Colors.red.shade600, size: 20),
          SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
              color: Colors.grey.shade800,
            ),
          ),
          Text(
            title,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey.shade600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEventFightCard(Fight fight) {
    final isUpcoming = fight.status == 'scheduled';
    final hasWinner = fight.winnerId != null;
    
    return Container(
      margin: EdgeInsets.only(bottom: 12),
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          // Fight Header
          Row(
            children: [
              if (fight.isMainEvent)
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.red.shade600,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    'MAIN EVENT',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              if (fight.isTitleFight)
                Container(
                  margin: EdgeInsets.only(left: 8),
                  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.amber.shade600,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    'TITLE FIGHT',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              Spacer(),
              Container(
                padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: isUpcoming ? Colors.blue.shade100 : Colors.green.shade100,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  isUpcoming ? 'UPCOMING' : 'COMPLETED',
                  style: TextStyle(
                    color: isUpcoming ? Colors.blue.shade700 : Colors.green.shade700,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          
          SizedBox(height: 12),
          
          // Fighters
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      fight.fighter1?.name ?? 'TBD',
                      style: TextStyle(
                        color: hasWinner && fight.winnerId == fight.fighter1Id 
                            ? Colors.green.shade700 
                            : hasWinner && fight.winnerId == fight.fighter2Id 
                                ? Colors.red.shade700 
                                : Colors.grey.shade800,
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    if (fight.fighter1?.record != null)
                      Text(
                        fight.fighter1!.record,
                        style: TextStyle(
                          color: Colors.grey.shade600,
                          fontSize: 12,
                        ),
                      ),
                  ],
                ),
              ),
              Container(
                padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  'VS',
                  style: TextStyle(
                    color: Colors.grey.shade700,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      fight.fighter2?.name ?? 'TBD',
                      style: TextStyle(
                        color: hasWinner && fight.winnerId == fight.fighter2Id 
                            ? Colors.green.shade700 
                            : hasWinner && fight.winnerId == fight.fighter1Id 
                                ? Colors.red.shade700 
                                : Colors.grey.shade800,
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    if (fight.fighter2?.record != null)
                      Text(
                        fight.fighter2!.record,
                        style: TextStyle(
                          color: Colors.grey.shade600,
                          fontSize: 12,
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ),
          
          SizedBox(height: 12),
          
          // Weight Class
          Text(
            fight.weightClass,
            style: TextStyle(
              color: Colors.grey.shade600,
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
          ),
          
          // Result or Prediction Button
          if (isUpcoming)
            Container(
              margin: EdgeInsets.only(top: 12),
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () => _showPredictionDialog(fight),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red.shade600,
                    foregroundColor: Colors.white,
                    padding: EdgeInsets.symmetric(vertical: 8),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(6),
                    ),
                  ),
                  child: Text('Make Prediction'),
                ),
              ),
            )
          else if (hasWinner)
            Container(
              margin: EdgeInsets.only(top: 12),
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.green.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.green.shade200),
              ),
              child: Row(
                children: [
                  Icon(Icons.emoji_events, color: Colors.green.shade600, size: 16),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Winner: ${fight.winnerId == fight.fighter1Id ? fight.fighter1?.name : fight.fighter2?.name}',
                      style: TextStyle(
                        color: Colors.green.shade700,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  if (fight.method != null)
                    Text(
                      '(${fight.method})',
                      style: TextStyle(
                        color: Colors.green.shade600,
                        fontSize: 12,
                      ),
                    ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  void _showPredictionDialog(Fight fight) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Make Prediction'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Who do you think will win?'),
            SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pop(context);
                      _makePrediction(fight, fight.fighter1Id);
                    },
                    child: Text(fight.fighter1?.name ?? 'Fighter 1'),
                  ),
                ),
                SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pop(context);
                      _makePrediction(fight, fight.fighter2Id);
                    },
                    child: Text(fight.fighter2?.name ?? 'Fighter 2'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _makePrediction(Fight fight, String predictedWinnerId) async {
    try {
      await SimpleDatabaseService.instance.createPrediction(
        userId: _currentUserId,
        fightId: fight.id,
        predictedWinnerId: predictedWinnerId,
      );
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Prediction saved!'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error saving prediction: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  String _formatDate(DateTime date) {
    return '${date.month}/${date.day}/${date.year}';
  }
} 