import 'package:flutter/material.dart';
import '../models/fighter.dart';
import '../models/ranking_item.dart';
import '../services/simple_database_service.dart';

class RankingsScreen extends StatefulWidget {
  const RankingsScreen({super.key});

  @override
  _RankingsScreenState createState() => _RankingsScreenState();
}

class _RankingsScreenState extends State<RankingsScreen> with TickerProviderStateMixin {
  int _selectedWeightClass = 0;
  List<RankingItem> _rankings = [];
  bool _isLoading = false;
  String? _error;
  late AnimationController _animationController;
  late Animation<double> _slideAnimation;
  
  final List<String> _weightClasses = [
    'Men\'s Pound-for-PoundTop Rank',
    'Flyweight',
    'Bantamweight',
    'Featherweight',
    'Lightweight',
    'Welterweight',
    'Middleweight',
    'Light Heavyweight',
    'Heavyweight',
  ];

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    _slideAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeOutBack),
    );
    _loadRankings();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _loadRankings() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final weightClass = _weightClasses[_selectedWeightClass];
      print('🔍 Loading rankings for weight class: $weightClass');
      
      final rankings = await SimpleDatabaseService.instance.getRankingItems(weightClass);
      print('📊 Found ${rankings.length} rankings');
      
      setState(() {
        _rankings = rankings;
        _isLoading = false;
      });
      _animationController.forward();
    } catch (e) {
      print('❌ Error loading rankings: $e');
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
                          Icons.sports_martial_arts,
                          color: Colors.white,
                          size: 32,
                        ),
                        const SizedBox(width: 12),
                        Text(
                          'UFC Rankings',
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
                      'Official UFC Fighter Rankings',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
              ),
              
              // Weight Class Selector
              Container(
                height: 60,
                margin: const EdgeInsets.symmetric(horizontal: 16),
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: _weightClasses.length,
                  itemBuilder: (context, index) {
                    return Container(
                      margin: const EdgeInsets.only(right: 12),
                      child: GestureDetector(
                        onTap: () {
                          setState(() {
                            _selectedWeightClass = index;
                          });
                          _loadRankings();
                        },
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                          decoration: BoxDecoration(
                            gradient: _selectedWeightClass == index
                                ? LinearGradient(
                                    colors: [Colors.white, Colors.white.withOpacity(0.9)],
                                  )
                                : LinearGradient(
                                    colors: [
                                      Colors.white.withOpacity(0.2),
                                      Colors.white.withOpacity(0.1),
                                    ],
                                  ),
                            borderRadius: BorderRadius.circular(25),
                            border: Border.all(
                              color: _selectedWeightClass == index
                                  ? Colors.white
                                  : Colors.white.withOpacity(0.3),
                              width: 1,
                            ),
                          ),
                          child: Text(
                            _weightClasses[index],
                            style: TextStyle(
                              color: _selectedWeightClass == index
                                  ? Colors.red.shade900
                                  : Colors.white,
                              fontWeight: _selectedWeightClass == index
                                  ? FontWeight.bold
                                  : FontWeight.normal,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
              
              const SizedBox(height: 20),
              
              // Rankings List
              Expanded(
                child: Container(
                  margin: const EdgeInsets.symmetric(horizontal: 16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.3),
                        blurRadius: 10,
                        offset: const Offset(0, 5),
                      ),
                    ],
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: _buildRankingsList(),
                  ),
                ),
              ),
              
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRankingsList() {
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
              'Loading rankings...',
              style: TextStyle(
                color: Colors.grey.shade600,
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
              'Error loading rankings',
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
                color: Colors.grey.shade600,
                fontSize: 14,
              ),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadRankings,
              child: Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_rankings.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.sports_martial_arts,
              color: Colors.grey.shade400,
              size: 48,
            ),
            SizedBox(height: 16),
            Text(
              'No rankings found',
              style: TextStyle(
                color: Colors.grey.shade600,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 8),
            Text(
              'Try running the data pipeline first',
              style: TextStyle(
                color: Colors.grey.shade500,
                fontSize: 14,
              ),
            ),
          ],
        ),
      );
    }

    return SlideTransition(
      position: Tween<Offset>(
        begin: const Offset(0, 0.3),
        end: Offset.zero,
      ).animate(_slideAnimation),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _rankings.length,
        itemBuilder: (context, index) {
          return _buildRankingItem(index, _rankings[index]);
        },
      ),
    );
  }

  Widget _buildRankingItem(int index, RankingItem rankingItem) {
    bool isChampion = rankingItem.isChampion;
    bool isTop5 = rankingItem.rankPosition <= 5;
    
    // Determine display rank
    String displayRank;
    if (isChampion) {
      displayRank = 'C';
    } else {
      // For contenders, show their actual rank position
      displayRank = '${rankingItem.rankPosition}';
    }
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        gradient: isChampion
            ? LinearGradient(
                colors: [Colors.amber.shade400, Colors.amber.shade600],
              )
            : isTop5
                ? LinearGradient(
                    colors: [Colors.red.shade50, Colors.red.shade100],
                  )
                : LinearGradient(
                    colors: [Colors.grey.shade50, Colors.grey.shade100],
                  ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isChampion
              ? Colors.amber.shade600
              : isTop5
                  ? Colors.red.shade200
                  : Colors.grey.shade300,
          width: 1,
        ),
      ),
      child: ListTile(
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: isChampion
                ? Colors.amber.shade600
                : isTop5
                    ? Colors.red.shade600
                    : Colors.grey.shade600,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Center(
            child: Text(
              displayRank,
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
          ),
        ),
        title: Text(
          rankingItem.fighter.name,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: isChampion
                ? Colors.amber.shade900
                : isTop5
                    ? Colors.red.shade900
                    : Colors.grey.shade800,
          ),
        ),
        subtitle: Text(
          rankingItem.fighter.record ?? 'Record not available',
          style: TextStyle(
            color: Colors.grey.shade600,
          ),
        ),
        trailing: isChampion
            ? Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.amber.shade600,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  'CHAMPION',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 10,
                  ),
                ),
              )
            : null,
      ),
    );
  }
} 