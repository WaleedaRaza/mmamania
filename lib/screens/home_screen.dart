import 'package:flutter/material.dart';
import '../services/ufc_data_service.dart';
import '../models/fighter.dart';
import '../models/ranking.dart';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final UFCDataService _ufcDataService = UFCDataService();

  @override
  void initState() {
    super.initState();
    _loadData();
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
        title: Text('FightHub', style: TextStyle(color: Colors.white)),
        backgroundColor: Color(0xFF2D2D2D),
        elevation: 0,
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: () async {
              await _loadData();
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildWelcomeCard(),
            SizedBox(height: 20),
            _buildTopRankings(),
            SizedBox(height: 20),
            _buildDivisionsOverview(),
          ],
        ),
      ),
    );
  }

  Widget _buildWelcomeCard() {
    return Card(
      color: Color(0xFF2D2D2D),
      child: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.sports_mma, color: Colors.red, size: 32),
                SizedBox(width: 12),
                Text(
                  'Welcome to FightHub',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
            SizedBox(height: 12),
            Text(
              'Your ultimate MMA prediction and analysis platform',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[300],
              ),
            ),
            SizedBox(height: 16),
            Row(
              children: [
                _buildStatCard('Fighters', _ufcDataService.getAllFighters().length.toString()),
                SizedBox(width: 12),
                _buildStatCard('Rankings', _ufcDataService.getAllRankings().length.toString()),
                SizedBox(width: 12),
                _buildStatCard('Divisions', _ufcDataService.getDivisions().length.toString()),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(String label, String value) {
    return Expanded(
      child: Container(
        padding: EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Color(0xFF3D3D3D),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          children: [
            Text(
              value,
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.red,
              ),
            ),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[400],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTopRankings() {
    final allRankings = _ufcDataService.getAllRankings();
    final topRankings = allRankings.where((r) => r.rank <= 5).take(5).toList();
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Top Ranked Fighters',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        SizedBox(height: 12),
        ...topRankings.map((ranking) => _buildRankingCard(ranking)).toList(),
      ],
    );
  }

  Widget _buildRankingCard(Ranking ranking) {
    return Card(
      color: Color(0xFF2D2D2D),
      margin: EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: ranking.rank == 0 ? Colors.yellow : Colors.red,
          child: Text(
            ranking.rank == 0 ? 'C' : ranking.rank.toString(),
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(
          ranking.fighterName,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        subtitle: Text(
          '${ranking.division} • ${ranking.record.wins}-${ranking.record.losses}-${ranking.record.draws}',
          style: TextStyle(color: Colors.grey[400]),
        ),
        trailing: Icon(Icons.arrow_forward_ios, color: Colors.grey[400]),
        onTap: () {
          // Navigate to fighter profile
        },
      ),
    );
  }

  Widget _buildDivisionsOverview() {
    final divisions = _ufcDataService.getDivisions();
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Divisions',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        SizedBox(height: 12),
        ...divisions.map((division) => _buildDivisionCard(division)).toList(),
      ],
    );
  }

  Widget _buildDivisionCard(String division) {
    final rankings = _ufcDataService.getRankingsForDivision(division);
    final champion = _ufcDataService.getChampionForDivision(division);
    
    return Card(
      color: Color(0xFF2D2D2D),
      margin: EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.red,
          child: Icon(Icons.sports_mma, color: Colors.white),
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
        trailing: Icon(Icons.arrow_forward_ios, color: Colors.grey[400]),
        onTap: () {
          // Navigate to division rankings
        },
      ),
    );
  }
} 