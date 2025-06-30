import 'package:flutter/material.dart';
import '../services/ufc_data_service.dart';
import '../models/fight.dart';
import '../models/event.dart';
import '../models/fighter.dart';

class FightsScreen extends StatefulWidget {
  @override
  _FightsScreenState createState() => _FightsScreenState();
}

class _FightsScreenState extends State<FightsScreen> with SingleTickerProviderStateMixin {
  final UFCDataService _ufcDataService = UFCDataService();
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Fights'),
        backgroundColor: Color(0xFF2D2D2D),
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.red,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.grey[400],
          tabs: [
            Tab(text: 'Upcoming Fights'),
            Tab(text: 'Fight Cards'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildUpcomingFightsTab(),
          _buildFightCardsTab(),
        ],
      ),
    );
  }

  Widget _buildUpcomingFightsTab() {
    return Center(
      child: Text(
        'Upcoming fights coming soon!',
        style: TextStyle(fontSize: 20, color: Colors.grey),
      ),
    );
  }

  Widget _buildFightCardsTab() {
    return Center(
      child: Text(
        'Fight cards and events coming soon!',
        style: TextStyle(fontSize: 20, color: Colors.grey),
      ),
    );
  }

  Widget _buildFightCard(Fight fight) {
    return Card(
      margin: EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.red,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    fight.weightClass,
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Spacer(),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.blue,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    fight.fightType,
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildFighterInfo(fight.fighter1, true),
                ),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 16),
                  child: Text(
                    'VS',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.red,
                    ),
                  ),
                ),
                Expanded(
                  child: _buildFighterInfo(fight.fighter2, false),
                ),
              ],
            ),
            SizedBox(height: 16),
            Row(
              children: [
                Icon(Icons.calendar_today, color: Colors.grey[400], size: 16),
                SizedBox(width: 8),
                Text(
                  fight.date.toString().split(' ')[0],
                  style: TextStyle(color: Colors.grey[400]),
                ),
                Spacer(),
                ElevatedButton(
                  onPressed: () {
                    // Navigate to fight details
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                  ),
                  child: Text('Make Prediction'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFighterInfo(Fighter fighter, bool isLeft) {
    return Column(
      children: [
        CircleAvatar(
          radius: 30,
          backgroundColor: Colors.grey[700],
          child: Text(
            fighter.name.split(' ').map((n) => n[0]).join(''),
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        SizedBox(height: 8),
        Text(
          fighter.name,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.white,
            fontSize: 14,
          ),
          textAlign: TextAlign.center,
        ),
        Text(
          fighter.recordString,
          style: TextStyle(
            color: Colors.grey[400],
            fontSize: 12,
          ),
        ),
      ],
    );
  }
} 