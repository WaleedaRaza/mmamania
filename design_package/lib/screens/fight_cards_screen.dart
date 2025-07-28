import 'package:flutter/material.dart';
import '../models/fight_card.dart';
import '../models/event.dart';
import '../models/fight.dart';
import '../services/fight_card_manager.dart';
import '../widgets/fight_card_widget.dart';
import '../widgets/event_card_widget.dart';

class FightCardsScreen extends StatefulWidget {
  const FightCardsScreen({Key? key}) : super(key: key);

  @override
  State<FightCardsScreen> createState() => _FightCardsScreenState();
}

class _FightCardsScreenState extends State<FightCardsScreen>
    with TickerProviderStateMixin {
  late TabController _tabController;
  final FightCardManager _fightCardManager = FightCardManager();
  
  List<Event> _upcomingEvents = [];
  List<FightCard> _pastFightCards = [];
  List<FightCard> _searchResults = [];
  bool _isLoading = false;
  bool _isSearching = false;
  String _searchQuery = '';
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      print('🔄 Loading fight cards data...');
      
      // Clear cache to force fresh data
      await _fightCardManager.clearCache();
      print('🗑️ Cleared cache to force fresh data');
      
      // Load upcoming events with force refresh
      final upcomingEvents = await _fightCardManager.getUpcomingEvents(forceRefresh: true);
      print('📅 Loaded ${upcomingEvents.length} upcoming events');
      
      // Load past fight cards
      final pastCards = await _fightCardManager.getFightCardsByType('past');
      print('📋 Loaded ${pastCards.length} past fight cards');
      
      setState(() {
        _upcomingEvents = upcomingEvents;
        _pastFightCards = pastCards;
        _isLoading = false;
      });
      
      print('✅ Fight cards data loaded successfully');
    } catch (e) {
      print('❌ Error loading fight cards: $e');
      setState(() {
        _isLoading = false;
      });
      _showErrorSnackBar('Error loading fight cards: $e');
    }
  }

  Future<void> _searchFightCards(String query) async {
    if (query.isEmpty) {
      setState(() {
        _searchResults = [];
        _isSearching = false;
        _searchQuery = '';
      });
      return;
    }

    setState(() {
      _isSearching = true;
      _searchQuery = query;
    });

    try {
      final results = await _fightCardManager.searchFightCards(query);
      setState(() {
        _searchResults = results;
        _isSearching = false;
      });
    } catch (e) {
      setState(() {
        _isSearching = false;
      });
      _showErrorSnackBar('Error searching: $e');
    }
  }

  Future<void> _refreshData() async {
    await _loadData();
    _showSuccessSnackBar('Data refreshed');
  }

  Future<void> _checkForUpdates() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final updatedCards = await _fightCardManager.checkForUpdates();
      if (updatedCards.isNotEmpty) {
        _showSuccessSnackBar('${updatedCards.length} fight cards updated');
        await _loadData(); // Reload to show updates
      } else {
        _showSuccessSnackBar('No updates found');
      }
    } catch (e) {
      _showErrorSnackBar('Error checking for updates: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }

  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('UFC Fight Cards'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : _refreshData,
            tooltip: 'Refresh',
          ),
          IconButton(
            icon: const Icon(Icons.update),
            onPressed: _isLoading ? null : _checkForUpdates,
            tooltip: 'Check for Updates',
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Upcoming'),
            Tab(text: 'Past Events'),
            Tab(text: 'Search'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildUpcomingTab(),
          _buildPastEventsTab(),
          _buildSearchTab(),
        ],
      ),
    );
  }

  Widget _buildUpcomingTab() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_upcomingEvents.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.event_busy, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            const Text(
              'No upcoming events found',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadData,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _refreshData,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _upcomingEvents.length,
        itemBuilder: (context, index) {
          final event = _upcomingEvents[index];
          return EventCardWidget(
            event: event,
            onTap: () => _navigateToFightCard(event.id),
          );
        },
      ),
    );
  }

  Widget _buildPastEventsTab() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_pastFightCards.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.history, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            const Text(
              'No past events found',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadData,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _refreshData,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _pastFightCards.length,
        itemBuilder: (context, index) {
          final fightCard = _pastFightCards[index];
          return FightCardWidget(
            fightCard: fightCard,
            onTap: () => _navigateToFightCard(fightCard.id),
          );
        },
      ),
    );
  }

  Widget _buildSearchTab() {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: TextField(
            decoration: InputDecoration(
              hintText: 'Search fight cards...',
              prefixIcon: const Icon(Icons.search),
              suffixIcon: _searchQuery.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: () {
                        setState(() {
                          _searchQuery = '';
                          _searchResults = [];
                        });
                      },
                    )
                  : null,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            onChanged: (value) {
              _searchFightCards(value);
            },
          ),
        ),
        Expanded(
          child: _isSearching
              ? const Center(child: CircularProgressIndicator())
              : _searchResults.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.search, size: 64, color: Colors.grey),
                          const SizedBox(height: 16),
                          Text(
                            _searchQuery.isEmpty
                                ? 'Search for fight cards'
                                : 'No results found for "$_searchQuery"',
                            style: const TextStyle(fontSize: 18, color: Colors.grey),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _searchResults.length,
                      itemBuilder: (context, index) {
                        final fightCard = _searchResults[index];
                        return FightCardWidget(
                          fightCard: fightCard,
                          onTap: () => _navigateToFightCard(fightCard.id),
                        );
                      },
                    ),
        ),
      ],
    );
  }

  void _navigateToFightCard(String eventId) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => FightCardDetailScreen(eventId: eventId),
      ),
    );
  }
}

class FightCardDetailScreen extends StatefulWidget {
  final String eventId;

  const FightCardDetailScreen({Key? key, required this.eventId}) : super(key: key);

  @override
  State<FightCardDetailScreen> createState() => _FightCardDetailScreenState();
}

class _FightCardDetailScreenState extends State<FightCardDetailScreen> {
  final FightCardManager _fightCardManager = FightCardManager();
  FightCard? _fightCard;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadFightCard();
  }

  Future<void> _loadFightCard() async {
    try {
      final fightCard = await _fightCardManager.getFightCard(widget.eventId);
      setState(() {
        _fightCard = fightCard;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      _showErrorSnackBar('Error loading fight card: $e');
    }
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: const Text('Fight Card')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_fightCard == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Fight Card')),
        body: const Center(
          child: Text('Fight card not found'),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(_fightCard!.event.title),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => _loadFightCard(),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildEventInfo(),
            const SizedBox(height: 24),
            _buildFightSections(),
          ],
        ),
      ),
    );
  }

  Widget _buildEventInfo() {
    final event = _fightCard!.event;
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              event.title,
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              'Date: ${event.displayDate}',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const SizedBox(height: 4),
            Text(
              'Location: ${event.location}',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            if (event.broadcastInfo != null) ...[
              const SizedBox(height: 4),
              Text(
                'Broadcast: ${event.broadcastInfo}',
                style: Theme.of(context).textTheme.bodyLarge,
              ),
            ],
            const SizedBox(height: 8),
            Text(
              _fightCard!.summary,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFightSections() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (_fightCard!.mainCardFights.isNotEmpty) ...[
          _buildFightSection('Main Card', _fightCard!.mainCardFights),
          const SizedBox(height: 16),
        ],
        if (_fightCard!.prelimsFights.isNotEmpty) ...[
          _buildFightSection('Prelims', _fightCard!.prelimsFights),
          const SizedBox(height: 16),
        ],
        if (_fightCard!.earlyPrelimsFights.isNotEmpty) ...[
          _buildFightSection('Early Prelims', _fightCard!.earlyPrelimsFights),
        ],
      ],
    );
  }

  Widget _buildFightSection(String title, List<Fight> fights) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        ...fights.map((fight) => _buildFightCard(fight)),
      ],
    );
  }

  Widget _buildFightCard(Fight fight) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    fight.weightClass ?? 'Unknown',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.grey[600],
                    ),
                  ),
                ),
                if (fight.fightOrder != null)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.blue,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      'Fight ${fight.fightOrder}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: Text(
                    fight.fighter1,
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const Text('vs', style: TextStyle(color: Colors.grey)),
                Expanded(
                  child: Text(
                    fight.fighter2,
                    textAlign: TextAlign.end,
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                Expanded(
                  child: Text(
                    fight.fighter1RecordString,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ),
                Expanded(
                  child: Text(
                    fight.fighter2RecordString,
                    textAlign: TextAlign.end,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ),
              ],
            ),
            if (fight.isCompleted) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.green[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  fight.resultSummary,
                  style: TextStyle(
                    color: Colors.green[800],
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
            if (fight.oddsDisplay.isNotEmpty && fight.oddsDisplay != 'Odds not available') ...[
              const SizedBox(height: 8),
              Text(
                'Odds: ${fight.oddsDisplay}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.orange[700],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
} 