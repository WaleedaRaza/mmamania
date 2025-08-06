import 'package:flutter/material.dart';
import '../models/fight.dart';
import '../models/event.dart';

class FightCardWidget extends StatelessWidget {
  final Event event;
  final List<Fight> fights;
  final VoidCallback? onTap;

  const FightCardWidget({
    Key? key,
    required this.event,
    required this.fights,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isUpcoming = event.date.isAfter(DateTime.now());
    final hasFights = fights.isNotEmpty;

    return Container(
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
                  Icons.sports_mma,
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
                  '${fights.length} fights',
                  style: TextStyle(
                    color: Colors.grey.shade700,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
          
          // Fight List
          if (hasFights) ...[
            Container(
              padding: EdgeInsets.symmetric(horizontal: 16),
              child: Column(
                children: fights.take(5).map((fight) => _buildFightRow(fight)).toList(),
              ),
            ),
            if (fights.length > 5)
              Padding(
                padding: EdgeInsets.all(16),
                child: Text(
                  '+${fights.length - 5} more fights',
                  style: TextStyle(
                    color: Colors.grey.shade600,
                    fontSize: 12,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ),
          ] else ...[
            Container(
              padding: EdgeInsets.all(16),
              child: Text(
                'No fights available',
                style: TextStyle(
                  color: Colors.grey.shade500,
                  fontSize: 14,
                  fontStyle: FontStyle.italic,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ],
          
          // Action Button
          Container(
            padding: EdgeInsets.all(16),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: onTap,
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
    );
  }

  Widget _buildFightRow(Fight fight) {
    print('🎯 _buildFightRow called for fight: ${fight.id}');
    final hasResult = fight.result != null && fight.result!.isNotEmpty;
    final hasWinner = fight.winnerId != null;
    final isCompleted = hasResult || hasWinner;
    
    return Container(
      padding: EdgeInsets.symmetric(vertical: 8, horizontal: 12),
      margin: EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  fight.getFighter1Name() ?? 'TBD',
                  style: TextStyle(
                    color: _getFighterColor(fight, fight.fighter1Id, true),
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                  ),
                ),
              ),
              Container(
                padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: isCompleted ? Colors.grey.shade200 : Colors.blue.shade100,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  isCompleted ? 'COMPLETED' : 'VS',
                  style: TextStyle(
                    color: isCompleted ? Colors.grey.shade700 : Colors.blue.shade700,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Expanded(
                child: Text(
                  fight.getFighter2Name() ?? 'TBD',
                  textAlign: TextAlign.end,
                  style: TextStyle(
                    color: _getFighterColor(fight, fight.fighter2Id, false),
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                  ),
                ),
              ),
            ],
          ),
          if (hasResult) ...[
            SizedBox(height: 4),
            Text(
              fight.result!,
              style: TextStyle(
                color: Colors.grey.shade600,
                fontSize: 12,
                fontStyle: FontStyle.italic,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ],
      ),
    );
  }

  Color _getFighterColor(Fight fight, String? fighterId, bool isFighter1) {
    if (fight.winnerId == null) return Colors.grey.shade700;
    
    final isWinner = fight.winnerId == fighterId;
    return isWinner ? Colors.green.shade700 : Colors.red.shade700;
  }

  String _formatDate(DateTime date) {
    return '${date.month}/${date.day}/${date.year}';
  }
} 