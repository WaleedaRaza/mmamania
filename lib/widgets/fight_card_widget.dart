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
        color: const Color(0xFF121212),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withOpacity(0.06)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.35),
            blurRadius: 16,
            offset: Offset(0, 10),
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
                colors: [Colors.red.shade800, Colors.red.shade600],
              ),
              borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.sports_mma,
                  color: Colors.white,
                  size: 20,
                ),
                SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        event.title,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      SizedBox(height: 2),
                      Row(
                        children: [
                          Icon(Icons.location_on, size: 12, color: Colors.white70),
                          SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              '${event.venue} • ${event.location}',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                color: Colors.white70,
                                fontSize: 12,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    isUpcoming ? '🔜 UPCOMING' : '✅ COMPLETED',
                    style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                  ),
                )
              ],
            ),
          ),
          
          // Event Details
          Padding(
            padding: EdgeInsets.all(16),
            child: Row(
              children: [
                Text('📅', style: TextStyle(fontSize: 14)),
                SizedBox(width: 6),
                Text(
                  _formatDate(event.date),
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 14,
                  ),
                ),
                Spacer(),
                Text('🥊', style: TextStyle(fontSize: 14)),
                SizedBox(width: 6),
                Text(
                  '${fights.length} fights',
                  style: TextStyle(
                    color: Colors.white70,
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
                    color: Colors.white60,
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
                  color: Colors.white54,
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
                    borderRadius: BorderRadius.circular(10),
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
    
    // Check if we have winner and loser names (not null and not empty)
    final hasWinnerLoser = (fight.winnerName != null && fight.winnerName!.isNotEmpty) && 
                          (fight.loserName != null && fight.loserName!.isNotEmpty);
    
    return Container(
      padding: EdgeInsets.symmetric(vertical: 10, horizontal: 12),
      margin: EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withOpacity(0.06)),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: hasWinnerLoser
              ? [const Color(0xFF0F1E11), const Color(0xFF132015)] // green-ish glass for completed
              : [const Color(0xFF1A1A1A), const Color(0xFF1F1F1F)],
        ),
      ),
      child: Column(
        children: [
          if (hasWinnerLoser) ...[
            Row(
              children: [
                Expanded(
                  child: Text(
                    '🥇 ${fight.winnerName!}',
                    style: TextStyle(
                      color: Colors.greenAccent.shade200,
                      fontWeight: FontWeight.w700,
                      fontSize: 14,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.18),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    'def.',
                    style: TextStyle(
                      color: Colors.greenAccent,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Expanded(
                  child: Text(
                    fight.loserName!,
                    textAlign: TextAlign.end,
                    style: TextStyle(
                      color: Colors.redAccent.shade100,
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ] else ...[
            // Show scheduled fight format
            Row(
              children: [
                Expanded(
                  child: Text(
                    fight.getFighter1Name() ?? 'TBD',
                    style: TextStyle(
                      color: Colors.white70,
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.purple.withOpacity(0.18),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    'VS',
                    style: TextStyle(
                      color: Colors.purpleAccent,
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
                      color: Colors.white70,
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ],
          if (hasResult) ...[
            SizedBox(height: 6),
            Text(
              fight.result!,
              style: TextStyle(
                color: Colors.white60,
                fontSize: 12,
                fontStyle: FontStyle.italic,
              ),
              textAlign: TextAlign.center,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ],
      ),
    );
  }

  Color _getFighterColor(Fight fight, String? fighterId, bool isFighter1) {
    if (fight.winnerId == null) return Colors.white70;
    final isWinner = fight.winnerId == fighterId;
    return isWinner ? Colors.greenAccent.shade200 : Colors.redAccent.shade100;
  }

  String _formatDate(DateTime date) {
    return '${date.month}/${date.day}/${date.year}';
  }
} 