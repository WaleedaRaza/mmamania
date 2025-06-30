import 'package:flutter/material.dart';
import '../services/ufc_data_service.dart';
import '../models/fighter.dart';
import '../models/ranking.dart';

class StatsScreen extends StatefulWidget {
  @override
  _StatsScreenState createState() => _StatsScreenState();
}

class _StatsScreenState extends State<StatsScreen> with TickerProviderStateMixin {
  final UFCDataService _ufcDataService = UFCDataService();
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    await _ufcDataService.loadData();
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFF1A1A1A),
      appBar: AppBar(
        title: Text('UFC Statistics', style: TextStyle(color: Colors.white)),
        backgroundColor: Color(0xFF2D2D2D),
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.red,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.grey[400],
          tabs: [
            Tab(text: 'Overview'),
            Tab(text: 'Fighters'),
            Tab(text: 'Divisions'),
            Tab(text: 'Records'),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: () async {
              await _loadData();
            },
          ),
        ],
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildOverviewTab(),
          _buildFightersTab(),
          _buildDivisionsTab(),
          _buildRecordsTab(),
        ],
      ),
    );
  }

  Widget _buildOverviewTab() {
    final allFighters = _ufcDataService.getAllFighters();
    final allRankings = _ufcDataService.getAllRankings();
    final divisions = _ufcDataService.getDivisions();

    // Calculate statistics
    final totalFights = allFighters.fold<int>(0, (sum, fighter) => 
        sum + fighter.record.wins + fighter.record.losses + fighter.record.draws);
    
    final totalWins = allFighters.fold<int>(0, (sum, fighter) => sum + fighter.record.wins);
    final totalLosses = allFighters.fold<int>(0, (sum, fighter) => sum + fighter.record.losses);
    final totalDraws = allFighters.fold<int>(0, (sum, fighter) => sum + fighter.record.draws);
    
    final winRate = totalFights > 0 ? (totalWins / totalFights * 100) : 0.0;
    
    // Find top performers
    final topWinRate = allFighters
        .where((f) => f.record.wins + f.record.losses + f.record.draws >= 5)
        .toList()
      ..sort((a, b) {
        final aRate = (a.record.wins / (a.record.wins + a.record.losses + a.record.draws));
        final bRate = (b.record.wins / (b.record.wins + b.record.losses + b.record.draws));
        return bRate.compareTo(aRate);
      });

    return SingleChildScrollView(
      padding: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildOverviewCards(allFighters.length, allRankings.length, divisions.length, totalFights),
          SizedBox(height: 24),
          _buildWinRateCard(winRate, totalWins, totalLosses, totalDraws),
          SizedBox(height: 24),
          _buildTopPerformersCard(topWinRate.take(5).toList()),
          SizedBox(height: 24),
          _buildDivisionBreakdownCard(divisions),
        ],
      ),
    );
  }

  Widget _buildOverviewCards(int fighters, int rankings, int divisions, int totalFights) {
    return Row(
      children: [
        Expanded(child: _buildStatCard('Fighters', fighters.toString(), Icons.person)),
        SizedBox(width: 12),
        Expanded(child: _buildStatCard('Rankings', rankings.toString(), Icons.leaderboard)),
        SizedBox(width: 12),
        Expanded(child: _buildStatCard('Divisions', divisions.toString(), Icons.category)),
        SizedBox(width: 12),
        Expanded(child: _buildStatCard('Total Fights', totalFights.toString(), Icons.sports_mma)),
      ],
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Color(0xFF3D3D3D), Color(0xFF2D2D2D)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.red.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: Colors.red, size: 24),
          SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[400],
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildWinRateCard(double winRate, int wins, int losses, int draws) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.trending_up, color: Colors.red),
                SizedBox(width: 8),
                Text(
                  'Overall Win Rate',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
            SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: Column(
                    children: [
                      Text(
                        '${winRate.toStringAsFixed(1)}%',
                        style: TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: Colors.red,
                        ),
                      ),
                      Text(
                        'Win Rate',
                        style: TextStyle(color: Colors.grey[400]),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    children: [
                      Text(
                        '$wins',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.green,
                        ),
                      ),
                      Text('Wins', style: TextStyle(color: Colors.grey[400])),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    children: [
                      Text(
                        '$losses',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.orange,
                        ),
                      ),
                      Text('Losses', style: TextStyle(color: Colors.grey[400])),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    children: [
                      Text(
                        '$draws',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.blue,
                        ),
                      ),
                      Text('Draws', style: TextStyle(color: Colors.grey[400])),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTopPerformersCard(List<Fighter> topPerformers) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.star, color: Colors.yellow),
                SizedBox(width: 8),
                Text(
                  'Top Performers (Win Rate)',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
            SizedBox(height: 16),
            ...topPerformers.map((fighter) {
              final totalFights = fighter.record.wins + fighter.record.losses + fighter.record.draws;
              final winRate = totalFights > 0 ? (fighter.record.wins / totalFights * 100) : 0.0;
              
              return ListTile(
                leading: CircleAvatar(
                  backgroundColor: Colors.red,
                  child: Text(
                    fighter.name.split(' ').last[0],
                    style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                ),
                title: Text(
                  fighter.name,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                subtitle: Text(
                  '${fighter.record.wins}-${fighter.record.losses}-${fighter.record.draws}',
                  style: TextStyle(color: Colors.grey[400]),
                ),
                trailing: Container(
                  padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: Colors.green),
                  ),
                  child: Text(
                    '${winRate.toStringAsFixed(1)}%',
                    style: TextStyle(
                      color: Colors.green,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildDivisionBreakdownCard(List<String> divisions) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.category, color: Colors.red),
                SizedBox(width: 8),
                Text(
                  'Division Breakdown',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
            SizedBox(height: 16),
            ...divisions.map((division) {
              final rankings = _ufcDataService.getRankingsForDivision(division);
              final champion = _ufcDataService.getChampionForDivision(division);
              
              // Calculate division statistics
              final fighters = rankings.map((r) => _ufcDataService.getFighterByRanking(r)).where((f) => f != null).cast<Fighter>().toList();
              final totalFights = fighters.fold<int>(0, (sum, f) => 
                  sum + f.record.wins + f.record.losses + f.record.draws);
              final totalWins = fighters.fold<int>(0, (sum, f) => sum + f.record.wins);
              final winRate = totalFights > 0 ? (totalWins / totalFights * 100) : 0.0;
              
              return ListTile(
                leading: CircleAvatar(
                  backgroundColor: Colors.red.withOpacity(0.3),
                  child: Icon(Icons.sports_mma, color: Colors.red),
                ),
                title: Text(
                  division,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                subtitle: Text(
                  champion != null 
                      ? 'Champion: ${champion.fighterName}'
                      : '${rankings.length} ranked fighters',
                  style: TextStyle(color: Colors.grey[400]),
                ),
                trailing: Container(
                  padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.red.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: Colors.red),
                  ),
                  child: Text(
                    '${rankings.length}',
                    style: TextStyle(
                      color: Colors.red,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildFightersTab() {
    final allFighters = _ufcDataService.getAllFighters();
    
    return Column(
      children: [
        Padding(
          padding: EdgeInsets.all(16),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  decoration: InputDecoration(
                    hintText: 'Search fighters...',
                    hintStyle: TextStyle(color: Colors.grey[400]),
                    prefixIcon: Icon(Icons.search, color: Colors.grey[400]),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: Colors.grey[600]!),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: Colors.grey[600]!),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: Colors.red),
                    ),
                    filled: true,
                    fillColor: Color(0xFF2D2D2D),
                  ),
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: ListView.builder(
            padding: EdgeInsets.symmetric(horizontal: 16),
            itemCount: allFighters.length,
            itemBuilder: (context, index) {
              final fighter = allFighters[index];
              final totalFights = fighter.record.wins + fighter.record.losses + fighter.record.draws;
              final winRate = totalFights > 0 ? (fighter.record.wins / totalFights * 100) : 0.0;
              
              return Card(
                margin: EdgeInsets.only(bottom: 8),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: Colors.red,
                    child: Text(
                      fighter.name.split(' ').last[0],
                      style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                  ),
                  title: Text(
                    fighter.name,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${fighter.record.wins}-${fighter.record.losses}-${fighter.record.draws}',
                        style: TextStyle(color: Colors.grey[400]),
                      ),
                      SizedBox(height: 4),
                      LinearProgressIndicator(
                        value: winRate / 100,
                        backgroundColor: Colors.grey[700],
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.red),
                      ),
                    ],
                  ),
                  trailing: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        '${winRate.toStringAsFixed(1)}%',
                        style: TextStyle(
                          color: Colors.red,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'Win Rate',
                        style: TextStyle(
                          color: Colors.grey[400],
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildDivisionsTab() {
    final divisions = _ufcDataService.getDivisions();
    
    return ListView.builder(
      padding: EdgeInsets.all(16),
      itemCount: divisions.length,
      itemBuilder: (context, index) {
        final division = divisions[index];
        final rankings = _ufcDataService.getRankingsForDivision(division);
        final champion = _ufcDataService.getChampionForDivision(division);
        
        // Calculate division statistics
        final fighters = rankings.map((r) => _ufcDataService.getFighterByRanking(r)).where((f) => f != null).cast<Fighter>().toList();
        final totalFights = fighters.fold<int>(0, (sum, f) => 
            sum + f.record.wins + f.record.losses + f.record.draws);
        final totalWins = fighters.fold<int>(0, (sum, f) => sum + f.record.wins);
        final winRate = totalFights > 0 ? (totalWins / totalFights * 100) : 0.0;
        
        return Card(
          margin: EdgeInsets.only(bottom: 16),
          child: Padding(
            padding: EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.category, color: Colors.red),
                    SizedBox(width: 8),
                    Text(
                      division,
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    Spacer(),
                    Container(
                      padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.red.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: Colors.red),
                      ),
                      child: Text(
                        '${rankings.length} fighters',
                        style: TextStyle(
                          color: Colors.red,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 16),
                if (champion != null) ...[
                  Container(
                    padding: EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.yellow.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.yellow.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.star, color: Colors.yellow),
                        SizedBox(width: 8),
                        Text(
                          'Champion: ${champion.fighterName}',
                          style: TextStyle(
                            color: Colors.yellow,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                  SizedBox(height: 16),
                ],
                Row(
                  children: [
                    Expanded(
                      child: _buildDivisionStat('Total Fights', totalFights.toString(), Icons.sports_mma),
                    ),
                    SizedBox(width: 12),
                    Expanded(
                      child: _buildDivisionStat('Win Rate', '${winRate.toStringAsFixed(1)}%', Icons.trending_up),
                    ),
                    SizedBox(width: 12),
                    Expanded(
                      child: _buildDivisionStat('Avg Fights', totalFights > 0 ? (totalFights / fighters.length).toStringAsFixed(1) : '0', Icons.analytics),
                    ),
                  ],
                ),
                SizedBox(height: 16),
                Text(
                  'Top 5 Ranked',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                SizedBox(height: 8),
                ...rankings.take(5).map((ranking) => ListTile(
                  dense: true,
                  leading: CircleAvatar(
                    radius: 16,
                    backgroundColor: ranking.rank == 0 ? Colors.yellow : Colors.red,
                    child: Text(
                      ranking.rank == 0 ? 'C' : ranking.rank.toString(),
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                  title: Text(
                    ranking.fighterName,
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 14,
                    ),
                  ),
                  subtitle: Text(
                    '${ranking.record.wins}-${ranking.record.losses}-${ranking.record.draws}',
                    style: TextStyle(color: Colors.grey[400], fontSize: 12),
                  ),
                )).toList(),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildDivisionStat(String label, String value, IconData icon) {
    return Container(
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Color(0xFF3D3D3D),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Icon(icon, color: Colors.red, size: 20),
          SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          Text(
            label,
            style: TextStyle(
              fontSize: 10,
              color: Colors.grey[400],
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildRecordsTab() {
    final allFighters = _ufcDataService.getAllFighters();
    
    // Sort by different criteria
    final mostWins = List<Fighter>.from(allFighters)
      ..sort((a, b) => b.record.wins.compareTo(a.record.wins));
    
    final mostLosses = List<Fighter>.from(allFighters)
      ..sort((a, b) => b.record.losses.compareTo(a.record.losses));
    
    final mostFights = List<Fighter>.from(allFighters)
      ..sort((a, b) {
        final aTotal = a.record.wins + a.record.losses + a.record.draws;
        final bTotal = b.record.wins + b.record.losses + b.record.draws;
        return bTotal.compareTo(aTotal);
      });
    
    final undefeated = allFighters.where((f) => f.record.losses == 0 && f.record.wins > 0).toList();
    final winless = allFighters.where((f) => f.record.wins == 0 && f.record.losses > 0).toList();

    return SingleChildScrollView(
      padding: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildRecordSection('Most Wins', mostWins.take(5).toList(), 'wins'),
          SizedBox(height: 24),
          _buildRecordSection('Most Fights', mostFights.take(5).toList(), 'total'),
          SizedBox(height: 24),
          _buildRecordSection('Undefeated Fighters', undefeated.take(5).toList(), 'undefeated'),
          SizedBox(height: 24),
          _buildRecordSection('Most Losses', mostLosses.take(5).toList(), 'losses'),
        ],
      ),
    );
  }

  Widget _buildRecordSection(String title, List<Fighter> fighters, String type) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  type == 'wins' ? Icons.trending_up :
                  type == 'total' ? Icons.sports_mma :
                  type == 'undefeated' ? Icons.star :
                  Icons.trending_down,
                  color: type == 'undefeated' ? Colors.yellow : Colors.red,
                ),
                SizedBox(width: 8),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
            SizedBox(height: 16),
            ...fighters.map((fighter) {
              String value;
              Color valueColor;
              
              switch (type) {
                case 'wins':
                  value = '${fighter.record.wins} wins';
                  valueColor = Colors.green;
                  break;
                case 'total':
                  final total = fighter.record.wins + fighter.record.losses + fighter.record.draws;
                  value = '$total fights';
                  valueColor = Colors.blue;
                  break;
                case 'undefeated':
                  value = '${fighter.record.wins}-0-${fighter.record.draws}';
                  valueColor = Colors.yellow;
                  break;
                case 'losses':
                  value = '${fighter.record.losses} losses';
                  valueColor = Colors.orange;
                  break;
                default:
                  value = '';
                  valueColor = Colors.white;
              }
              
              return ListTile(
                leading: CircleAvatar(
                  backgroundColor: Colors.red,
                  child: Text(
                    fighter.name.split(' ').last[0],
                    style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                ),
                title: Text(
                  fighter.name,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                subtitle: Text(
                  '${fighter.record.wins}-${fighter.record.losses}-${fighter.record.draws}',
                  style: TextStyle(color: Colors.grey[400]),
                ),
                trailing: Container(
                  padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: valueColor.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: valueColor),
                  ),
                  child: Text(
                    value,
                    style: TextStyle(
                      color: valueColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }
} 