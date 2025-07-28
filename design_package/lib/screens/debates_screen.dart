import 'package:flutter/material.dart';
import '../models/debate_room.dart';
import 'audio_debate_room_screen.dart';

class DebatesScreen extends StatefulWidget {
  @override
  _DebatesScreenState createState() => _DebatesScreenState();
}

class _DebatesScreenState extends State<DebatesScreen> {
  final List<Map<String, dynamic>> _debates = [
    {
      'id': '1',
      'title': 'Who wins: Makhachev vs Oliveira 2?',
      'author': 'MMA_Fan_2024',
      'votes': 156,
      'comments': 23,
      'time': '2 hours ago',
      'category': 'Fight Prediction',
    },
    {
      'id': '2',
      'title': 'Is Jon Jones the GOAT?',
      'author': 'FightAnalyst',
      'votes': 89,
      'comments': 45,
      'time': '5 hours ago',
      'category': 'GOAT Debate',
    },
    {
      'id': '3',
      'title': 'Next title challenger for Lightweight?',
      'author': 'UFCInsider',
      'votes': 234,
      'comments': 67,
      'time': '1 day ago',
      'category': 'Matchmaking',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Live Debates'),
        backgroundColor: Color(0xFF2D2D2D),
        elevation: 0,
        actions: [
          IconButton(
            icon: Icon(Icons.add),
            onPressed: () {
              // Create new debate
            },
          ),
        ],
      ),
      body: Column(
        children: [
          _buildCategories(),
          Expanded(
            child: ListView.builder(
              padding: EdgeInsets.all(16),
              itemCount: _debates.length,
              itemBuilder: (context, index) {
                final debate = _debates[index];
                return _buildDebateCard(debate);
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // Create a new debate room
          final newDebateRoom = DebateRoom(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            title: 'New Live Debate',
            description: 'Start a new live audio debate',
            category: 'General',
            createdBy: 'You',
            maxParticipants: 20,
            participantCount: 1,
            isActive: true,
            status: DebateRoomStatus.active,
            type: DebateRoomType.audio,
            createdAt: DateTime.now(),
            audioSettings: {
              'maxSpeakers': 6,
              'allowListeners': true,
              'requireApproval': false,
              'recordingEnabled': false,
            },
          );
          
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => AudioDebateRoomScreen(room: newDebateRoom),
            ),
          );
        },
        backgroundColor: Colors.red,
        child: Icon(Icons.add, color: Colors.white),
      ),
    );
  }

  Widget _buildCategories() {
    final categories = ['All', 'Fight Prediction', 'GOAT Debate', 'Matchmaking', 'Analysis'];
    
    return Container(
      height: 50,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: EdgeInsets.symmetric(horizontal: 16),
        itemCount: categories.length,
        itemBuilder: (context, index) {
          final category = categories[index];
          return Container(
            margin: EdgeInsets.only(right: 8),
            child: FilterChip(
              label: Text(category),
              selected: index == 0,
              onSelected: (selected) {
                // Filter debates
              },
              backgroundColor: Color(0xFF3D3D3D),
              selectedColor: Colors.red,
              labelStyle: TextStyle(color: Colors.white),
            ),
          );
        },
      ),
    );
  }

  Widget _buildDebateCard(Map<String, dynamic> debate) {
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
                    color: Colors.blue,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    debate['category'],
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Spacer(),
                Text(
                  debate['time'],
                  style: TextStyle(
                    color: Colors.grey[400],
                    fontSize: 12,
                  ),
                ),
              ],
            ),
            SizedBox(height: 12),
            Text(
              debate['title'],
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            SizedBox(height: 8),
            Row(
              children: [
                CircleAvatar(
                  radius: 12,
                  backgroundColor: Colors.grey[700],
                  child: Text(
                    debate['author'][0].toUpperCase(),
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                SizedBox(width: 8),
                Text(
                  debate['author'],
                  style: TextStyle(
                    color: Colors.grey[400],
                    fontSize: 12,
                  ),
                ),
              ],
            ),
            SizedBox(height: 12),
            Row(
              children: [
                Icon(Icons.thumb_up, color: Colors.grey[400], size: 16),
                SizedBox(width: 4),
                Text(
                  '${debate['votes']}',
                  style: TextStyle(
                    color: Colors.grey[400],
                    fontSize: 12,
                  ),
                ),
                SizedBox(width: 16),
                Icon(Icons.comment, color: Colors.grey[400], size: 16),
                SizedBox(width: 4),
                Text(
                  '${debate['comments']}',
                  style: TextStyle(
                    color: Colors.grey[400],
                    fontSize: 12,
                  ),
                ),
                Spacer(),
                ElevatedButton(
                  onPressed: () {
                    // Create a mock debate room and navigate to audio debate
                    final debateRoom = DebateRoom(
                      id: debate['id'],
                      title: debate['title'],
                      description: 'Live audio debate about ${debate['title']}',
                      category: debate['category'],
                      createdBy: debate['author'],
                      maxParticipants: 20,
                      participantCount: 8,
                      isActive: true,
                      status: DebateRoomStatus.active,
                      type: DebateRoomType.audio,
                      createdAt: DateTime.now().subtract(const Duration(hours: 2)),
                      audioSettings: {
                        'maxSpeakers': 6,
                        'allowListeners': true,
                        'requireApproval': false,
                        'recordingEnabled': false,
                      },
                    );
                    
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (context) => AudioDebateRoomScreen(room: debateRoom),
                      ),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                    minimumSize: Size(80, 32),
                  ),
                  child: Text('Join'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
} 