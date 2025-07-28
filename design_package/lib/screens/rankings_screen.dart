import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/ufc_rankings.dart';
import '../services/firebase_service.dart';

class RankingsScreen extends StatefulWidget {
  const RankingsScreen({super.key});

  @override
  State<RankingsScreen> createState() => _RankingsScreenState();
}

class _RankingsScreenState extends State<RankingsScreen> {
  String selectedDivision = 'Men\'s Pound-for-Pound';
  List<String> divisions = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadDivisions();
  }

  Future<void> _loadDivisions() async {
    try {
      final availableDivisions = await FirebaseService.getAvailableDivisions();
      setState(() {
        divisions = availableDivisions;
        isLoading = false;
      });
    } catch (e) {
      print('Error loading divisions: $e');
      setState(() {
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('UFC Rankings'),
        backgroundColor: Colors.black,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: Column(
        children: [
          // Division Selector
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.grey[100],
            child: Row(
              children: [
                const Text(
                  'Division: ',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: DropdownButton<String>(
                    value: selectedDivision,
                    isExpanded: true,
                    items: divisions.map((division) {
                      return DropdownMenuItem<String>(
                        value: division,
                        child: Text(division),
                      );
                    }).toList(),
                    onChanged: (value) {
                      if (value != null) {
                        setState(() {
                          selectedDivision = value;
                        });
                      }
                    },
                  ),
                ),
              ],
            ),
          ),
          
          // Rankings List
          Expanded(
            child: isLoading
                ? const Center(child: CircularProgressIndicator())
                : StreamBuilder<List<UFCRanking>>(
                    stream: FirebaseService.getRankingsStream(selectedDivision),
                    builder: (context, snapshot) {
                      if (snapshot.hasError) {
                        return Center(
                          child: Text('Error: ${snapshot.error}'),
                        );
                      }

                      if (snapshot.connectionState == ConnectionState.waiting) {
                        return const Center(child: CircularProgressIndicator());
                      }

                      final rankings = snapshot.data ?? [];

                      if (rankings.isEmpty) {
                        return const Center(
                          child: Text('No rankings available'),
                        );
                      }

                      return ListView.builder(
                        itemCount: rankings.length,
                        itemBuilder: (context, index) {
                          final ranking = rankings[index];
                          return _buildRankingCard(ranking, index + 1);
                        },
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildRankingCard(UFCRanking ranking, int displayRank) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getRankColor(displayRank),
          child: Text(
            displayRank.toString(),
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(
          ranking.name,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        subtitle: Text(
          ranking.record ?? 'Record not available',
          style: TextStyle(
            color: Colors.grey[600],
          ),
        ),
        trailing: IconButton(
          icon: const Icon(Icons.info_outline),
          onPressed: () {
            _showFighterDetails(ranking);
          },
        ),
      ),
    );
  }

  Color _getRankColor(int rank) {
    if (rank == 1) return Colors.amber;
    if (rank == 2) return Colors.grey[400]!;
    if (rank == 3) return Colors.brown[300]!;
    return Colors.blue;
  }

  void _showFighterDetails(UFCRanking ranking) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(ranking.name),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Division: ${ranking.division}'),
            Text('Rank: ${ranking.rank}'),
            if (ranking.record != null) Text('Record: ${ranking.record}'),
            const SizedBox(height: 8),
            Text(
              'Last Updated: ${_formatDate(ranking.lastUpdated)}',
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 12,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
} 