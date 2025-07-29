import 'package:flutter/material.dart';
import '../models/fight.dart';
import '../models/event.dart';
import '../models/fighter.dart';
import '../models/prediction.dart';
import '../models/user_stats.dart';
import '../services/simple_database_service.dart';

class FightCardsScreen extends StatefulWidget {
  const FightCardsScreen({super.key});

  @override
  _FightCardsScreenState createState() => _FightCardsScreenState();
}

class _FightCardsScreenState extends State<FightCardsScreen> with TickerProviderStateMixin {
  int _selectedTab = 0;
  final List<String> _tabs = ['Upcoming', 'Past', 'All'];
  List<Event> _events = [];
  List<Fight> _fights = [];
  Map<String, List<Fight>> _eventFights = {};
  bool _isLoading = false;
  String? _error;
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  
  // Mock user ID for now - in real app this would come from auth
  final String _currentUserId = 'user_123';

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
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
      
      // Load events first
      final events = await SimpleDatabaseService.instance.getEvents(upcoming: upcoming);
      print('📊 Loaded ${events.length} events');
      
      // Group fights by event
      final allFights = await SimpleDatabaseService.instance.getFights(upcoming: upcoming);
      print('🥊 Loaded ${allFights.length} total fights');
      
      // Create event-fight mapping
      final Map<String, List<Fight>> eventFights = {};
      for (final fight in allFights) {
        if (fight.eventId != null) {
          eventFights.putIfAbsent(fight.eventId, () => []).add(fight);
        }
      }
      
      // Debug: Print event-fight mapping
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
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.red.shade900,
              Colors.red.shade800,
              Colors.black,
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header Section
              Container(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.sports_mma,
                          color: Colors.white,
                          size: 32,
                        ),
                        const SizedBox(width: 12),
                        Text(
                          'Fight Cards',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Latest UFC Events & Fights',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
              ),
              
              // Tab Selector
              Container(
                margin: const EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(25),
                ),
                child: Row(
                  children: _tabs.asMap().entries.map((entry) {
                    int index = entry.key;
                    String tab = entry.value;
                    bool isSelected = _selectedTab == index;
                    
                    return Expanded(
                      child: GestureDetector(
                        onTap: () {
                          setState(() {
                            _selectedTab = index;
                          });
                          _loadData();
                        },
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          decoration: BoxDecoration(
                            gradient: isSelected
                                ? LinearGradient(
                                    colors: [Colors.white, Colors.white.withOpacity(0.9)],
                                  )
                                : null,
                            borderRadius: BorderRadius.circular(25),
                          ),
                          child: Text(
                            tab,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: isSelected
                                  ? Colors.red.shade900
                                  : Colors.white,
                              fontWeight: isSelected
                                  ? FontWeight.bold
                                  : FontWeight.normal,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),
              
              const SizedBox(height: 20),
              
              // Fight Cards List
              Expanded(
                child: Container(
                  margin: const EdgeInsets.symmetric(horizontal: 16),
                  child: _buildFightCardsList(),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFightCardsList() {
    if (_isLoading) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.red.shade600),
            ),
            SizedBox(height: 16),
            Text(
              'Loading fight cards...',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
              ),
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
            Icon(
              Icons.error_outline,
              color: Colors.red.shade600,
              size: 48,
            ),
            SizedBox(height: 16),
            Text(
              'Error loading fight cards',
              style: TextStyle(
                color: Colors.red.shade600,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 8),
            Text(
              _error!,
              style: TextStyle(
                color: Colors.white70,
                fontSize: 14,
              ),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadData,
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
            Icon(
              Icons.sports_mma,
              color: Colors.grey.shade400,
              size: 48,
            ),
            SizedBox(height: 16),
            Text(
              'No events available',
              style: TextStyle(
                color: Colors.grey.shade600,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 8),
            Text(
              'Check back later for upcoming events',
              style: TextStyle(
                color: Colors.grey.shade500,
                fontSize: 14,
              ),
            ),
          ],
        ),
      );
    }

    return FadeTransition(
      opacity: _fadeAnimation,
      child: ListView.builder(
        padding: const EdgeInsets.only(bottom: 20),
        itemCount: _events.length,
        itemBuilder: (context, index) {
          final event = _events[index];
          final eventFights = _eventFights[event.id] ?? [];
          return _buildEventCard(event, eventFights);
        },
      ),
    );
  }

  Widget _buildEventCard(Event event, List<Fight> eventFights) {
    final isUpcoming = event.status == 'scheduled';
    final isMainEvent = event.type == 'numbered';
    
    return GestureDetector(
      onTap: () => _showEventDetails(event, eventFights),
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.white,
              Colors.grey.shade50,
            ],
          ),
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.2),
              blurRadius: 10,
              offset: const Offset(0, 5),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: Column(
            children: [
              // Event Header
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: isMainEvent
                        ? [Colors.red.shade600, Colors.red.shade800]
                        : [Colors.grey.shade600, Colors.grey.shade800],
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      isUpcoming ? Icons.schedule : Icons.history,
                      color: Colors.white,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            event.title,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '${event.venue} • ${event.location}',
                            style: TextStyle(
                              color: Colors.white70,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: isUpcoming ? Colors.orange : Colors.green,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        isUpcoming ? 'UPCOMING' : 'COMPLETED',
                        style: const TextStyle(
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
              Container(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    // Event Info
                    Row(
                      children: [
                        Icon(
                          Icons.calendar_today,
                          color: Colors.grey.shade600,
                          size: 16,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          event.date.toString().split(' ')[0],
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey.shade700,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        const Spacer(),
                        Text(
                          '${eventFights.length} fights',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey.shade600,
                          ),
                        ),
                      ],
                    ),
                    
                    const SizedBox(height: 12),
                    
                    // Preview of main fights
                    if (eventFights.isNotEmpty) ...[
                      ...eventFights.take(3).map((fight) => _buildFightPreview(fight)),
                      if (eventFights.length > 3)
                        Padding(
                          padding: const EdgeInsets.only(top: 8),
                          child: Text(
                            '+${eventFights.length - 3} more fights',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey.shade600,
                              fontStyle: FontStyle.italic,
                            ),
                          ),
                        ),
                    ] else
                      Padding(
                        padding: const EdgeInsets.all(16),
                        child: Text(
                          'No fights available for this event',
                          style: TextStyle(
                            color: Colors.grey.shade500,
                            fontSize: 14,
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                      ),
                    
                    const SizedBox(height: 12),
                    
                    // Action Button
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: () => _showEventDetails(event, eventFights),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.red.shade600,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        child: Text(
                          isUpcoming ? 'View Event & Predict' : 'View Results',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildFightPreview(Fight fight) {
    final isUpcoming = fight.status == 'scheduled';
    final hasWinner = fight.winnerId != null;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Row(
        children: [
          Expanded(
            child: Text(
              fight.fighter1?.name ?? 'TBD',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: hasWinner && fight.winnerId == fight.fighter1Id 
                    ? Colors.green.shade700 
                    : Colors.grey.shade800,
              ),
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: isUpcoming ? Colors.orange.shade100 : Colors.grey.shade200,
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              isUpcoming ? 'VS' : (hasWinner ? 'W' : 'D'),
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.bold,
                color: isUpcoming ? Colors.orange.shade700 : Colors.grey.shade600,
              ),
            ),
          ),
          Expanded(
            child: Text(
              fight.fighter2?.name ?? 'TBD',
              textAlign: TextAlign.end,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: hasWinner && fight.winnerId == fight.fighter2Id 
                    ? Colors.green.shade700 
                    : Colors.grey.shade800,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFightCard(Fight fight) {
    final isUpcoming = fight.status == 'scheduled';
    final isMainEvent = fight.isMainEvent;
    
    return GestureDetector(
      onTap: () => _showFightDetails(fight),
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.white,
              Colors.grey.shade50,
            ],
          ),
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.2),
              blurRadius: 10,
              offset: const Offset(0, 5),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: Column(
            children: [
              // Event Header
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: isMainEvent
                        ? [Colors.red.shade600, Colors.red.shade800]
                        : [Colors.grey.shade600, Colors.grey.shade800],
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      isUpcoming ? Icons.schedule : Icons.history,
                      color: Colors.white,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            fight.weightClass,
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                          Text(
                            fight.date != null 
                                ? '${fight.date!.day}/${fight.date!.month}/${fight.date!.year}'
                                : 'Date TBD',
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.8),
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: isUpcoming
                            ? Colors.blue.withOpacity(0.2)
                            : Colors.green.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: isUpcoming ? Colors.blue : Colors.green,
                        ),
                      ),
                      child: Text(
                        isUpcoming ? 'UPCOMING' : 'COMPLETED',
                        style: TextStyle(
                          color: isUpcoming ? Colors.blue : Colors.green,
                          fontWeight: FontWeight.bold,
                          fontSize: 10,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              
              // Fight Details
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    // Main Event Badge
                    if (isMainEvent) ...[
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [Colors.amber.shade50, Colors.amber.shade100],
                          ),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.amber.shade300),
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.star, color: Colors.amber.shade600, size: 20),
                            const SizedBox(width: 8),
                            Text(
                              'MAIN EVENT',
                              style: TextStyle(
                                color: Colors.amber.shade800,
                                fontWeight: FontWeight.bold,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 12),
                    ],
                    
                    // Fighter vs Fighter
                    Row(
                      children: [
                        Expanded(
                          child: Column(
                            children: [
                              CircleAvatar(
                                radius: 30,
                                backgroundColor: Colors.red.shade100,
                                child: Icon(Icons.person, color: Colors.red.shade600, size: 30),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                fight.fighter1?.name ?? 'TBD',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                ),
                                textAlign: TextAlign.center,
                              ),
                              Text(
                                fight.fighter1?.record ?? 'Record N/A',
                                style: TextStyle(
                                  color: Colors.grey.shade600,
                                  fontSize: 12,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                          ),
                        ),
                        
                        // VS
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          decoration: BoxDecoration(
                            color: Colors.red.shade600,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            'VS',
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                            ),
                          ),
                        ),
                        
                        Expanded(
                          child: Column(
                            children: [
                              CircleAvatar(
                                radius: 30,
                                backgroundColor: Colors.blue.shade100,
                                child: Icon(Icons.person, color: Colors.blue.shade600, size: 30),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                fight.fighter2?.name ?? 'TBD',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                ),
                                textAlign: TextAlign.center,
                              ),
                              Text(
                                fight.fighter2?.record ?? 'Record N/A',
                                style: TextStyle(
                                  color: Colors.grey.shade600,
                                  fontSize: 12,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // Prediction Button for upcoming fights
                    if (isUpcoming) ...[
                      ElevatedButton(
                        onPressed: () => _showPredictionDialog(fight),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.red.shade600,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(25),
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.psychology, size: 20),
                            const SizedBox(width: 8),
                            Text('Make Prediction'),
                          ],
                        ),
                      ),
                    ],
                    
                    // Result for completed fights
                    if (!isUpcoming && fight.winnerId != null) ...[
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.green.shade100,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.green.shade300),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.check_circle, color: Colors.green.shade600, size: 16),
                            const SizedBox(width: 4),
                            Text(
                              'Winner: ${fight.winnerId == fight.fighter1Id ? fight.fighter1?.name : fight.fighter2?.name}',
                              style: TextStyle(
                                color: Colors.green.shade800,
                                fontWeight: FontWeight.bold,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showFightDetails(Fight fight) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.8,
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
            
            Expanded(
              child: SingleChildScrollView(
                padding: EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Fight Details',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 20),
                    
                    // Fighters
                    Row(
                      children: [
                        Expanded(
                          child: _buildFighterCard(fight.fighter1, 'Fighter 1'),
                        ),
                        SizedBox(width: 16),
                        Expanded(
                          child: _buildFighterCard(fight.fighter2, 'Fighter 2'),
                        ),
                      ],
                    ),
                    
                    SizedBox(height: 20),
                    
                    // Fight Info
                    _buildInfoRow('Weight Class', fight.weightClass),
                    _buildInfoRow('Rounds', '${fight.rounds}'),
                    _buildInfoRow('Status', fight.status),
                    if (fight.date != null)
                      _buildInfoRow('Date', '${fight.date!.day}/${fight.date!.month}/${fight.date!.year}'),
                    if (fight.isMainEvent)
                      _buildInfoRow('Type', 'Main Event'),
                    if (fight.isTitleFight)
                      _buildInfoRow('Type', 'Title Fight'),
                    
                    if (fight.winnerId != null) ...[
                      SizedBox(height: 20),
                      Container(
                        padding: EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.green.shade50,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.green.shade200),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Result',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                            SizedBox(height: 8),
                            _buildInfoRow('Winner', fight.winnerId == fight.fighter1Id ? fight.fighter1?.name : fight.fighter2?.name),
                            if (fight.method != null)
                              _buildInfoRow('Method', fight.method!),
                            if (fight.round != null)
                              _buildInfoRow('Round', '${fight.round}'),
                            if (fight.time != null)
                              _buildInfoRow('Time', fight.time!),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFighterCard(Fighter? fighter, String label) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        children: [
          CircleAvatar(
            radius: 30,
            backgroundColor: Colors.grey.shade300,
            child: Icon(Icons.person, color: Colors.grey.shade600, size: 30),
          ),
          SizedBox(height: 8),
          Text(
            label,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 12,
              color: Colors.grey.shade600,
            ),
          ),
          SizedBox(height: 4),
          Text(
            fighter?.name ?? 'TBD',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 14,
            ),
            textAlign: TextAlign.center,
          ),
          if (fighter?.record != null) ...[
            SizedBox(height: 4),
            Text(
              fighter!.record!,
              style: TextStyle(
                color: Colors.grey.shade600,
                fontSize: 12,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String? value) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Text(
            '$label:',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: Colors.grey.shade700,
            ),
          ),
          SizedBox(width: 8),
          Text(
            value ?? 'N/A',
            style: TextStyle(
              color: Colors.grey.shade800,
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
            
            Expanded(
              child: SingleChildScrollView(
                padding: EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Event Header
                    Container(
                      padding: EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [Colors.red.shade600, Colors.red.shade800],
                        ),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            event.title,
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          SizedBox(height: 8),
                          Text(
                            '${event.venue} • ${event.location}',
                            style: TextStyle(
                              color: Colors.white70,
                              fontSize: 14,
                            ),
                          ),
                          SizedBox(height: 4),
                          Text(
                            event.date.toString().split(' ')[0],
                            style: TextStyle(
                              color: Colors.white70,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                    
                    SizedBox(height: 20),
                    
                    // Event Stats
                    Row(
                      children: [
                        Expanded(
                          child: _buildStatCard('Total Fights', '${eventFights.length}', Icons.sports_mma),
                        ),
                        SizedBox(width: 12),
                        Expanded(
                          child: _buildStatCard('Main Events', '${eventFights.where((f) => f.isMainEvent).length}', Icons.star),
                        ),
                        SizedBox(width: 12),
                        Expanded(
                          child: _buildStatCard('Status', event.status, Icons.info),
                        ),
                      ],
                    ),
                    
                    SizedBox(height: 20),
                    
                    // Fights List
                    Text(
                      'Fight Card',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 12),
                    
                    ...eventFights.map((fight) => _buildEventFightCard(fight)),
                    
                    if (event.status == 'scheduled') ...[
                      SizedBox(height: 20),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: () {
                            Navigator.pop(context);
                            // TODO: Navigate to prediction screen
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
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ],
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
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
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
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
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
                    color: Colors.amber.shade100,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    'MAIN EVENT',
                    style: TextStyle(
                      color: Colors.amber.shade800,
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
                    color: Colors.purple.shade100,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    'TITLE FIGHT',
                    style: TextStyle(
                      color: Colors.purple.shade800,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              Spacer(),
              Container(
                padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: isUpcoming ? Colors.orange.shade100 : Colors.green.shade100,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  isUpcoming ? 'UPCOMING' : 'COMPLETED',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: isUpcoming ? Colors.orange.shade700 : Colors.green.shade700,
                  ),
                ),
              ),
            ],
          ),
          
          SizedBox(height: 8),
          
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
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                        color: hasWinner && fight.winnerId == fight.fighter1Id 
                            ? Colors.green.shade700 
                            : Colors.grey.shade800,
                      ),
                    ),
                    Text(
                      fight.fighter1?.record ?? '0-0-0',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.red.shade100,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  'VS',
                  style: TextStyle(
                    color: Colors.red.shade700,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
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
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                        color: hasWinner && fight.winnerId == fight.fighter2Id 
                            ? Colors.green.shade700 
                            : Colors.grey.shade800,
                      ),
                    ),
                    Text(
                      fight.fighter2?.record ?? '0-0-0',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          
          SizedBox(height: 8),
          
          // Weight Class
          Text(
            fight.weightClass,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey.shade600,
              fontStyle: FontStyle.italic,
            ),
          ),
          
          // Result or Prediction Button
          if (hasWinner) ...[
            SizedBox(height: 8),
            Container(
              padding: EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.green.shade50,
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: Colors.green.shade200),
              ),
              child: Row(
                children: [
                  Icon(Icons.check_circle, color: Colors.green.shade600, size: 16),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Winner: ${fight.winnerId == fight.fighter1Id ? fight.fighter1?.name : fight.fighter2?.name}',
                      style: TextStyle(
                        color: Colors.green.shade700,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                  if (fight.method != null && fight.method!.isNotEmpty)
                    Text(
                      '(${fight.method})',
                      style: TextStyle(
                        color: Colors.green.shade600,
                        fontSize: 10,
                      ),
                    ),
                ],
              ),
            ),
          ] else if (isUpcoming) ...[
            SizedBox(height: 8),
            SizedBox(
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
                child: Text(
                  'Make Prediction',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
            ),
          ],
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
            SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: () => _makePrediction(fight, fight.fighter1Id!),
                    child: Text(fight.fighter1?.name ?? 'Fighter 1'),
                  ),
                ),
                SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () => _makePrediction(fight, fight.fighter2Id!),
                    child: Text(fight.fighter2?.name ?? 'Fighter 2'),
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text('Cancel'),
          ),
        ],
      ),
    );
  }

  Future<void> _makePrediction(Fight fight, String predictedWinnerId) async {
    try {
      final prediction = await SimpleDatabaseService.instance.createPrediction(
        userId: _currentUserId,
        fightId: fight.id,
        predictedWinnerId: predictedWinnerId,
      );

      if (prediction != null) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Prediction recorded!'),
            backgroundColor: Colors.green,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to record prediction'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
} 